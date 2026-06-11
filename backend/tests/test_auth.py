import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    """Verify that a user can register successfully."""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient) -> None:
    """Verify that registering with an existing email returns 422."""
    payload = {"email": "duplicate@example.com", "password": "securepassword123"}
    # First signup
    await client.post(f"{settings.API_V1_STR}/auth/register", json=payload)
    # Duplicate signup
    response = await client.post(f"{settings.API_V1_STR}/auth/register", json=payload)
    assert response.status_code == 422
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """Verify that a user can login and receive JWT tokens."""
    # Register user
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "login@example.com", "password": "securepassword123"}
    )
    # Login
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "login@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient) -> None:
    """Verify that login fails with incorrect credentials."""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_me_protected(client: AsyncClient) -> None:
    """Verify that the protected /me endpoint requires authentication."""
    # 1. Access without token should fail
    response = await client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401

    # 2. Access with valid token should succeed
    email = "me@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "securepassword123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "securepassword123"}
    )
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == email


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient) -> None:
    """Verify token refresh rotation flow."""
    email = "refresh@example.com"
    await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": "securepassword123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "securepassword123"}
    )
    refresh_token = login_res.json()["refresh_token"]

    # Refresh
    response = await client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    # Try using the old refresh token again - should fail as it was rotated
    fail_response = await client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert fail_response.status_code == 401
