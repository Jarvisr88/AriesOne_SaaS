"""
Models for deposit management.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    WIRE_TRANSFER = "wire_transfer"
    ACH = "ach"


class DepositBase(BaseModel):
    """Base deposit model."""
    customer_id: int = Field(..., description="Customer identifier")
    order_id: int = Field(..., description="Order identifier")
    deposit_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Deposit date"
    )
    deposit_amount: Decimal = Field(
        ...,
        description="Deposit amount",
        gt=Decimal(0)
    )
    payment_method: PaymentMethod = Field(
        ...,
        description="Payment method"
    )
    notes: Optional[str] = Field(
        None,
        description="Deposit notes"
    )


class DepositCreate(DepositBase):
    """Deposit creation model."""
    pass


class DepositUpdate(BaseModel):
    """Deposit update model."""
    deposit_date: Optional[datetime] = None
    deposit_amount: Optional[Decimal] = Field(None, gt=Decimal(0))
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None


class Deposit(DepositBase):
    """Deposit model."""
    id: int = Field(..., description="Deposit identifier")
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
