"""
Authorization Security Tests Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import InventoryItem, Order, Tenant, User


@pytest.mark.asyncio
async def test_tenant_isolation(
    client: AsyncClient,
    session: AsyncSession,
    user_token: str,
    test_tenant: Tenant,
    test_user: User
):
    """Test tenant data isolation."""
    # Create another tenant and user
    other_tenant = Tenant(
        name="Other Tenant",
        slug="other-tenant",
        subscription_plan="premium",
        max_users=10,
        max_storage=1073741824,
        used_storage=0
    )
    session.add(other_tenant)
    await session.commit()
    
    # Try to access other tenant's data
    response = await client.get(
        f"/tenants/{other_tenant.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_rbac_enforcement(
    client: AsyncClient,
    session: AsyncSession,
    user_token: str,
    test_tenant: Tenant,
    test_user: User
):
    """Test Role-Based Access Control."""
    # Try admin-only operations as regular user
    operations = [
        ("POST", "/tenants"),
        ("DELETE", f"/tenants/{test_tenant.id}"),
        ("POST", "/users/admin"),
        ("GET", "/system/logs"),
    ]
    
    for method, path in operations:
        response = await client.request(
            method,
            path,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_object_level_permissions(
    client: AsyncClient,
    session: AsyncSession,
    user_token: str,
    test_tenant: Tenant,
    test_user: User
):
    """Test object-level permission enforcement."""
    # Create inventory item owned by another user
    other_user = User(
        email="other@example.com",
        hashed_password="hashed",
        is_active=True,
        tenant_id=test_tenant.id
    )
    session.add(other_user)
    await session.commit()
    
    item = InventoryItem(
        name="Test Item",
        tenant_id=test_tenant.id,
        created_by=other_user.id,
        quantity=10,
        unit_price=100.00
    )
    session.add(item)
    await session.commit()
    
    # Try to modify other user's item
    response = await client.put(
        f"/inventory/{item.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Modified Item"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_permission_escalation(
    client: AsyncClient,
    session: AsyncSession,
    user_token: str,
    test_user: User
):
    """Test protection against permission escalation."""
    # Try to escalate own privileges
    response = await client.put(
        f"/users/{test_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"is_superuser": True}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_api_scope_enforcement(
    client: AsyncClient,
    user_token: str
):
    """Test API scope enforcement."""
    # Try to access endpoints with insufficient scope
    response = await client.get(
        "/admin/metrics",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient, user_token: str):
    """Test API rate limiting."""
    # Make multiple rapid requests
    for _ in range(100):
        response = await client.get(
            "/inventory",
            headers={"Authorization": f"Bearer {user_token}"}
        )
    
    # Next request should be rate limited
    response = await client.get(
        "/inventory",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_audit_logging(
    client: AsyncClient,
    session: AsyncSession,
    superuser_token: str
):
    """Test audit logging for sensitive operations."""
    # Perform sensitive operation
    response = await client.post(
        "/tenants",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={
            "name": "New Tenant",
            "slug": "new-tenant",
            "subscription_plan": "premium"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Check audit logs
    response = await client.get(
        "/system/audit-logs",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    logs = response.json()
    
    assert any(
        log["action"] == "tenant_created"
        and log["resource_type"] == "tenant"
        for log in logs
    )


@pytest.mark.asyncio
async def test_data_access_patterns(
    client: AsyncClient,
    session: AsyncSession,
    user_token: str,
    test_tenant: Tenant,
    test_user: User
):
    """Test data access patterns for suspicious behavior."""
    # Create test orders
    orders = []
    for _ in range(5):
        order = Order(
            customer_name="Test Customer",
            tenant_id=test_tenant.id,
            created_by=test_user.id,
            total=100.00
        )
        orders.append(order)
    
    session.add_all(orders)
    await session.commit()
    
    # Try to mass-fetch data
    response = await client.get(
        "/orders?limit=1000000",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_resource_isolation(
    client: AsyncClient,
    session: AsyncSession,
    user_token: str,
    test_tenant: Tenant
):
    """Test resource isolation between tenants."""
    # Create resource in test tenant
    response = await client.post(
        "/inventory",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Test Item",
            "tenant_id": str(test_tenant.id),
            "quantity": 10,
            "unit_price": 100.00
        }
    )
    assert response.status_code == status.HTTP_200_OK
    item_id = response.json()["id"]
    
    # Try to access resource with different tenant ID
    response = await client.get(
        f"/inventory/{item_id}",
        headers={
            "Authorization": f"Bearer {user_token}",
            "X-Tenant-ID": str(test_tenant.id + 1)
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
