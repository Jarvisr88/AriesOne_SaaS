"""
Integration tests for security features.
"""
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest_asyncio

from ability.security.auth import SecurityService
from ability.config import Settings


@pytest.fixture
def test_settings():
    """Test settings fixture."""
    return Settings(
        secret_key="test-secret-key",
        algorithm="HS256",
        api_key="test-api-key",
        test_mode=True
    )

@pytest_asyncio.fixture
async def test_client():
    """Test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def security_service(test_settings):
    """Security service fixture."""
    return SecurityService(test_settings)

@pytest.mark.asyncio
async def test_jwt_authentication(test_client, security_service):
    """Test JWT authentication."""
    # Create test user and token
    test_user = {
        "username": "testuser",
        "scopes": ["eligibility:read"]
    }
    token = security_service.create_access_token(test_user)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get(
        "/api/v1/eligibility/status",
        headers=headers
    )
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_invalid_jwt(test_client):
    """Test invalid JWT handling."""
    headers = {"Authorization": "Bearer invalid-token"}
    response = await test_client.get(
        "/api/v1/eligibility/status",
        headers=headers
    )
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_api_key_authentication(test_client, test_settings):
    """Test API key authentication."""
    headers = {"X-API-Key": test_settings.api_key}
    response = await test_client.get(
        "/api/v1/eligibility/status",
        headers=headers
    )
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_invalid_api_key(test_client):
    """Test invalid API key handling."""
    headers = {"X-API-Key": "invalid-key"}
    response = await test_client.get(
        "/api/v1/eligibility/status",
        headers=headers
    )
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_missing_authentication(test_client):
    """Test missing authentication handling."""
    response = await test_client.get("/api/v1/eligibility/status")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_permission_check(test_client, security_service):
    """Test permission checking."""
    # Create test user with limited permissions
    test_user = {
        "username": "testuser",
        "scopes": ["eligibility:read"]
    }
    token = security_service.create_access_token(test_user)
    
    # Test allowed endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get(
        "/api/v1/eligibility/status",
        headers=headers
    )
    assert response.status_code == 200
    
    # Test restricted endpoint
    response = await test_client.post(
        "/api/v1/eligibility/submit",
        headers=headers,
        json={"test": "data"}
    )
    assert response.status_code == 403
