# backend/app/core/dependencies.py
"""FastAPI dependency injection for authentication, authorization, and rate limiting.

All route handlers use these dependencies to enforce:
- JWT authentication with user resolution
- Role-based access control (admin check)
- Subscription tier verification for feature gating
- Database session lifecycle management
"""
from __future__ import annotations

import uuid
import logging
from typing import AsyncGenerator

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import SubscriptionTier, settings
from app.core.exceptions import AuthError, ForbiddenError, QuotaExceededError, SubscriptionRequiredError
from app.core.security import verify_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository

logger = logging.getLogger("codeguru.dependencies")

# Redis is optional — required only for quota tracking in production.
# On Vercel, use Upstash Redis or disable quotas.
try:
    import redis.asyncio as aioredis
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False
    aioredis = None  # type: ignore[assignment]

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
)


async def get_redis() -> AsyncGenerator:
    """Provide a Redis connection if configured, otherwise yield None.

    Gracefully degrades when Redis is unavailable (e.g. on Vercel without Upstash).
    """
    if not _REDIS_AVAILABLE or not settings.REDIS_URL:
        logger.debug("Redis not configured — returning None")
        yield None
        return

    client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.aclose()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate the JWT bearer token and resolve the current active user.

    Raises AuthError if the token is invalid, expired, or the user is
    not found / inactive.
    """
    user_id_str = verify_token(token, expected_type="access")
    if not user_id_str:
        raise AuthError("Could not validate credentials or token expired.")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthError("Invalid token format for user ID.")

    repo = UserRepository(db)
    user = await repo.get_user_with_profile(user_uuid)
    if not user:
        raise AuthError("User not found.")

    if not user.is_active:
        raise AuthError("Inactive user account.")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the resolved user has an active account.

    This is a convenience dependency that adds an explicit active check
    on top of get_current_user (which already checks is_active).
    """
    if not current_user.is_active:
        raise AuthError("Inactive user account.")
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify the current user has superuser (admin) privileges.

    Raises ForbiddenError if the user is not a superuser.
    """
    if not current_user.is_superuser:
        raise ForbiddenError("Admin privileges required.")
    return current_user


def require_subscription(
    *allowed_tiers: SubscriptionTier,
) -> "SubscriptionChecker":
    """Create a dependency that enforces subscription tier requirements.

    Usage in routes:
        @router.get("/feature", dependencies=[Depends(require_subscription(SubscriptionTier.PRO))])

    Or as a parameter dependency:
        user: User = Depends(require_subscription(SubscriptionTier.PRO, SubscriptionTier.TEAM))
    """
    return SubscriptionChecker(allowed_tiers=list(allowed_tiers))


class SubscriptionChecker:
    """Callable dependency that verifies the user's subscription tier."""

    def __init__(self, allowed_tiers: list[SubscriptionTier]) -> None:
        self.allowed_tiers = allowed_tiers

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_tier = SubscriptionTier(getattr(current_user, "subscription_tier", "free"))

        if user_tier not in self.allowed_tiers:
            tier_names = ", ".join(t.value for t in self.allowed_tiers)
            raise SubscriptionRequiredError(
                detail=f"This feature requires one of: {tier_names} subscription.",
                required_tier=self.allowed_tiers[0].value if self.allowed_tiers else "pro",
            )

        return current_user


async def check_usage_quota(
    feature: str,
    current_user: User = Depends(get_current_user),
    redis_client=None,
) -> User:
    """Check if the user has remaining quota for a specific feature.

    Uses Redis counters to track monthly usage. The counter key format is:
    usage:{user_id}:{feature}:{year}:{month}

    Raises QuotaExceededError if the limit is reached.
    """
    if redis_client is None:
        return current_user  # No Redis — skip quota check
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)
    user_tier = SubscriptionTier(getattr(current_user, "subscription_tier", "free"))

    # Determine the monthly limit for this feature + tier
    limits_map: dict[str, dict[SubscriptionTier, int]] = {
        "code_review": {
            SubscriptionTier.FREE: settings.TIER_FREE_CODE_REVIEWS_MONTHLY,
            SubscriptionTier.PRO: settings.TIER_PRO_CODE_REVIEWS_MONTHLY,
            SubscriptionTier.TEAM: settings.TIER_PRO_CODE_REVIEWS_MONTHLY,
        },
        "dsa_session": {
            SubscriptionTier.FREE: settings.TIER_FREE_DSA_SESSIONS_MONTHLY,
            SubscriptionTier.PRO: settings.TIER_PRO_DSA_SESSIONS_MONTHLY,
            SubscriptionTier.TEAM: settings.TIER_PRO_DSA_SESSIONS_MONTHLY,
        },
        "interview": {
            SubscriptionTier.FREE: settings.TIER_FREE_INTERVIEW_MONTHLY,
            SubscriptionTier.PRO: settings.TIER_PRO_INTERVIEW_MONTHLY,
            SubscriptionTier.TEAM: settings.TIER_PRO_INTERVIEW_MONTHLY,
        },
        "rag_query": {
            SubscriptionTier.FREE: settings.TIER_FREE_RAG_QUERIES_MONTHLY,
            SubscriptionTier.PRO: settings.TIER_PRO_RAG_QUERIES_MONTHLY,
            SubscriptionTier.TEAM: settings.TIER_PRO_RAG_QUERIES_MONTHLY,
        },
    }

    tier_limits = limits_map.get(feature)
    if tier_limits is None:
        return current_user  # Unknown feature, allow by default

    monthly_limit = tier_limits.get(user_tier, 0)
    if monthly_limit == -1:
        return current_user  # Unlimited

    counter_key = f"usage:{current_user.id}:{feature}:{now.year}:{now.month}"

    try:
        current_count_raw = await redis_client.get(counter_key)
        current_count = int(current_count_raw) if current_count_raw is not None else 0
    except Exception:
        # If Redis is unavailable, allow the request but log the issue
        logger.warning(
            "Redis unavailable for quota check, allowing request for user=%s feature=%s",
            current_user.id,
            feature,
        )
        return current_user

    if current_count >= monthly_limit:
        raise QuotaExceededError(
            detail=(
                f"You have used {current_count}/{monthly_limit} {feature.replace('_', ' ')} "
                f"requests this month. Upgrade to Pro for higher limits."
            )
        )

    return current_user


async def increment_usage(
    user_id: uuid.UUID,
    feature: str,
    redis_client,
) -> int:
    """Increment the usage counter for a user+feature and return the new count.

    Sets a TTL of 35 days on the counter key to auto-expire after the billing period.
    """
    if redis_client is None:
        return 0  # No Redis — skip increment

    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)
    counter_key = f"usage:{user_id}:{feature}:{now.year}:{now.month}"

    try:
        pipe = redis_client.pipeline()
        pipe.incr(counter_key)
        pipe.expire(counter_key, 35 * 24 * 3600)  # 35 days TTL
        results = await pipe.execute()
        return int(results[0])
    except Exception:
        logger.warning(
            "Redis unavailable for usage increment, user=%s feature=%s",
            user_id,
            feature,
        )
        return 0
