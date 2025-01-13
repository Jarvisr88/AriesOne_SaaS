"""
Order Integration Tests Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import InventoryItem, Order, Tenant, User


@pytest.mark.asyncio
async def test_create_order(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test order creation."""
    # Create test inventory item
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
    
    response = await client.post(
        "/orders",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "customer_name": "Test Customer",
            "customer_email": "customer@example.com",
            "shipping_address": "123 Test St",
            "billing_address": "123 Test St",
            "status": "pending",
            "tenant_id": str(test_tenant.id),
            "items": [
                {
                    "inventory_item_id": str(item.id),
                    "quantity": 2,
                    "unit_price": 100.00,
                    "discount": 0
                }
            ]
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["customer_name"] == "Test Customer"
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["subtotal"] == 200.00
    assert data["tax"] == 20.00
    assert data["total"] == 220.00


@pytest.mark.asyncio
async def test_create_order_insufficient_quantity(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test order creation with insufficient inventory."""
    # Create test inventory item with low quantity
    item = InventoryItem(
        name="Test Item",
        description="Test description",
        category="equipment",
        status="available",
        quantity=1,
        unit_price=100.00,
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    
    response = await client.post(
        "/orders",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "customer_name": "Test Customer",
            "customer_email": "customer@example.com",
            "shipping_address": "123 Test St",
            "billing_address": "123 Test St",
            "status": "pending",
            "tenant_id": str(test_tenant.id),
            "items": [
                {
                    "inventory_item_id": str(item.id),
                    "quantity": 2,
                    "unit_price": 100.00,
                    "discount": 0
                }
            ]
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Not enough quantity" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_orders(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test order listing."""
    # Create test orders
    orders = [
        Order(
            customer_name=f"Customer {i}",
            customer_email=f"customer{i}@example.com",
            shipping_address="123 Test St",
            billing_address="123 Test St",
            status="pending",
            tenant_id=test_tenant.id,
            created_by=test_user.id,
            updated_by=test_user.id,
            subtotal=100.00,
            tax=10.00,
            total=110.00
        )
        for i in range(3)
    ]
    session.add_all(orders)
    await session.commit()
    
    response = await client.get(
        "/orders",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_get_order(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test getting order by ID."""
    # Create test order
    order = Order(
        customer_name="Test Customer",
        customer_email="customer@example.com",
        shipping_address="123 Test St",
        billing_address="123 Test St",
        status="pending",
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        updated_by=test_user.id,
        subtotal=100.00,
        tax=10.00,
        total=110.00
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    
    response = await client.get(
        f"/orders/{order.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(order.id)
    assert data["customer_name"] == order.customer_name


@pytest.mark.asyncio
async def test_update_order(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test order update."""
    # Create test order
    order = Order(
        customer_name="Test Customer",
        customer_email="customer@example.com",
        shipping_address="123 Test St",
        billing_address="123 Test St",
        status="pending",
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        updated_by=test_user.id,
        subtotal=100.00,
        tax=10.00,
        total=110.00
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    
    response = await client.put(
        f"/orders/{order.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "customer_name": "Updated Customer",
            "status": "processing"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["customer_name"] == "Updated Customer"
    assert data["status"] == "processing"


@pytest.mark.asyncio
async def test_delete_order(
    client: AsyncClient,
    user_token: str,
    session: AsyncSession,
    test_tenant: Tenant,
    test_user: User
):
    """Test order deletion."""
    # Create test order
    order = Order(
        customer_name="Test Customer",
        customer_email="customer@example.com",
        shipping_address="123 Test St",
        billing_address="123 Test St",
        status="pending",
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        updated_by=test_user.id,
        subtotal=100.00,
        tax=10.00,
        total=110.00
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    
    response = await client.delete(
        f"/orders/{order.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Order successfully deleted"
    
    # Verify order is deleted
    response = await client.get(
        f"/orders/{order.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
