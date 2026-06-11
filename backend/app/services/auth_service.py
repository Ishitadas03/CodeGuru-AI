from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, verify_token
from app.core.exceptions import AuthError, ValidationError
from app.core.config import settings
from app.models.user import User
from app.models.session import RefreshToken
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse
import httpx


class AuthService:
    """Service orchestrating registration, login, JWT token rotation, and Google OAuth."""

    async def register(self, db: AsyncSession, email: str, password: str) -> User:
        """Register a new user, ensuring email uniqueness."""
        repo = UserRepository(db)
        existing_user = await repo.get_by_email(email)
        if existing_user:
            raise ValidationError("Email already registered.")
            
        hashed_password = get_password_hash(password)
        user = await repo.create_user(email=email, hashed_password=hashed_password)
        return user

    async def login(self, db: AsyncSession, email: str, password: str) -> TokenResponse:
        """Authenticate user credentials and return access and refresh tokens."""
        repo = UserRepository(db)
        user = await repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthError("Incorrect email or password.")
            
        if not user.is_active:
            raise AuthError("User account is inactive.")

        return await self._generate_session_tokens(db, user)

    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> TokenResponse:
        """Validate an active refresh token, revoke it, and return a new token pair."""
        subject = verify_token(refresh_token, expected_type="refresh")
        if not subject:
            raise AuthError("Invalid or expired refresh token.")

        # Check in DB to verify it hasn't been revoked
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        db_token = result.scalars().first()
        if not db_token:
            raise AuthError("Refresh token is invalid, revoked, or expired.")

        # Revoke the old token
        db_token.is_revoked = True
        db.add(db_token)
        await db.flush()

        repo = UserRepository(db)
        user = await repo.get(db_token.user_id)
        if not user or not user.is_active:
            raise AuthError("User account is no longer active.")

        # Generate new tokens
        tokens = await self._generate_session_tokens(db, user)
        await db.commit()
        return tokens

    async def revoke_tokens(self, db: AsyncSession, refresh_token: str) -> None:
        """Revoke a refresh token on logout."""
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        db_token = result.scalars().first()
        if db_token:
            db_token.is_revoked = True
            db.add(db_token)
            await db.commit()

    async def google_oauth(self, db: AsyncSession, oauth_token: str) -> TokenResponse:
        """Authenticate user via Google OAuth, auto-registering new users."""
        email = None
        # Support development bypass/mock
        if oauth_token.startswith("mock_google_token_"):
            email = oauth_token.replace("mock_google_token_", "") + "@example.com"
        else:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://www.googleapis.com/oauth2/v3/userinfo",
                        headers={"Authorization": f"Bearer {oauth_token}"},
                        timeout=5.0
                    )
                    if response.status_code == 200:
                        email = response.json().get("email")
            except Exception as e:
                raise AuthError(f"Google OAuth connection failed: {str(e)}")

        if not email:
            raise AuthError("Failed to retrieve user email from Google OAuth.")

        repo = UserRepository(db)
        user = await repo.get_by_email(email)
        if not user:
            # Auto-register Google OAuth user with random password
            import secrets
            random_pw = secrets.token_hex(16)
            hashed_password = get_password_hash(random_pw)
            user = await repo.create_user(email=email, hashed_password=hashed_password)

        if not user.is_active:
            raise AuthError("User account is inactive.")

        return await self._generate_session_tokens(db, user)

    async def _generate_session_tokens(self, db: AsyncSession, user: User) -> TokenResponse:
        """Helper to generate JWT tokens and store refresh token in database."""
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        db_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at
        )
        db.add(db_token)
        await db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
