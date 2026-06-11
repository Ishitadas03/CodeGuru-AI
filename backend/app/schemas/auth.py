from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for user registration requests."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters long.")


class LoginRequest(BaseModel):
    """Schema for user login requests."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for successful authentication token responses."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Schema for token refresh requests."""
    refresh_token: str
