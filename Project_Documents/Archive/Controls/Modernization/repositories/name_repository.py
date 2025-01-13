"""
Name Repository Module
Provides data access layer for name operations.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..models.name_model import Name
from .base import BaseRepository

class NameRepository(BaseRepository):
    """Repository for name data access."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize name repository.
        
        Args:
            session: Database session
        """
        super().__init__(session)
        
    async def create(self, name: Name) -> Name:
        """
        Create new name record.
        
        Args:
            name: Name to create
            
        Returns:
            Created name
        """
        self.session.add(name)
        await self.session.commit()
        await self.session.refresh(name)
        return name
    
    async def get_by_id(self, name_id: int) -> Optional[Name]:
        """
        Get name by ID.
        
        Args:
            name_id: Name ID
            
        Returns:
            Name if found, None otherwise
        """
        query = select(Name).where(Name.id == name_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update(self, name_id: int, name: Name) -> Optional[Name]:
        """
        Update existing name.
        
        Args:
            name_id: Name ID
            name: Updated name data
            
        Returns:
            Updated name if found, None otherwise
        """
        query = (
            update(Name)
            .where(Name.id == name_id)
            .values(name.dict(exclude={'id'}))
            .returning(Name)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, name_id: int) -> bool:
        """
        Delete name by ID.
        
        Args:
            name_id: Name ID
            
        Returns:
            True if deleted, False if not found
        """
        query = delete(Name).where(Name.id == name_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
    
    async def search(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        courtesy_title: Optional[str] = None
    ) -> List[Name]:
        """
        Search names by criteria.
        
        Args:
            first_name: Optional first name to search
            last_name: Optional last name to search
            courtesy_title: Optional courtesy title to search
            
        Returns:
            List of matching names
        """
        query = select(Name)
        
        if first_name:
            query = query.where(Name.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.where(Name.last_name.ilike(f"%{last_name}%"))
        if courtesy_title:
            query = query.where(Name.courtesy_title == courtesy_title)
            
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_full_name(self, full_name: str) -> List[Name]:
        """
        Get names matching full name search.
        
        Args:
            full_name: Full name to search
            
        Returns:
            List of matching names
        """
        # Split full name into parts
        parts = full_name.strip().split()
        
        if len(parts) < 2:
            return []
            
        # Search by first and last name
        query = select(Name).where(
            Name.first_name.ilike(f"%{parts[0]}%"),
            Name.last_name.ilike(f"%{parts[-1]}%")
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
