"""
Authentication Integration Tests Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
import pytest
from fastapi import status
from httpx import AsyncClient

from core.database.models import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, test_tenant: User):
    """Test user registration."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newuser123",
            "first_name": "New",
            "last_name": "User"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    """Test registration with duplicate email."""
    response = await client.post(
        "/auth/register",
        json={
            "email": test_user.email,
            "password": "newuser123",
            "first_name": "New",
            "last_name": "User"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login."""
    response = await client.post(
        "/auth/token",
        data={
            "username": test_user.email,
            "password": "user123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["expires_in"], int)


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post(
        "/auth/token",
        data={
            "username": "invalid@example.com",
            "password": "wrongpass"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user: User):
    """Test token refresh."""
    # First login to get tokens
    login_response = await client.post(
        "/auth/token",
        data={
            "username": test_user.email,
            "password": "user123"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token to get new access token
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Test refresh with invalid token."""
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, user_token: str):
    """Test user logout."""
    response = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Successfully logged out"
    
    # Try to use the token after logout
    response = await client.get(
        "/tenants",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, user_token: str):
    """Test password change."""
    response = await client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "old_password": "user123",
            "new_password": "newpass123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Password successfully changed"
    
    # Try to login with new password
    response = await client.post(
        "/auth/token",
        data={
            "username": "user@example.com",
            "password": "newpass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_change_password_invalid_old(client: AsyncClient, user_token: str):
    """Test password change with invalid old password."""
    response = await client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "old_password": "wrongpass",
            "new_password": "newpass123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Incorrect password"
