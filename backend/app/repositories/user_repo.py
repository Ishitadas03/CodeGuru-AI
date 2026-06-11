from typing import Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.user import User
from app.models.profile import Profile
from app.schemas.user import UpdateProfileRequest


class UserRepository(BaseRepository[User]):
    """Repository managing User and Profile database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by email with profile loaded eagerly."""
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.profile))
        )
        return result.scalars().first()

    async def get_user_with_profile(self, user_id: Any) -> Optional[User]:
        """Fetch user by ID with profile loaded eagerly."""
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.profile))
        )
        return result.scalars().first()

    async def create_user(self, *, email: str, hashed_password: str) -> User:
        """Create user and associate a blank profile in a single transaction."""
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.flush()  # Generate user.id

        profile = Profile(user_id=user.id, skills=[])
        self.db.add(profile)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        # Reload to populate profile relationship
        return await self.get_user_with_profile(user.id)

    async def update_profile(self, *, user: User, profile_in: UpdateProfileRequest) -> Profile:
        """Update user's profile metadata."""
        profile = user.profile
        if not profile:
            profile = Profile(user_id=user.id)
            self.db.add(profile)
            await self.db.flush()

        update_data = profile_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
