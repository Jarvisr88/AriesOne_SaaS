"""
Price management forms using FastAPI and Pydantic.
"""
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, validator, Field
from fastapi import Form, HTTPException, Depends
from ...repositories.price_repository import PriceRepository
from ...repositories.models import PriceList, PriceListItem

class PriceListForm(BaseModel):
    """Price list form with validation."""
    name: str
    description: Optional[str]
    company_id: int
    effective_date: date
    expiration_date: Optional[date]
    is_active: bool = True

    @validator('name')
    def name_not_empty(cls, v):
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('expiration_date')
    def valid_date_range(cls, v, values):
        """Validate expiration date is after effective date."""
        if v and 'effective_date' in values and v <= values['effective_date']:
            raise ValueError('Expiration date must be after effective date')
        return v

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: Optional[str] = Form(None),
        company_id: int = Form(...),
        effective_date: date = Form(...),
        expiration_date: Optional[date] = Form(None),
        is_active: bool = Form(True)
    ):
        """Convert form data to model."""
        return cls(
            name=name,
            description=description,
            company_id=company_id,
            effective_date=effective_date,
            expiration_date=expiration_date,
            is_active=is_active
        )

class PriceListItemForm(BaseModel):
    """Price list item form."""
    price_list_id: int
    item_code: str
    description: Optional[str]
    unit_price: Decimal = Field(..., ge=0)
    minimum_quantity: int = Field(1, ge=1)
    maximum_quantity: Optional[int] = Field(None, ge=1)
    is_active: bool = True

    @validator('item_code')
    def item_code_format(cls, v):
        """Validate item code format."""
        if not v.strip():
            raise ValueError('Item code cannot be empty')
        return v.strip().upper()

    @validator('maximum_quantity')
    def valid_quantity_range(cls, v, values):
        """Validate quantity range."""
        if v and 'minimum_quantity' in values and v < values['minimum_quantity']:
            raise ValueError('Maximum quantity must be greater than minimum quantity')
        return v

    @classmethod
    def as_form(
        cls,
        price_list_id: int = Form(...),
        item_code: str = Form(...),
        description: Optional[str] = Form(None),
        unit_price: Decimal = Form(...),
        minimum_quantity: int = Form(1),
        maximum_quantity: Optional[int] = Form(None),
        is_active: bool = Form(True)
    ):
        """Convert form data to model."""
        return cls(
            price_list_id=price_list_id,
            item_code=item_code,
            description=description,
            unit_price=unit_price,
            minimum_quantity=minimum_quantity,
            maximum_quantity=maximum_quantity,
            is_active=is_active
        )

class BulkPriceUpdateForm(BaseModel):
    """Bulk price update form."""
    price_list_id: int
    items: List[Dict[str, Decimal]]  # List of {item_code: new_price}
    adjustment_type: str = Field(..., regex='^(fixed|percentage)$')
    adjustment_value: Decimal

    @validator('adjustment_value')
    def valid_adjustment(cls, v, values):
        """Validate adjustment value."""
        if values.get('adjustment_type') == 'percentage':
            if v <= -100:
                raise ValueError('Percentage adjustment cannot be -100% or less')
        elif v <= 0:
            raise ValueError('Fixed adjustment must be positive')
        return v

class PriceManager:
    """Handle price management operations."""
    
    def __init__(self, database):
        self.database = database
        self.price_repository = PriceRepository(database)

    async def create_price_list(
        self,
        form_data: PriceListForm,
        created_by: str
    ) -> PriceList:
        """Create new price list."""
        # Check if name exists for company
        existing = await self.price_repository.get_by_name_and_company(
            form_data.name,
            form_data.company_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Price list name already exists for this company"
            )

        return await self.price_repository.create_price_list(
            name=form_data.name,
            description=form_data.description,
            company_id=form_data.company_id,
            effective_date=form_data.effective_date,
            expiration_date=form_data.expiration_date,
            is_active=form_data.is_active,
            created_by=created_by
        )

    async def update_price_list(
        self,
        price_list_id: int,
        form_data: PriceListForm,
        updated_by: str
    ) -> PriceList:
        """Update price list details."""
        # Check if price list exists
        price_list = await self.price_repository.get_price_list(price_list_id)
        if not price_list:
            raise HTTPException(status_code=404, detail="Price list not found")

        # Check if name exists for company (excluding current price list)
        existing = await self.price_repository.get_by_name_and_company(
            form_data.name,
            form_data.company_id,
            exclude_id=price_list_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Price list name already exists for this company"
            )

        return await self.price_repository.update_price_list(
            price_list_id=price_list_id,
            name=form_data.name,
            description=form_data.description,
            effective_date=form_data.effective_date,
            expiration_date=form_data.expiration_date,
            is_active=form_data.is_active,
            updated_by=updated_by
        )

    async def add_price_list_item(
        self,
        form_data: PriceListItemForm,
        created_by: str
    ) -> PriceListItem:
        """Add item to price list."""
        # Check if price list exists
        price_list = await self.price_repository.get_price_list(form_data.price_list_id)
        if not price_list:
            raise HTTPException(status_code=404, detail="Price list not found")

        # Check if item code exists in price list
        existing = await self.price_repository.get_item_by_code(
            form_data.price_list_id,
            form_data.item_code
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Item code already exists in this price list"
            )

        return await self.price_repository.create_price_list_item(
            price_list_id=form_data.price_list_id,
            item_code=form_data.item_code,
            description=form_data.description,
            unit_price=form_data.unit_price,
            minimum_quantity=form_data.minimum_quantity,
            maximum_quantity=form_data.maximum_quantity,
            is_active=form_data.is_active,
            created_by=created_by
        )

    async def update_price_list_item(
        self,
        item_id: int,
        form_data: PriceListItemForm,
        updated_by: str
    ) -> PriceListItem:
        """Update price list item."""
        # Check if item exists
        item = await self.price_repository.get_price_list_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Price list item not found")

        # Check if item code exists in price list (excluding current item)
        existing = await self.price_repository.get_item_by_code(
            form_data.price_list_id,
            form_data.item_code,
            exclude_id=item_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Item code already exists in this price list"
            )

        return await self.price_repository.update_price_list_item(
            item_id=item_id,
            item_code=form_data.item_code,
            description=form_data.description,
            unit_price=form_data.unit_price,
            minimum_quantity=form_data.minimum_quantity,
            maximum_quantity=form_data.maximum_quantity,
            is_active=form_data.is_active,
            updated_by=updated_by
        )

    async def bulk_update_prices(
        self,
        form_data: BulkPriceUpdateForm,
        updated_by: str
    ) -> List[PriceListItem]:
        """Bulk update prices in a price list."""
        # Check if price list exists
        price_list = await self.price_repository.get_price_list(form_data.price_list_id)
        if not price_list:
            raise HTTPException(status_code=404, detail="Price list not found")

        updated_items = []
        for item_code, new_price in form_data.items.items():
            item = await self.price_repository.get_item_by_code(
                form_data.price_list_id,
                item_code
            )
            if item:
                # Calculate new price based on adjustment type
                if form_data.adjustment_type == 'percentage':
                    adjustment = (item.unit_price * form_data.adjustment_value) / 100
                else:
                    adjustment = form_data.adjustment_value

                new_price = item.unit_price + adjustment
                if new_price <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Adjustment would result in zero or negative price for item {item_code}"
                    )

                updated_item = await self.price_repository.update_price_list_item(
                    item_id=item.id,
                    unit_price=new_price,
                    updated_by=updated_by
                )
                updated_items.append(updated_item)

        return updated_items
