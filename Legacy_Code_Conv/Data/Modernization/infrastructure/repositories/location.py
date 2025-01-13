"""Location repository implementation module."""
from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.location import Location
from infrastructure.repositories.base import Repository

class LocationRepository(Repository[Location]):
    """Location repository implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: Database session.
        """
        super().__init__(session, Location)

    async def get_by_company(self, company_id: UUID) -> List[Location]:
        """Get all locations for a company.
        
        Args:
            company_id: Company ID.
            
        Returns:
            List of locations.
        """
        result = await self._session.execute(
            select(Location).where(
                Location.company_id == company_id,
                Location.is_deleted == False
            )
        )
        return list(result.scalars().all())

    async def get_active_locations(self, company_id: UUID) -> List[Location]:
        """Get active locations for a company.
        
        Args:
            company_id: Company ID.
            
        Returns:
            List of active locations.
        """
        result = await self._session.execute(
            select(Location).where(
                Location.company_id == company_id,
                Location.is_active == True,
                Location.is_deleted == False
            )
        )
        return list(result.scalars().all())

    async def soft_delete(self, id: UUID) -> None:
        """Soft delete a location.
        
        Args:
            id: Location ID.
        """
        location = await self.get_by_id(id)
        if location:
            location.is_deleted = True
            await self.update(location)
