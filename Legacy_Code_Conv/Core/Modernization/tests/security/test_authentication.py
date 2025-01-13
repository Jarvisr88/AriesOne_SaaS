"""
Authentication Security Tests Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import User
from core.utils.security import create_access_token


@pytest.mark.asyncio
async def test_password_complexity(client: AsyncClient):
    """Test password complexity requirements."""
    weak_passwords = [
        "short",  # Too short
        "onlylowercase",  # No uppercase/numbers/symbols
        "ONLYUPPERCASE",  # No lowercase/numbers/symbols
        "12345678",  # Only numbers
        "password123",  # Common password
    ]
    
    for password in weak_passwords:
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": password,
                "first_name": "Test",
                "last_name": "User"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_brute_force_protection(client: AsyncClient, test_user: User):
    """Test protection against brute force attacks."""
    # Attempt multiple failed logins
    for _ in range(5):
        response = await client.post(
            "/auth/token",
            data={
                "username": test_user.email,
                "password": "wrongpass"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Next attempt should trigger rate limiting
    response = await client.post(
        "/auth/token",
        data={
            "username": test_user.email,
            "password": "wrongpass"
        }
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_token_expiration(client: AsyncClient, test_user: User):
    """Test token expiration."""
    # Create expired token
    expired_token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=-3600  # Expired 1 hour ago
    )
    
    response = await client.get(
        "/tenants",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "token has expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_session_fixation(
    client: AsyncClient,
    test_user: User,
    user_token: str
):
    """Test protection against session fixation."""
    # Get initial token
    initial_token = user_token
    
    # Change password
    response = await client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {initial_token}"},
        json={
            "old_password": "user123",
            "new_password": "newpass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Try to use old token
    response = await client.get(
        "/tenants",
        headers={"Authorization": f"Bearer {initial_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_csrf_protection(client: AsyncClient, user_token: str):
    """Test CSRF protection."""
    # Try request without CSRF token
    response = await client.post(
        "/auth/change-password",
        headers={
            "Authorization": f"Bearer {user_token}",
            "Origin": "http://malicious-site.com"
        },
        json={
            "old_password": "user123",
            "new_password": "newpass123"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_secure_headers(client: AsyncClient):
    """Test secure response headers."""
    response = await client.get("/")
    headers = response.headers
    
    # Check security headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Content-Security-Policy" in headers
    assert "Strict-Transport-Security" in headers


@pytest.mark.asyncio
async def test_sql_injection(client: AsyncClient):
    """Test protection against SQL injection."""
    malicious_inputs = [
        "' OR '1'='1",
        "; DROP TABLE users;",
        "' UNION SELECT * FROM users--",
    ]
    
    for input_str in malicious_inputs:
        response = await client.post(
            "/auth/register",
            json={
                "email": f"test{input_str}@example.com",
                "password": "Test123!",
                "first_name": f"Test{input_str}",
                "last_name": "User"
            }
        )
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]


@pytest.mark.asyncio
async def test_xss_protection(client: AsyncClient, user_token: str):
    """Test protection against XSS attacks."""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        '<img src="x" onerror="alert(\'xss\')">'
    ]
    
    for payload in xss_payloads:
        response = await client.post(
            "/tenants",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": payload,
                "slug": "test-tenant",
                "description": payload
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_password_reset_token_security(
    client: AsyncClient,
    test_user: User
):
    """Test password reset token security."""
    # Request password reset
    response = await client.post(
        "/auth/forgot-password",
        json={"email": test_user.email}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Try to reset with invalid token
    response = await client.post(
        "/auth/reset-password",
        json={
            "token": "invalid_token",
            "new_password": "NewPass123!"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_sensitive_data_exposure(
    client: AsyncClient,
    user_token: str,
    test_user: User
):
    """Test protection against sensitive data exposure."""
    # Get user profile
    response = await client.get(
        f"/users/{test_user.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify sensitive data is not exposed
    assert "password" not in data
    assert "hashed_password" not in data
    assert "security_question" not in data
    assert "security_answer" not in data
