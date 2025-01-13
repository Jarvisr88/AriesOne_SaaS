"""
Services for the Price Utilities module.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from .models import (
    PriceListItem, PriceUpdate, ICDCode, PriceParameter,
    PriceCalculationRule, AuditLog, PriceType, PriceCategory
)
from .database import get_db
from .cache import cache_manager

class PriceService:
    """Price management service."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def get_price_list(
        self,
        company_id: str,
        page: int = 1,
        page_size: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PriceListItem]:
        """Get price list with pagination and filtering."""
        cache_key = f"price_list:{company_id}:{page}:{page_size}:{filters}"
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return [PriceListItem(**item) for item in cached_result]

        query = select(PriceListItem).where(
            PriceListItem.company_id == company_id,
            PriceListItem.is_active == True
        )

        if filters:
            for key, value in filters.items():
                if hasattr(PriceListItem, key):
                    query = query.where(getattr(PriceListItem, key) == value)

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        await cache_manager.set(cache_key, [item.dict() for item in items], expire=300)
        return items

    async def update_prices(self, update: PriceUpdate, user_id: str) -> List[PriceListItem]:
        """Update prices in bulk."""
        items = []
        async with self.db.begin():
            for item_code in update.item_codes:
                query = select(PriceListItem).where(
                    PriceListItem.item_code == item_code,
                    PriceListItem.is_active == True
                )
                result = await self.db.execute(query)
                item = result.scalar_one_or_none()

                if not item:
                    continue

                # Calculate new price
                old_price = getattr(item, f"{update.price_category.value}_price")
                new_price = (
                    Decimal(update.update_value)
                    if update.update_type == "fixed"
                    else old_price * (1 + Decimal(update.update_value) / 100)
                )

                # Create new price record
                new_item = PriceListItem(
                    **item.dict(),
                    id=None,
                    effective_date=update.effective_date,
                    **{f"{update.price_category.value}_price": new_price},
                    created_by=user_id,
                    updated_by=user_id
                )
                self.db.add(new_item)
                items.append(new_item)

                # Deactivate old price
                await self.db.execute(
                    update(PriceListItem)
                    .where(PriceListItem.id == item.id)
                    .values(
                        is_active=False,
                        expiration_date=update.effective_date,
                        updated_by=user_id
                    )
                )

                # Log the change
                audit_log = AuditLog(
                    company_id=item.company_id,
                    action="price_update",
                    entity_type="price_list_item",
                    entity_id=item.id,
                    changes={
                        "old_price": str(old_price),
                        "new_price": str(new_price),
                        "price_category": update.price_category.value,
                        "update_type": update.update_type,
                        "update_value": str(update.update_value)
                    },
                    user_id=user_id
                )
                self.db.add(audit_log)

        await cache_manager.delete_pattern(f"price_list:{item.company_id}:*")
        return items

class ICDCodeService:
    """ICD code management service."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def get_icd_codes(
        self,
        code_type: str,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None
    ) -> List[ICDCode]:
        """Get ICD codes with pagination and search."""
        cache_key = f"icd_codes:{code_type}:{page}:{page_size}:{search}"
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return [ICDCode(**code) for code in cached_result]

        query = select(ICDCode).where(
            ICDCode.type == code_type,
            ICDCode.is_active == True
        )

        if search:
            query = query.where(
                (ICDCode.code.ilike(f"%{search}%")) |
                (ICDCode.description.ilike(f"%{search}%"))
            )

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        codes = result.scalars().all()

        await cache_manager.set(cache_key, [code.dict() for code in codes], expire=300)
        return codes

    async def update_icd_codes(
        self,
        codes: List[ICDCode],
        user_id: str
    ) -> List[ICDCode]:
        """Update ICD codes in bulk."""
        updated_codes = []
        async with self.db.begin():
            for code in codes:
                # Check if code exists
                query = select(ICDCode).where(
                    ICDCode.code == code.code,
                    ICDCode.type == code.type
                )
                result = await self.db.execute(query)
                existing_code = result.scalar_one_or_none()

                if existing_code:
                    # Deactivate old code
                    await self.db.execute(
                        update(ICDCode)
                        .where(ICDCode.code == code.code)
                        .values(
                            is_active=False,
                            deactivation_date=datetime.utcnow()
                        )
                    )

                # Create new code
                new_code = ICDCode(**code.dict())
                self.db.add(new_code)
                updated_codes.append(new_code)

                # Log the change
                audit_log = AuditLog(
                    action="icd_code_update",
                    entity_type="icd_code",
                    entity_id=code.code,
                    changes={
                        "old_code": existing_code.dict() if existing_code else None,
                        "new_code": code.dict()
                    },
                    user_id=user_id
                )
                self.db.add(audit_log)

        await cache_manager.delete_pattern("icd_codes:*")
        return updated_codes

class PriceCalculationService:
    """Price calculation service."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def calculate_price(
        self,
        base_price: Decimal,
        company_id: str,
        price_type: PriceType,
        price_category: PriceCategory
    ) -> Decimal:
        """Calculate price based on rules."""
        # Get applicable rules
        query = select(PriceCalculationRule).where(
            PriceCalculationRule.company_id == company_id,
            PriceCalculationRule.price_type == price_type,
            PriceCalculationRule.price_category == price_category,
            PriceCalculationRule.is_active == True
        )
        result = await self.db.execute(query)
        rules = result.scalars().all()

        # Apply rules in sequence
        calculated_price = base_price
        for rule in rules:
            try:
                # Simple eval-based calculation for demo
                # In production, use a proper expression parser
                formula = rule.calculation_formula.replace(
                    "base_price",
                    str(calculated_price)
                )
                calculated_price = Decimal(str(eval(formula)))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Price calculation failed: {str(e)}"
                )

        return calculated_price
