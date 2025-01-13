"""
Tenant Routes Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth.dependencies import get_current_superuser, get_current_user
from ...database import get_session
from ...database.models import Tenant, User
from ...security import require_permission
from ..models import TenantCreate, TenantResponse, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: Annotated[User, Depends(get_current_superuser)],
    session: AsyncSession = Depends(get_session)
) -> TenantResponse:
    """Create new tenant."""
    # Check if tenant with slug exists
    stmt = select(Tenant).where(Tenant.slug == tenant_data.slug)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this slug already exists"
        )

    # Create tenant
    tenant = Tenant(**tenant_data.model_dump())
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)

    return TenantResponse.model_validate(tenant)


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
) -> List[TenantResponse]:
    """List all tenants."""
    # Only superusers can see all tenants
    if not current_user.is_superuser:
        stmt = select(Tenant).where(
            Tenant.id == current_user.tenant_id
        ).offset(skip).limit(limit)
    else:
        stmt = select(Tenant).offset(skip).limit(limit)

    result = await session.execute(stmt)
    tenants = result.scalars().all()

    return [TenantResponse.model_validate(t) for t in tenants]


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> TenantResponse:
    """Get tenant by ID."""
    # Check access
    if not current_user.is_superuser and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get tenant
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    return TenantResponse.model_validate(tenant)


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session)
) -> TenantResponse:
    """Update tenant."""
    # Check access
    if not current_user.is_superuser and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get tenant
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Check if slug is taken
    if tenant_data.slug != tenant.slug:
        stmt = select(Tenant).where(
            Tenant.slug == tenant_data.slug,
            Tenant.id != tenant_id
        )
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this slug already exists"
            )

    # Update tenant
    for field, value in tenant_data.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)

    await session.commit()
    await session.refresh(tenant)

    return TenantResponse.model_validate(tenant)


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: UUID,
    current_user: Annotated[User, Depends(get_current_superuser)],
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Delete tenant."""
    # Get tenant
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Delete tenant
    await session.delete(tenant)
    await session.commit()

    return {"message": "Tenant successfully deleted"}
