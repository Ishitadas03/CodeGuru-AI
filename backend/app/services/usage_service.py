import logging
import uuid
import datetime
import tiktoken
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.models.usage import AIUsageRecord
from app.core.config import SubscriptionTier, settings
from app.core.exceptions import QuotaExceededError

logger = logging.getLogger("codeguru.usage_service")
slack_logger = logging.getLogger("codeguru.slack")

# Rates per 1K tokens
MODEL_RATES = {
    "gemini-2.0-flash": {"input": 0.000075 / 1000, "output": 0.0003 / 1000},
    "gemini-2.5-pro": {"input": 0.00125 / 1000, "output": 0.005 / 1000},
    "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
    "codellama": {"input": 0.0, "output": 0.0},
    "default": {"input": 0.000075 / 1000, "output": 0.0003 / 1000}
}


class UsageService:
    """Manages AI token budgets, limits, platform cost circuit breakers, and cost reporting."""

    def __init__(self) -> None:
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.encoding = None

    def count_tokens(self, text: str) -> int:
        """Estimate token count for a text block using tiktoken."""
        if not text:
            return 0
        if self.encoding:
            return len(self.encoding.encode(text, disallowed_special=()))
        # Fallback to simple whitespace estimator if tiktoken fails
        return len(text.split())

    def _get_model_rates(self, model: str) -> dict[str, float]:
        """Resolve cost rates for the target model."""
        for name, rates in MODEL_RATES.items():
            if name in model.lower():
                return rates
        return MODEL_RATES["default"]

    async def get_user_daily_tokens(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        redis_client: Optional[Redis] = None
    ) -> tuple[int, int]:
        """Fetch user's input/output tokens used today from Redis or SQL database."""
        today_start = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if redis_client:
            try:
                input_key = f"usage:{user_id}:daily_input"
                output_key = f"usage:{user_id}:daily_output"
                in_val = await redis_client.get(input_key)
                out_val = await redis_client.get(output_key)
                if in_val is not None and out_val is not None:
                    return int(in_val), int(out_val)
            except Exception as e:
                logger.warning(f"Failed to read user daily tokens from Redis: {str(e)}")

        # DB Fallback
        stmt = select(
            func.sum(AIUsageRecord.input_tokens),
            func.sum(AIUsageRecord.output_tokens)
        ).where(
            AIUsageRecord.user_id == user_id,
            AIUsageRecord.created_at >= today_start
        )
        res = await db.execute(stmt)
        row = res.fetchone()
        in_sum = (row[0] if row and row[0] is not None else 0)
        out_sum = (row[1] if row and row[1] is not None else 0)

        # Cache back to Redis if client is available
        if redis_client:
            try:
                input_key = f"usage:{user_id}:daily_input"
                output_key = f"usage:{user_id}:daily_output"
                # Set expire to end of day
                seconds_to_midnight = int((today_start + datetime.timedelta(days=1) - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
                await redis_client.setex(input_key, max(1, seconds_to_midnight), in_sum)
                await redis_client.setex(output_key, max(1, seconds_to_midnight), out_sum)
            except Exception:
                pass

        return in_sum, out_sum

    async def get_platform_daily_cost(
        self,
        db: AsyncSession,
        redis_client: Optional[Redis] = None
    ) -> float:
        """Fetch cumulative estimated platform cost today."""
        today_start = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if redis_client:
            try:
                cost_key = "platform:daily_cost"
                val = await redis_client.get(cost_key)
                if val is not None:
                    return float(val)
            except Exception as e:
                logger.warning(f"Failed to read platform daily cost from Redis: {str(e)}")

        # DB Fallback
        stmt = select(func.sum(AIUsageRecord.estimated_cost)).where(
            AIUsageRecord.created_at >= today_start
        )
        res = await db.execute(stmt)
        cost_sum = res.scalar() or 0.0

        # Cache back to Redis
        if redis_client:
            try:
                cost_key = "platform:daily_cost"
                seconds_to_midnight = int((today_start + datetime.timedelta(days=1) - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
                await redis_client.setex(cost_key, max(1, seconds_to_midnight), str(cost_sum))
            except Exception:
                pass

        return cost_sum

    async def verify_budgets(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        tier: SubscriptionTier,
        estimated_input_tokens: int,
        redis_client: Optional[Redis] = None
    ) -> None:
        """Pre-check budget limits for user and platform circuit breaker before executing LLM request."""
        # 1. Platform Circuit Breaker
        platform_cost = await self.get_platform_daily_cost(db, redis_client)
        if platform_cost >= 200.0:
            slack_logger.critical(
                "CRITICAL: Platform daily budget exceeded! Cost = $%.2f / Limit = $200. Pausing non-pro AI features.",
                platform_cost
            )
            # Gate limit: non-Pro tiers are paused when platform limit is reached
            if tier != SubscriptionTier.PRO and tier != SubscriptionTier.TEAM:
                raise QuotaExceededError(
                    detail="The AI service is temporarily suspended due to daily system maintenance. Please try again later."
                )

        # 2. User Daily Quota
        limits = {
            SubscriptionTier.FREE: {"input": 50000, "output": 10000},
            SubscriptionTier.PRO: {"input": 500000, "output": 100000},
            SubscriptionTier.TEAM: {"input": 1000000, "output": 200000}
        }
        user_limits = limits.get(tier, limits[SubscriptionTier.FREE])

        user_in, user_out = await self.get_user_daily_tokens(db, user_id, redis_client)

        if user_in + estimated_input_tokens > user_limits["input"]:
            raise QuotaExceededError(
                detail=(
                    f"Daily input token limit exceeded. "
                    f"Used: {user_in}/{user_limits['input']} tokens. "
                    "Upgrade to Pro/Team for higher limits."
                )
            )

    async def record_usage(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        model: str,
        input_tokens: int,
        output_tokens: int,
        redis_client: Optional[Redis] = None
    ) -> AIUsageRecord:
        """Save usage log to SQL and increment caches."""
        rates = self._get_model_rates(model)
        cost = (input_tokens * rates["input"]) + (output_tokens * rates["output"])

        # Insert DB record
        record = AIUsageRecord(
            user_id=user_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=cost
        )
        db.add(record)
        await db.flush()

        # Update cache counts if Redis client is available
        if redis_client:
            try:
                today_start = datetime.datetime.now(datetime.timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                seconds_to_midnight = int((today_start + datetime.timedelta(days=1) - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
                seconds_to_midnight = max(1, seconds_to_midnight)

                input_key = f"usage:{user_id}:daily_input"
                output_key = f"usage:{user_id}:daily_output"
                cost_key = "platform:daily_cost"

                # Check and increment or set
                pipe = redis_client.pipeline()
                pipe.incrby(input_key, input_tokens)
                pipe.expire(input_key, seconds_to_midnight)
                pipe.incrby(output_key, output_tokens)
                pipe.expire(output_key, seconds_to_midnight)
                
                # Redis floats are formatted as strings
                pipe.incrbyfloat(cost_key, cost)
                pipe.expire(cost_key, seconds_to_midnight)
                await pipe.execute()
            except Exception as e:
                logger.warning(f"Failed to increment daily usage counters in Redis: {str(e)}")

        return record
