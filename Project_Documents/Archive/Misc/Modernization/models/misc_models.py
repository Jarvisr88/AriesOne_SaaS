"""Models for miscellaneous operations including deposits, claims, and purchase orders."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CREDIT_CARD = 'credit_card'
    CHECK = 'check'
    CASH = 'cash'
    BANK_TRANSFER = 'bank_transfer'
    OTHER = 'other'


class DepositStatus(str, Enum):
    """Deposit status enumeration."""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    VOIDED = 'voided'


class DepositCreate(BaseModel):
    """Request model for creating deposit."""
    customer_id: int = Field(..., description="Customer identifier")
    order_id: Optional[int] = Field(None, description="Associated order ID")
    amount: Decimal = Field(..., description="Deposit amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    reference: Optional[str] = Field(None, description="Payment reference")
    notes: Optional[str] = Field(None, description="Additional notes")

    @validator('amount')
    def validate_amount(cls, v):
        """Validate deposit amount."""
        if v <= 0:
            raise ValueError("Deposit amount must be positive")
        return v


class DepositResponse(BaseModel):
    """Response model for deposit operations."""
    id: int = Field(..., description="Deposit identifier")
    customer_id: int = Field(..., description="Customer identifier")
    order_id: Optional[int] = Field(None, description="Associated order ID")
    amount: Decimal = Field(..., description="Deposit amount")
    payment_method: PaymentMethod = Field(..., description="Payment method")
    reference: Optional[str] = Field(None, description="Payment reference")
    status: DepositStatus = Field(..., description="Deposit status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class DepositUpdate(BaseModel):
    """Model for updating deposit status."""
    status: DepositStatus = Field(..., description="New status")
    reason: Optional[str] = Field(None, description="Status change reason")


class ClaimAction(str, Enum):
    """Claim action enumeration."""
    VOID = 'void'
    REPLACE = 'replace'


class ClaimStatus(str, Enum):
    """Claim status enumeration."""
    ACTIVE = 'active'
    VOIDED = 'voided'
    REPLACED = 'replaced'


class VoidSubmissionRequest(BaseModel):
    """Request model for voiding submission."""
    claim_number: str = Field(..., description="Claim number")
    action: ClaimAction = Field(..., description="Void action")
    reason: str = Field(..., description="Void reason")
    replacement_claim: Optional[str] = Field(None, description="Replacement claim number")

    @validator('claim_number')
    def validate_claim_number(cls, v):
        """Validate claim number format."""
        if not re.match(r'^[A-Z0-9]{6,12}$', v):
            raise ValueError("Invalid claim number format")
        return v

    @validator('replacement_claim')
    def validate_replacement(cls, v, values):
        """Validate replacement claim if action is replace."""
        if values.get('action') == ClaimAction.REPLACE and not v:
            raise ValueError("Replacement claim required for replace action")
        return v


class VoidSubmissionResponse(BaseModel):
    """Response model for void submission."""
    claim_number: str = Field(..., description="Claim number")
    action: ClaimAction = Field(..., description="Void action")
    status: ClaimStatus = Field(..., description="Claim status")
    processed_at: datetime = Field(..., description="Processing timestamp")
    replacement_claim: Optional[str] = Field(None, description="Replacement claim number")
    reason: str = Field(..., description="Void reason")


class OrderItemStatus(str, Enum):
    """Order item status enumeration."""
    PENDING = 'pending'
    PARTIAL = 'partial'
    RECEIVED = 'received'
    CANCELLED = 'cancelled'


class OrderItem(BaseModel):
    """Order item model."""
    id: int = Field(..., description="Item identifier")
    order_id: int = Field(..., description="Order identifier")
    product_id: int = Field(..., description="Product identifier")
    barcode: str = Field(..., description="Product barcode")
    quantity: int = Field(..., description="Ordered quantity")
    received_quantity: int = Field(..., description="Received quantity")
    status: OrderItemStatus = Field(..., description="Item status")

    @validator('quantity', 'received_quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive."""
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class ScanRequest(BaseModel):
    """Request model for barcode scan."""
    barcode: str = Field(..., description="Product barcode")
    quantity: int = Field(1, description="Scan quantity")

    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate scan quantity."""
        if v <= 0:
            raise ValueError("Scan quantity must be positive")
        return v


class ScanResponse(BaseModel):
    """Response model for barcode scan."""
    item: OrderItem = Field(..., description="Updated order item")
    message: str = Field(..., description="Status message")
    status: str = Field(..., description="Scan status")


class OrderSummary(BaseModel):
    """Summary model for purchase order."""
    id: int = Field(..., description="Order identifier")
    total_items: int = Field(..., description="Total number of items")
    received_items: int = Field(..., description="Number of received items")
    completion_percentage: float = Field(..., description="Order completion percentage")
    status: str = Field(..., description="Order status")
    last_updated: datetime = Field(..., description="Last update timestamp")
