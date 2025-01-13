"""
Order Routes Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth.dependencies import get_current_user
from ...database import get_session
from ...database.models import InventoryItem, Order, OrderItem, User
from ...security import require_permission
from ..models import OrderCreate, OrderResponse, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> OrderResponse:
    """Create new order."""
    # Check tenant access
    if not current_user.is_superuser and current_user.tenant_id != order_data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Create order
    order = Order(
        **order_data.model_dump(exclude={'items'}),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    session.add(order)

    # Create order items
    subtotal = 0
    for item_data in order_data.items:
        # Get inventory item
        stmt = select(InventoryItem).where(
            InventoryItem.id == item_data.inventory_item_id,
            InventoryItem.tenant_id == order_data.tenant_id
        )
        result = await session.execute(stmt)
        inventory_item = result.scalar_one_or_none()

        if not inventory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory item {item_data.inventory_item_id} not found"
            )

        # Check quantity
        if inventory_item.quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough quantity for item {inventory_item.name}"
            )

        # Create order item
        order_item = OrderItem(
            order=order,
            inventory_item=inventory_item,
            **item_data.model_dump()
        )
        session.add(order_item)

        # Update inventory quantity
        inventory_item.quantity -= item_data.quantity

        # Calculate subtotal
        item_total = item_data.quantity * item_data.unit_price
        item_discount = item_total * (item_data.discount / 100)
        subtotal += item_total - item_discount

    # Calculate totals
    order.subtotal = subtotal
    order.tax = subtotal * 0.1  # 10% tax
    order.total = subtotal + order.tax

    await session.commit()
    await session.refresh(order)

    return OrderResponse.model_validate(order)


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    status: str = None
) -> List[OrderResponse]:
    """List orders."""
    # Build query
    query = select(Order)
    
    # Filter by tenant
    if not current_user.is_superuser:
        query = query.where(Order.tenant_id == current_user.tenant_id)
    
    # Apply filters
    if status:
        query = query.where(Order.status == status)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await session.execute(query)
    orders = result.scalars().all()

    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> OrderResponse:
    """Get order by ID."""
    # Get order
    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Check tenant access
    if not current_user.is_superuser and current_user.tenant_id != order.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return OrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    order_data: OrderUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> OrderResponse:
    """Update order."""
    # Get order
    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Check tenant access
    if not current_user.is_superuser and current_user.tenant_id != order.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Update order
    for field, value in order_data.model_dump(exclude={'items'}).items():
        setattr(order, field, value)
    
    order.updated_by = current_user.id

    # Update items if provided
    if order_data.items:
        # Return quantities to inventory
        for item in order.items:
            item.inventory_item.quantity += item.quantity
            await session.delete(item)

        # Create new items
        subtotal = 0
        for item_data in order_data.items:
            # Get inventory item
            stmt = select(InventoryItem).where(
                InventoryItem.id == item_data.inventory_item_id,
                InventoryItem.tenant_id == order.tenant_id
            )
            result = await session.execute(stmt)
            inventory_item = result.scalar_one_or_none()

            if not inventory_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Inventory item {item_data.inventory_item_id} not found"
                )

            # Check quantity
            if inventory_item.quantity < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough quantity for item {inventory_item.name}"
                )

            # Create order item
            order_item = OrderItem(
                order=order,
                inventory_item=inventory_item,
                **item_data.model_dump()
            )
            session.add(order_item)

            # Update inventory quantity
            inventory_item.quantity -= item_data.quantity

            # Calculate subtotal
            item_total = item_data.quantity * item_data.unit_price
            item_discount = item_total * (item_data.discount / 100)
            subtotal += item_total - item_discount

        # Update totals
        order.subtotal = subtotal
        order.tax = subtotal * 0.1  # 10% tax
        order.total = subtotal + order.tax

    await session.commit()
    await session.refresh(order)

    return OrderResponse.model_validate(order)


@router.delete("/{order_id}")
async def delete_order(
    order_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Delete order."""
    # Get order
    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Check tenant access
    if not current_user.is_superuser and current_user.tenant_id != order.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Return quantities to inventory
    for item in order.items:
        item.inventory_item.quantity += item.quantity

    # Delete order
    await session.delete(order)
    await session.commit()

    return {"message": "Order successfully deleted"}
