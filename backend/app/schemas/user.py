import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileResponse(BaseModel):
    """Schema for profile representation in responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = Field(default_factory=list)


class UserResponse(BaseModel):
    """Schema for user representation in responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    subscription_tier: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    profile: Optional[ProfileResponse] = None


class UpdateProfileRequest(BaseModel):
    """Schema for updating a user's profile metadata."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=1000)
    skills: Optional[List[str]] = Field(None, description="List of programming skills/languages.")
