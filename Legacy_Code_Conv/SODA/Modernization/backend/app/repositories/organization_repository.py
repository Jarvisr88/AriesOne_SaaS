"""Organization repository for database operations."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.sql import Select

from ..core.database.base_repository import BaseRepository
from ..core.database.database import DatabaseService
from ..core.cache import CacheService
from ..core.metrics import MetricsService
from ..domain.models.organization import (
    Organization,
    OrganizationType,
    OrganizationStatus,
    UserOrganization
)

class OrganizationRepository(BaseRepository[Organization]):
    """Repository for organization operations."""

    def __init__(
        self,
        db: DatabaseService,
        cache: Optional[CacheService] = None,
        metrics: Optional[MetricsService] = None
    ):
        """Initialize organization repository."""
        super().__init__(db, Organization, cache, metrics)
        self.cache_ttl = 3600  # 1 hour for organizations

    async def find_by_code(self, code: str) -> Optional[Organization]:
        """Find organization by code."""
        return await self.find_one(Organization.code == code)

    async def find_by_type(
        self,
        type: OrganizationType,
        offset: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """Find organizations by type."""
        return await self.find_many(
            Organization.type == type,
            offset=offset,
            limit=limit
        )

    async def find_active_organizations(
        self,
        offset: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """Find all active organizations."""
        return await self.find_many(
            Organization.status == OrganizationStatus.ACTIVE,
            offset=offset,
            limit=limit
        )

    async def find_by_parent(
        self,
        parent_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """Find organizations by parent."""
        return await self.find_many(
            Organization.parent_id == parent_id,
            offset=offset,
            limit=limit
        )

    async def search_organizations(
        self,
        search_term: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """Search organizations by name or code."""
        search_pattern = f"%{search_term}%"
        return await self.find_many(
            or_(
                Organization.name.ilike(search_pattern),
                Organization.code.ilike(search_pattern)
            ),
            offset=offset,
            limit=limit
        )

    async def update_status(
        self,
        organization_id: UUID,
        status: OrganizationStatus
    ) -> Optional[Organization]:
        """Update organization's status."""
        return await self.update(organization_id, {"status": status})

    async def update_settings(
        self,
        organization_id: UUID,
        settings: Dict[str, Any]
    ) -> Optional[Organization]:
        """Update organization's settings."""
        org = await self.get_by_id(organization_id)
        if org:
            current_settings = org.settings or {}
            current_settings.update(settings)
            return await self.update(
                organization_id,
                {"settings": current_settings}
            )
        return None

    async def add_user(
        self,
        organization_id: UUID,
        user_id: UUID,
        role: str,
        permissions: Optional[Dict[str, Any]] = None
    ) -> Optional[UserOrganization]:
        """Add user to organization."""
        try:
            async with self.db.transaction() as session:
                user_org = UserOrganization(
                    organization_id=organization_id,
                    user_id=user_id,
                    role=role,
                    permissions=permissions
                )
                session.add(user_org)
                await session.flush()
                await session.refresh(user_org)
                return user_org

        except Exception as e:
            self.logger.error(f"Error adding user to organization: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment("organization.error.add_user")
            return None

    async def remove_user(
        self,
        organization_id: UUID,
        user_id: UUID
    ) -> bool:
        """Remove user from organization."""
        try:
            async with self.db.transaction() as session:
                result = await session.execute(
                    delete(UserOrganization).where(
                        and_(
                            UserOrganization.organization_id == organization_id,
                            UserOrganization.user_id == user_id
                        )
                    )
                )
                return result.rowcount > 0

        except Exception as e:
            self.logger.error(f"Error removing user from organization: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment("organization.error.remove_user")
            return False

    async def update_user_role(
        self,
        organization_id: UUID,
        user_id: UUID,
        role: str
    ) -> Optional[UserOrganization]:
        """Update user's role in organization."""
        try:
            async with self.db.transaction() as session:
                result = await session.execute(
                    select(UserOrganization).where(
                        and_(
                            UserOrganization.organization_id == organization_id,
                            UserOrganization.user_id == user_id
                        )
                    )
                )
                user_org = result.scalar_one_or_none()
                if user_org:
                    user_org.role = role
                    await session.flush()
                    await session.refresh(user_org)
                    return user_org
                return None

        except Exception as e:
            self.logger.error(f"Error updating user role in organization: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment("organization.error.update_user_role")
            return None
