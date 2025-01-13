"""
Inventory Integration Tests Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from core.database.models import InventoryItem, Tenant, User


@pytest.mark.asyncio
async def test_create_inventory_item(
    client: AsyncClient,
    user_token: str,
    test_tenant: Tenant
):
    """Test inventory item creation."""
    response = await client.post(
        "/inventory",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Test Item",
            "description": "Test description",
            "category": "equipment",
            "status": "available",
            "quantity": 10,
            "unit_price": 100.00,
            "tenant_id": str(test_tenant.id)
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["quantity"] == 10
    assert data["tenant_id"] == str(test_tenant.id)


@pytest.mark.asyncio
async def test_create_inventory_item_wrong_tenant(
    client: AsyncClient,
    user_token: str
):
    """Test inventory item creation for wrong tenant."""
    response = await client.post(
        "/inventory",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Test Item",
            "description": "Test description",
            "category": "equipment",
            "status": "available",
            "quantity": 10,
            "unit_price": 100.00,
            "tenant_id": str(uuid4())
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_list_inventory_items(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test inventory item listing."""
    # Create test items
    items = [
        InventoryItem(
            name=f"Item {i}",
            description=f"Description {i}",
            category="equipment",
            status="available",
            quantity=10,
            unit_price=100.00,
            tenant_id=test_tenant.id,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        for i in range(3)
    ]
    session.add_all(items)
    await session.commit()
    
    response = await client.get(
        "/inventory",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_list_inventory_items_filtered(
    client: AsyncClient,
    user_token: str
):
    """Test inventory item listing with filters."""
    response = await client.get(
        "/inventory?category=equipment&status=available",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(item["category"] == "equipment" for item in data)
    assert all(item["status"] == "available" for item in data)


@pytest.mark.asyncio
async def test_get_inventory_item(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test getting inventory item by ID."""
    # Create test item
    item = InventoryItem(
        name="Test Item",
        description="Test description",
        category="equipment",
        status="available",
        quantity=10,
        unit_price=100.00,
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    
    response = await client.get(
        f"/inventory/{item.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(item.id)
    assert data["name"] == item.name


@pytest.mark.asyncio
async def test_update_inventory_item(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test inventory item update."""
    # Create test item
    item = InventoryItem(
        name="Test Item",
        description="Test description",
        category="equipment",
        status="available",
        quantity=10,
        unit_price=100.00,
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    
    response = await client.put(
        f"/inventory/{item.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Updated Item",
            "description": "Updated description",
            "quantity": 15
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Item"
    assert data["description"] == "Updated description"
    assert data["quantity"] == 15


@pytest.mark.asyncio
async def test_delete_inventory_item(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test inventory item deletion."""
    # Create test item
    item = InventoryItem(
        name="Test Item",
        description="Test description",
        category="equipment",
        status="available",
        quantity=10,
        unit_price=100.00,
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    
    response = await client.delete(
        f"/inventory/{item.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Inventory item successfully deleted"
    
    # Verify item is deleted
    response = await client.get(
        f"/inventory/{item.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
