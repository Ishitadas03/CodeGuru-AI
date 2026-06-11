from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserResponse, ProfileResponse, UpdateProfileRequest
from app.repositories.user_repo import UserRepository

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Fetch current user account and profile details."""
    return current_user


@router.put("/me/profile", response_model=ProfileResponse)
async def update_user_profile(
    profile_in: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    """Update current user profile info."""
    repo = UserRepository(db)
    profile = await repo.update_profile(user=current_user, profile_in=profile_in)
    return profile
