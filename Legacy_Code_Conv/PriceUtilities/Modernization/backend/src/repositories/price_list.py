"""
Price List Repository Module
Version: 1.0.0
Last Updated: 2025-01-12

This module provides repository implementations for price list related models.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session, joinedload

from .base import SQLAlchemyRepository
from ..models.price_list import PriceList, PriceListItem, PriceHistory

class PriceListRepository(SQLAlchemyRepository[PriceList]):
    """Repository for managing price lists."""
    
    def __init__(self, session: Session):
        super().__init__(session, PriceList)
    
    def get_with_items(self, id: int) -> Optional[PriceList]:
        """Get price list with all items."""
        stmt = select(PriceList).options(
            joinedload(PriceList.items)
        ).where(PriceList.id == id)
        return self._session.execute(stmt).scalar_one_or_none()
    
    def get_active_lists(self) -> List[PriceList]:
        """Get all active price lists."""
        stmt = select(PriceList).where(
            and_(
                PriceList.is_active == True,
                or_(
                    PriceList.expiration_date.is_(None),
                    PriceList.expiration_date > datetime.utcnow()
                )
            )
        )
        return list(self._session.execute(stmt).scalars().all())
    
    def get_by_name(self, name: str) -> Optional[PriceList]:
        """Get price list by name."""
        stmt = select(PriceList).where(PriceList.name == name)
        return self._session.execute(stmt).scalar_one_or_none()

class PriceListItemRepository(SQLAlchemyRepository[PriceListItem]):
    """Repository for managing price list items."""
    
    def __init__(self, session: Session):
        super().__init__(session, PriceListItem)
    
    def get_by_billing_code(self, price_list_id: int, billing_code: str) -> Optional[PriceListItem]:
        """Get item by billing code within a price list."""
        stmt = select(PriceListItem).where(
            and_(
                PriceListItem.price_list_id == price_list_id,
                PriceListItem.billing_code == billing_code
            )
        )
        return self._session.execute(stmt).scalar_one_or_none()
    
    def bulk_update_prices(self, items: List[Dict[str, Any]]) -> List[PriceListItem]:
        """Bulk update prices with history tracking."""
        updated_items = []
        for item_data in items:
            item_id = item_data.pop('id')
            item = self.get(item_id)
            if item:
                # Create price history
                history = PriceHistory(
                    price_list_item_id=item.id,
                    prev_rent_allowable=item.rent_allowable_price,
                    prev_rent_billable=item.rent_billable_price,
                    prev_sale_allowable=item.sale_allowable_price,
                    prev_sale_billable=item.sale_billable_price,
                    new_rent_allowable=item_data.get('rent_allowable_price', item.rent_allowable_price),
                    new_rent_billable=item_data.get('rent_billable_price', item.rent_billable_price),
                    new_sale_allowable=item_data.get('sale_allowable_price', item.sale_allowable_price),
                    new_sale_billable=item_data.get('sale_billable_price', item.sale_billable_price),
                    change_type='bulk_update'
                )
                self._session.add(history)
                
                # Update item
                for key, value in item_data.items():
                    setattr(item, key, value)
                updated_items.append(item)
        
        self._session.commit()
        return updated_items

class PriceHistoryRepository(SQLAlchemyRepository[PriceHistory]):
    """Repository for managing price history."""
    
    def __init__(self, session: Session):
        super().__init__(session, PriceHistory)
    
    def get_item_history(self, item_id: int) -> List[PriceHistory]:
        """Get price history for a specific item."""
        stmt = select(PriceHistory).where(
            PriceHistory.price_list_item_id == item_id
        ).order_by(PriceHistory.change_date.desc())
        return list(self._session.execute(stmt).scalars().all())
