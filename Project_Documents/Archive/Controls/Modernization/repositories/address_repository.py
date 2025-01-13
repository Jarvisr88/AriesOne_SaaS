"""
Address Repository Module
Provides data access layer for address operations.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..models.address_model import Address
from .base import BaseRepository

class AddressRepository(BaseRepository):
    """Repository for address data access."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize address repository.
        
        Args:
            session: Database session
        """
        super().__init__(session)
        
    async def create(self, address: Address) -> Address:
        """
        Create new address record.
        
        Args:
            address: Address to create
            
        Returns:
            Created address
        """
        self.session.add(address)
        await self.session.commit()
        await self.session.refresh(address)
        return address
    
    async def get_by_id(self, address_id: int) -> Optional[Address]:
        """
        Get address by ID.
        
        Args:
            address_id: Address ID
            
        Returns:
            Address if found, None otherwise
        """
        query = select(Address).where(Address.id == address_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update(self, address_id: int, address: Address) -> Optional[Address]:
        """
        Update existing address.
        
        Args:
            address_id: Address ID
            address: Updated address data
            
        Returns:
            Updated address if found, None otherwise
        """
        query = (
            update(Address)
            .where(Address.id == address_id)
            .values(address.dict(exclude={'id'}))
            .returning(Address)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, address_id: int) -> bool:
        """
        Delete address by ID.
        
        Args:
            address_id: Address ID
            
        Returns:
            True if deleted, False if not found
        """
        query = delete(Address).where(Address.id == address_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_by_zip(self, zip_code: str) -> List[Address]:
        """
        Get addresses by ZIP code.
        
        Args:
            zip_code: ZIP code to search
            
        Returns:
            List of matching addresses
        """
        query = select(Address).where(Address.zip_code == zip_code)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_state(self, state: str) -> List[Address]:
        """
        Get addresses by state.
        
        Args:
            state: State code to search
            
        Returns:
            List of matching addresses
        """
        query = select(Address).where(Address.state == state.upper())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def search(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None
    ) -> List[Address]:
        """
        Search addresses by criteria.
        
        Args:
            city: Optional city to search
            state: Optional state to search
            zip_code: Optional ZIP code to search
            
        Returns:
            List of matching addresses
        """
        query = select(Address)
        
        if city:
            query = query.where(Address.city.ilike(f"%{city}%"))
        if state:
            query = query.where(Address.state == state.upper())
        if zip_code:
            query = query.where(Address.zip_code.startswith(zip_code))
            
        result = await self.session.execute(query)
        return result.scalars().all()
