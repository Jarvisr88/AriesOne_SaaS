"""
Models for purchase order management.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Base item model."""
    barcode: str = Field(
        ...,
        description="Item barcode"
    )
    quantity: int = Field(
        ...,
        description="Item quantity",
        gt=0
    )
    unit_price: Decimal = Field(
        ...,
        description="Unit price",
        gt=Decimal(0)
    )
    description: Optional[str] = Field(
        None,
        description="Item description"
    )


class ItemCreate(ItemBase):
    """Item creation model."""
    pass


class ItemUpdate(BaseModel):
    """Item update model."""
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=Decimal(0))
    description: Optional[str] = None


class Item(ItemBase):
    """Item model."""
    id: int = Field(..., description="Item identifier")
    purchase_order_id: int = Field(
        ...,
        description="Purchase order identifier"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Update timestamp"
    )

    class Config:
        """Pydantic config."""
        orm_mode = True


class PurchaseOrderBase(BaseModel):
    """Base purchase order model."""
    vendor_id: int = Field(
        ...,
        description="Vendor identifier"
    )
    order_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Order date"
    )
    expected_date: Optional[datetime] = Field(
        None,
        description="Expected delivery date"
    )
    notes: Optional[str] = Field(
        None,
        description="Order notes"
    )


class PurchaseOrderCreate(PurchaseOrderBase):
    """Purchase order creation model."""
    items: List[ItemCreate] = Field(
        ...,
        description="Order items"
    )


class PurchaseOrderUpdate(BaseModel):
    """Purchase order update model."""
    expected_date: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseOrder(PurchaseOrderBase):
    """Purchase order model."""
    id: int = Field(..., description="Order identifier")
    status: str = Field(..., description="Order status")
    total_amount: Decimal = Field(
        ...,
        description="Total order amount"
    )
    items: List[Item] = Field(..., description="Order items")
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Update timestamp"
    )
    created_by: str = Field(..., description="Creator")
    updated_by: str = Field(..., description="Updater")

    class Config:
        """Pydantic config."""
        orm_mode = True
