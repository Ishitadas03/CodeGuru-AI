from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user account."""
    user = await auth_service.register(db, data.email, data.password)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Login with email and password to receive access and refresh tokens."""
    tokens = await auth_service.login(db, data.email, data.password)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Rotate an active refresh token for a new token pair."""
    tokens = await auth_service.refresh_token(db, data.refresh_token)
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
) -> Response:
    """Revoke a refresh token to logout user."""
    await auth_service.revoke_tokens(db, data.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    token_data: RefreshRequest,  # We can re-use RefreshRequest here which has a single string token, or create a GoogleLoginRequest.
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Authenticate or register a user using their Google OAuth access token."""
    tokens = await auth_service.google_oauth(db, token_data.refresh_token)
    return tokens
