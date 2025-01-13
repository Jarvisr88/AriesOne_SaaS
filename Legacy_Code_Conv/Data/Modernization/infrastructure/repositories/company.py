"""Company repository implementation module.

This module provides the repository implementation for Company entities,
handling database operations and queries specific to companies.

The CompanyRepository extends the base Repository class and adds
company-specific operations like NPI lookup and active company filtering.

Example:
    ```python
    # Create repository
    session = AsyncSession(engine)
    repo = CompanyRepository(session)
    
    # Get company by NPI
    company = await repo.get_by_npi("1234567890")
    
    # Get active companies
    active = await repo.get_active_companies(
        name="Health",
        offset=0,
        limit=10
    )
    ```
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.company import Company
from infrastructure.repositories.base import Repository

class CompanyRepository(Repository[Company]):
    """Repository for managing Company entities.
    
    This class extends the base Repository to provide company-specific
    database operations. It includes methods for:
    - Retrieving companies by NPI
    - Filtering active companies
    - Soft deleting companies
    
    The repository uses SQLAlchemy for database operations and supports
    both synchronous and asynchronous operations.
    
    Attributes:
        _session (AsyncSession): Database session for operations
        _model (Type[Company]): Company model class
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: AsyncSession for database operations
        """
        super().__init__(session, Company)

    async def get_by_npi(self, npi: str) -> Optional[Company]:
        """Get company by National Provider Identifier.
        
        Retrieves a company using its unique NPI number. Returns None if
        no company is found with the given NPI.
        
        Args:
            npi: National Provider Identifier (10-digit number)
            
        Returns:
            Company if found, None otherwise
            
        Example:
            ```python
            company = await repo.get_by_npi("1234567890")
            if company:
                print(f"Found: {company.name}")
            ```
        """
        result = await self._session.execute(
            select(Company).where(Company.npi == npi)
        )
        return result.scalar_one_or_none()

    async def get_active_companies(
        self,
        name: Optional[str] = None,
        npi: Optional[str] = None,
        is_active: bool = True,
        offset: int = 0,
        limit: int = 10
    ) -> List[Company]:
        """Get active companies with optional filtering.
        
        Retrieves a list of active companies, optionally filtered by name
        or NPI. Supports pagination through offset and limit parameters.
        
        Args:
            name: Optional company name filter (partial match)
            npi: Optional NPI filter (exact match)
            is_active: Filter by active status
            offset: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of companies matching the criteria
            
        Example:
            ```python
            # Get first 10 active companies with "Health" in name
            companies = await repo.get_active_companies(
                name="Health",
                offset=0,
                limit=10
            )
            ```
        """
        query = select(Company).where(Company.is_deleted == False)
        
        if is_active:
            query = query.where(Company.is_active == True)
        
        # Apply filters if provided
        if name:
            query = query.where(Company.name.ilike(f"%{name}%"))
        if npi:
            query = query.where(Company.npi == npi)
        
        # Add pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def soft_delete(self, id: UUID) -> None:
        """Soft delete a company.
        
        Marks a company as deleted without removing it from the database.
        This preserves the company's data while making it inactive.
        
        Args:
            id: UUID of the company to delete
            
        Example:
            ```python
            # Soft delete company
            await repo.soft_delete(company_id)
            
            # Verify deletion
            company = await repo.get_by_id(company_id)
            assert company.is_deleted == True
            ```
        """
        company = await self.get_by_id(id)
        if company:
            company.is_deleted = True
            await self.update(company)
