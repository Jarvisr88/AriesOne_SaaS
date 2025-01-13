"""Organization routes."""

from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import (
    get_organization_service,
    get_current_active_user
)
from ..schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationWithUsers,
    OrganizationSettingsUpdate,
    UserOrganizationCreate,
    UserOrganizationUpdate,
    UserOrganizationResponse
)
from ...services.organization_service import OrganizationService
from ...domain.models.organization import (
    Organization,
    OrganizationType,
    OrganizationStatus,
    UserOrganization
)
from ...domain.models.user import User

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization: OrganizationCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> Organization:
    """Create new organization."""
    return await organization_service.create_organization(
        organization.model_dump(),
        current_user.id
    )

@router.get("/{organization_id}", response_model=OrganizationWithUsers)
async def get_organization(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> Organization:
    """Get organization by ID."""
    return await organization_service.get_by_id(organization_id)

@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: UUID,
    update: OrganizationUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> Organization:
    """Update organization."""
    return await organization_service.update_organization(
        organization_id,
        update.model_dump(exclude_unset=True),
        current_user.id
    )

@router.patch("/{organization_id}/settings", response_model=OrganizationResponse)
async def update_settings(
    organization_id: UUID,
    settings: OrganizationSettingsUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> Organization:
    """Update organization settings."""
    return await organization_service.update_settings(
        organization_id,
        settings.settings,
        current_user.id
    )

@router.patch("/{organization_id}/status", response_model=OrganizationResponse)
async def update_status(
    organization_id: UUID,
    status: OrganizationStatus,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> Organization:
    """Update organization status."""
    return await organization_service.update_status(
        organization_id,
        status,
        current_user.id
    )

@router.post("/{organization_id}/users", response_model=UserOrganizationResponse)
async def add_user(
    organization_id: UUID,
    user: UserOrganizationCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> UserOrganization:
    """Add user to organization."""
    return await organization_service.add_user(
        organization_id,
        user.user_id,
        user.role,
        current_user.id,
        user.permissions
    )

@router.delete("/{organization_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    organization_id: UUID,
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> None:
    """Remove user from organization."""
    await organization_service.remove_user(
        organization_id,
        user_id,
        current_user.id
    )

@router.patch("/{organization_id}/users/{user_id}", response_model=UserOrganizationResponse)
async def update_user_role(
    organization_id: UUID,
    user_id: UUID,
    update: UserOrganizationUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> UserOrganization:
    """Update user's role in organization."""
    return await organization_service.update_user_role(
        organization_id,
        user_id,
        update.role,
        current_user.id
    )

@router.get("", response_model=List[OrganizationResponse])
async def search_organizations(
    search: str = "",
    type: Optional[OrganizationType] = None,
    status: Optional[OrganizationStatus] = None,
    offset: int = 0,
    limit: int = 100,
    current_user: Annotated[User, Depends(get_current_active_user)],
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)]
) -> List[Organization]:
    """Search organizations."""
    return await organization_service.search_organizations(
        search,
        type=type,
        status=status,
        offset=offset,
        limit=limit
    )
