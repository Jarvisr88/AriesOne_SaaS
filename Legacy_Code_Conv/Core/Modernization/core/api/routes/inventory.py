"""
Inventory Routes Module
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
from ...database.models import InventoryItem, User
from ...security import require_permission
from ..models import (InventoryItemCreate, InventoryItemResponse,
                     InventoryItemUpdate)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("", response_model=InventoryItemResponse)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> InventoryItemResponse:
    """Create new inventory item."""
    # Check tenant access
    if not current_user.is_superuser and current_user.tenant_id != item_data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Create item
    item = InventoryItem(
        **item_data.model_dump(),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)

    return InventoryItemResponse.model_validate(item)


@router.get("", response_model=List[InventoryItemResponse])
async def list_inventory_items(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    status: str = None
) -> List[InventoryItemResponse]:
    """List inventory items."""
    # Build query
    query = select(InventoryItem)
    
    # Filter by tenant
    if not current_user.is_superuser:
        query = query.where(InventoryItem.tenant_id == current_user.tenant_id)
    
    # Apply filters
    if category:
        query = query.where(InventoryItem.category == category)
    if status:
        query = query.where(InventoryItem.status == status)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await session.execute(query)
    items = result.scalars().all()

    return [InventoryItemResponse.model_validate(i) for i in items]


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> InventoryItemResponse:
    """Get inventory item by ID."""
    # Get item
    stmt = select(InventoryItem).where(InventoryItem.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )

    # Check tenant access
    if not current_user.is_superuser and current_user.tenant_id != item.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return InventoryItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: UUID,
    item_data: InventoryItemUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> InventoryItemResponse:
    """Update inventory item."""
    # Get item
    stmt = select(InventoryItem).where(InventoryItem.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )

    # Check tenant access
    if not current_user.is_superuser and current_user.tenant_id != item.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Update item
    for field, value in item_data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    
    item.updated_by = current_user.id
    await session.commit()
    await session.refresh(item)

    return InventoryItemResponse.model_validate(item)


@router.delete("/{item_id}")
async def delete_inventory_item(
    item_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Delete inventory item."""
    # Get item
    stmt = select(InventoryItem).where(InventoryItem.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )

    # Check tenant access
    if not current_user.is_superuser and current_user.tenant_id != item.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Delete item
    await session.delete(item)
    await session.commit()

    return {"message": "Inventory item successfully deleted"}
