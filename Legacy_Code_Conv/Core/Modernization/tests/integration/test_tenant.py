"""
Tenant Integration Tests Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
import pytest
from fastapi import status
from httpx import AsyncClient

from core.database.models import Tenant


@pytest.mark.asyncio
async def test_create_tenant(client: AsyncClient, superuser_token: str):
    """Test tenant creation."""
    response = await client.post(
        "/tenants",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={
            "name": "New Tenant",
            "slug": "new-tenant",
            "description": "Test tenant",
            "subscription_plan": "premium"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Tenant"
    assert data["slug"] == "new-tenant"
    assert data["subscription_plan"] == "premium"


@pytest.mark.asyncio
async def test_create_tenant_duplicate_slug(
    client: AsyncClient,
    superuser_token: str,
    test_tenant: Tenant
):
    """Test tenant creation with duplicate slug."""
    response = await client.post(
        "/tenants",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={
            "name": "Another Tenant",
            "slug": test_tenant.slug,
            "description": "Test tenant"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Tenant with this slug already exists"


@pytest.mark.asyncio
async def test_create_tenant_unauthorized(client: AsyncClient, user_token: str):
    """Test tenant creation by non-superuser."""
    response = await client.post(
        "/tenants",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "New Tenant",
            "slug": "new-tenant",
            "description": "Test tenant"
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_list_tenants(
    client: AsyncClient,
    superuser_token: str,
    test_tenant: Tenant
):
    """Test tenant listing."""
    response = await client.get(
        "/tenants",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(t["id"] == str(test_tenant.id) for t in data)


@pytest.mark.asyncio
async def test_list_tenants_filtered(
    client: AsyncClient,
    user_token: str,
    test_tenant: Tenant
):
    """Test tenant listing filtered by user's tenant."""
    response = await client.get(
        "/tenants",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(test_tenant.id)


@pytest.mark.asyncio
async def test_get_tenant(
    client: AsyncClient,
    superuser_token: str,
    test_tenant: Tenant
):
    """Test getting tenant by ID."""
    response = await client.get(
        f"/tenants/{test_tenant.id}",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_tenant.id)
    assert data["name"] == test_tenant.name
    assert data["slug"] == test_tenant.slug


@pytest.mark.asyncio
async def test_get_tenant_not_found(client: AsyncClient, superuser_token: str):
    """Test getting non-existent tenant."""
    response = await client.get(
        "/tenants/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_tenant(
    client: AsyncClient,
    superuser_token: str,
    test_tenant: Tenant
):
    """Test tenant update."""
    response = await client.put(
        f"/tenants/{test_tenant.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={
            "name": "Updated Tenant",
            "slug": test_tenant.slug,
            "description": "Updated description"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Tenant"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_tenant_unauthorized(
    client: AsyncClient,
    user_token: str,
    test_tenant: Tenant
):
    """Test tenant update by non-superuser."""
    response = await client.put(
        f"/tenants/{test_tenant.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Updated Tenant",
            "slug": test_tenant.slug,
            "description": "Updated description"
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_tenant(
    client: AsyncClient,
    superuser_token: str,
    test_tenant: Tenant
):
    """Test tenant deletion."""
    response = await client.delete(
        f"/tenants/{test_tenant.id}",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Tenant successfully deleted"
    
    # Verify tenant is deleted
    response = await client.get(
        f"/tenants/{test_tenant.id}",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_tenant_unauthorized(
    client: AsyncClient,
    user_token: str,
    test_tenant: Tenant
):
    """Test tenant deletion by non-superuser."""
    response = await client.delete(
        f"/tenants/{test_tenant.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
