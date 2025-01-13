"""
Price repository implementation for managing price lists and items.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from ..core.database import Database, Repository
from .models import PriceList, PriceListItem

class PriceRepository(Repository):
    """Repository for price list management operations."""
    
    def __init__(self, db: Database):
        super().__init__(db, PriceList)

    async def get_active_price_list(self, company_id: int, date: datetime = None) -> Optional[PriceList]:
        """Get active price list for a company at a given date."""
        if date is None:
            date = datetime.utcnow()
            
        async with self.db.session() as session:
            result = await session.execute(
                select(PriceList).where(
                    and_(
                        PriceList.company_id == company_id,
                        PriceList.is_active == True,
                        PriceList.effective_date <= date,
                        (PriceList.expiration_date.is_(None) | 
                         (PriceList.expiration_date >= date))
                    )
                )
            )
            return result.scalar_one_or_none()

    async def get_price_list_items(
        self, 
        price_list_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[PriceListItem]:
        """Get items in a price list with pagination."""
        async with self.db.session() as session:
            result = await session.execute(
                select(PriceListItem)
                .where(PriceListItem.price_list_id == price_list_id)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()

    async def get_item_price(
        self, 
        company_id: int, 
        item_code: str, 
        date: datetime = None
    ) -> Optional[PriceListItem]:
        """Get price for an item at a given date."""
        if date is None:
            date = datetime.utcnow()
            
        async with self.db.session() as session:
            result = await session.execute(
                select(PriceListItem)
                .join(PriceList)
                .where(
                    and_(
                        PriceList.company_id == company_id,
                        PriceList.is_active == True,
                        PriceList.effective_date <= date,
                        (PriceList.expiration_date.is_(None) | 
                         (PriceList.expiration_date >= date)),
                        PriceListItem.item_code == item_code,
                        PriceListItem.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()

    async def update_item_price(
        self,
        price_list_id: int,
        item_code: str,
        unit_price: int,
        updated_by: str
    ) -> Optional[PriceListItem]:
        """Update price for an item."""
        async with self.db.session() as session:
            result = await session.execute(
                select(PriceListItem).where(
                    and_(
                        PriceListItem.price_list_id == price_list_id,
                        PriceListItem.item_code == item_code
                    )
                )
            )
            item = result.scalar_one_or_none()
            
            if item:
                item.unit_price = unit_price
                item.updated_by = updated_by
                await session.commit()
                
            return item

    async def deactivate_price_list(
        self,
        price_list_id: int,
        updated_by: str,
        expiration_date: datetime = None
    ) -> None:
        """Deactivate a price list."""
        if expiration_date is None:
            expiration_date = datetime.utcnow()
            
        await self.update(
            price_list_id,
            is_active=False,
            expiration_date=expiration_date,
            updated_by=updated_by
        )
