"""
Company repository implementation for managing company-related operations.
"""
from typing import List, Optional
from sqlalchemy import select
from ..core.database import Database, Repository
from .models import Company, Location

class CompanyRepository(Repository):
    """Repository for company management operations."""
    
    def __init__(self, db: Database):
        super().__init__(db, Company)

    async def get_by_code(self, code: str) -> Optional[Company]:
        """Get company by unique code."""
        async with self.db.session() as session:
            result = await session.execute(
                select(Company).where(Company.code == code)
            )
            return result.scalar_one_or_none()

    async def get_locations(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Location]:
        """Get locations for a company."""
        async with self.db.session() as session:
            result = await session.execute(
                select(Location)
                .where(Location.company_id == company_id)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()

    async def add_location(
        self,
        company_id: int,
        name: str,
        address_line1: str,
        city: str,
        state: str,
        zip_code: str,
        address_line2: str = None,
        created_by: str = None
    ) -> Location:
        """Add a new location to a company."""
        async with self.db.session() as session:
            location = Location(
                company_id=company_id,
                name=name,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                zip_code=zip_code,
                created_by=created_by,
                updated_by=created_by
            )
            session.add(location)
            await session.commit()
            return location

    async def update_location(
        self,
        location_id: int,
        updated_by: str,
        **kwargs
    ) -> Optional[Location]:
        """Update a company location."""
        async with self.db.session() as session:
            location = await session.get(Location, location_id)
            if location:
                for key, value in kwargs.items():
                    if hasattr(location, key):
                        setattr(location, key, value)
                location.updated_by = updated_by
                await session.commit()
            return location

    async def deactivate_location(
        self,
        location_id: int,
        updated_by: str
    ) -> None:
        """Deactivate a company location."""
        await self.update_location(
            location_id,
            updated_by=updated_by,
            is_active=False
        )

    async def activate_location(
        self,
        location_id: int,
        updated_by: str
    ) -> None:
        """Activate a company location."""
        await self.update_location(
            location_id,
            updated_by=updated_by,
            is_active=True
        )
