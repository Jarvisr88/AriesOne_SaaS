"""Organization service for business logic operations."""

from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from fastapi import HTTPException, status

from ..core.metrics import MetricsService
from ..repositories.organization_repository import OrganizationRepository
from ..domain.models.organization import (
    Organization,
    OrganizationType,
    OrganizationStatus,
    UserOrganization
)
from .base_service import BaseService

class OrganizationService(BaseService[Organization]):
    """Service for organization operations."""

    def __init__(
        self,
        repository: OrganizationRepository,
        metrics: Optional[MetricsService] = None
    ):
        """Initialize organization service."""
        super().__init__(repository, metrics)
        self.repository: OrganizationRepository = repository

    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate organization data."""
        required_fields = ["name", "code", "type"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        # Validate organization code format
        if not data["code"].isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization code must be alphanumeric"
            )

        # Validate organization type
        try:
            OrganizationType(data["type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization type"
            )

    async def create_organization(
        self,
        data: Dict[str, Any],
        created_by_id: UUID
    ) -> Organization:
        """Create new organization."""
        self.validate_data(data)

        # Check if code already exists
        existing = await self.repository.find_by_code(data["code"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization code already exists"
            )

        # Set default values
        data.setdefault("status", OrganizationStatus.ACTIVE)
        data["created_by_id"] = created_by_id

        organization = await self.create(data)

        # Add creator as admin
        await self.repository.add_user(
            organization.id,
            created_by_id,
            "admin",
            {"full_access": True}
        )

        if self.metrics:
            self.metrics.increment(f"organization.created.{data['type']}")

        return organization

    async def update_organization(
        self,
        organization_id: UUID,
        data: Dict[str, Any],
        updated_by_id: UUID
    ) -> Organization:
        """Update organization."""
        # Verify user has permission to update
        if not await self.has_admin_access(organization_id, updated_by_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to update organization"
            )

        # If code is being updated, check it's not taken
        if "code" in data:
            existing = await self.repository.find_by_code(data["code"])
            if existing and existing.id != organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization code already exists"
                )

        data["updated_by_id"] = updated_by_id
        return await self.update(organization_id, data)

    async def update_status(
        self,
        organization_id: UUID,
        status: OrganizationStatus,
        updated_by_id: UUID
    ) -> Organization:
        """Update organization status."""
        # Verify user has permission to update
        if not await self.has_admin_access(organization_id, updated_by_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to update organization status"
            )

        updated = await self.repository.update_status(organization_id, status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        if self.metrics:
            self.metrics.increment(f"organization.status.updated.{status.value}")

        return updated

    async def update_settings(
        self,
        organization_id: UUID,
        settings: Dict[str, Any],
        updated_by_id: UUID
    ) -> Organization:
        """Update organization settings."""
        # Verify user has permission to update
        if not await self.has_admin_access(organization_id, updated_by_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to update organization settings"
            )

        updated = await self.repository.update_settings(organization_id, settings)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        if self.metrics:
            self.metrics.increment("organization.settings.updated")

        return updated

    async def add_user(
        self,
        organization_id: UUID,
        user_id: UUID,
        role: str,
        added_by_id: UUID,
        permissions: Optional[Dict[str, Any]] = None
    ) -> UserOrganization:
        """Add user to organization."""
        # Verify adding user has admin access
        if not await self.has_admin_access(organization_id, added_by_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to add members"
            )

        user_org = await self.repository.add_user(
            organization_id,
            user_id,
            role,
            permissions
        )
        if not user_org:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error adding user to organization"
            )

        if self.metrics:
            self.metrics.increment(f"organization.user.added.{role}")

        return user_org

    async def remove_user(
        self,
        organization_id: UUID,
        user_id: UUID,
        removed_by_id: UUID
    ) -> bool:
        """Remove user from organization."""
        # Verify removing user has admin access
        if not await self.has_admin_access(organization_id, removed_by_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to remove members"
            )

        # Don't allow removing the last admin
        if await self.is_last_admin(organization_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last administrator"
            )

        removed = await self.repository.remove_user(organization_id, user_id)
        if removed and self.metrics:
            self.metrics.increment("organization.user.removed")

        return removed

    async def update_user_role(
        self,
        organization_id: UUID,
        user_id: UUID,
        role: str,
        updated_by_id: UUID
    ) -> UserOrganization:
        """Update user's role in organization."""
        # Verify updating user has admin access
        if not await self.has_admin_access(organization_id, updated_by_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to update member roles"
            )

        # Don't allow changing role of the last admin
        if (
            role != "admin"
            and await self.is_last_admin(organization_id, user_id)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change role of the last administrator"
            )

        updated = await self.repository.update_user_role(
            organization_id,
            user_id,
            role
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in organization"
            )

        if self.metrics:
            self.metrics.increment(f"organization.user.role.updated.{role}")

        return updated

    async def has_admin_access(
        self,
        organization_id: UUID,
        user_id: UUID
    ) -> bool:
        """Check if user has admin access to organization."""
        org = await self.get_by_id(organization_id)
        for user_org in org.users:
            if user_org.user_id == user_id and user_org.role == "admin":
                return True
        return False

    async def is_last_admin(
        self,
        organization_id: UUID,
        user_id: UUID
    ) -> bool:
        """Check if user is the last admin of organization."""
        org = await self.get_by_id(organization_id)
        admin_count = sum(1 for user_org in org.users if user_org.role == "admin")
        if admin_count == 1:
            for user_org in org.users:
                if user_org.user_id == user_id and user_org.role == "admin":
                    return True
        return False

    async def search_organizations(
        self,
        search_term: str,
        type: Optional[OrganizationType] = None,
        status: Optional[OrganizationStatus] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """Search organizations with filters."""
        conditions = []
        if type:
            conditions.append(Organization.type == type)
        if status:
            conditions.append(Organization.status == status)

        return await self.repository.search_organizations(
            search_term,
            offset=offset,
            limit=limit,
            *conditions
        )
