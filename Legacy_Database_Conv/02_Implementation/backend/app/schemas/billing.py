"""
Pydantic schemas for billing domain.
Provides request and response validation for billing-related operations.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, constr, condecimal, conint, Field

from ..models.billing import (
    DocumentType, DocumentStatus, PaymentMethod,
    PaymentStatus, ClaimStatus
)

# Base schemas
class BillingDocumentBase(BaseModel):
    """Base schema for billing documents."""
    document_number: constr(min_length=1, max_length=50)
    document_type: DocumentType
    document_date: date
    status: DocumentStatus = DocumentStatus.DRAFT
    
    # References
    customer_id: int
    order_id: Optional[int] = None
    
    # Amounts
    subtotal: condecimal(ge=0, decimal_places=2)
    tax_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    discount_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    total_amount: condecimal(ge=0, decimal_places=2)
    
    # Insurance
    insurance_id: Optional[int] = None
    authorization_number: Optional[str] = None
    
    # Notes
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None

# Invoice schemas
class InvoiceItemBase(BaseModel):
    """Base schema for invoice items."""
    item_id: int
    quantity: conint(gt=0) = 1
    unit_price: condecimal(ge=0, decimal_places=2)
    tax_rate: condecimal(ge=0, le=100, decimal_places=2) = Decimal('0.00')
    tax_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    discount_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    total_amount: condecimal(ge=0, decimal_places=2)
    
    # Insurance billing
    hcpcs_code: Optional[str] = None
    diagnosis_code: Optional[str] = None
    insurance_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    patient_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')

class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating invoice items."""
    pass

class InvoiceItemUpdate(BaseModel):
    """Schema for updating invoice items."""
    quantity: Optional[conint(gt=0)] = None
    unit_price: Optional[condecimal(ge=0, decimal_places=2)] = None
    tax_rate: Optional[condecimal(ge=0, le=100, decimal_places=2)] = None
    discount_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    hcpcs_code: Optional[str] = None
    diagnosis_code: Optional[str] = None

class InvoiceItemResponse(InvoiceItemBase):
    """Schema for invoice item responses."""
    id: int
    invoice_id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

class InvoiceBase(BillingDocumentBase):
    """Base schema for invoices."""
    due_date: Optional[date] = None
    payment_terms: Optional[str] = None
    insurance_billed: bool = False
    insurance_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    patient_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')

class InvoiceCreate(InvoiceBase):
    """Schema for creating invoices."""
    items: List[InvoiceItemCreate]

class InvoiceUpdate(BaseModel):
    """Schema for updating invoices."""
    status: Optional[DocumentStatus] = None
    due_date: Optional[date] = None
    payment_terms: Optional[str] = None
    insurance_id: Optional[int] = None
    authorization_number: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None

class InvoiceResponse(InvoiceBase):
    """Schema for invoice responses."""
    id: int
    items: List[InvoiceItemResponse]
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Rental Invoice schemas
class RentalInvoiceItemBase(BaseModel):
    """Base schema for rental invoice items."""
    item_id: int
    serial_number_id: Optional[int] = None
    rental_start: date
    rental_end: date
    rental_rate: condecimal(ge=0, decimal_places=2)
    quantity: conint(gt=0) = 1
    tax_rate: condecimal(ge=0, le=100, decimal_places=2) = Decimal('0.00')
    tax_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    discount_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    total_amount: condecimal(ge=0, decimal_places=2)
    hcpcs_code: Optional[str] = None
    diagnosis_code: Optional[str] = None
    insurance_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')
    patient_amount: condecimal(ge=0, decimal_places=2) = Decimal('0.00')

class RentalInvoiceItemCreate(RentalInvoiceItemBase):
    """Schema for creating rental invoice items."""
    pass

class RentalInvoiceItemUpdate(BaseModel):
    """Schema for updating rental invoice items."""
    rental_end: Optional[date] = None
    rental_rate: Optional[condecimal(ge=0, decimal_places=2)] = None
    quantity: Optional[conint(gt=0)] = None
    tax_rate: Optional[condecimal(ge=0, le=100, decimal_places=2)] = None
    discount_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    hcpcs_code: Optional[str] = None
    diagnosis_code: Optional[str] = None

class RentalInvoiceItemResponse(RentalInvoiceItemBase):
    """Schema for rental invoice item responses."""
    id: int
    invoice_id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

class RentalInvoiceBase(BillingDocumentBase):
    """Base schema for rental invoices."""
    rental_period_start: date
    rental_period_end: date
    recurring_frequency: str
    next_bill_date: Optional[date] = None
    coverage_start: Optional[date] = None
    coverage_end: Optional[date] = None

class RentalInvoiceCreate(RentalInvoiceBase):
    """Schema for creating rental invoices."""
    items: List[RentalInvoiceItemCreate]

class RentalInvoiceUpdate(BaseModel):
    """Schema for updating rental invoices."""
    status: Optional[DocumentStatus] = None
    rental_period_end: Optional[date] = None
    next_bill_date: Optional[date] = None
    coverage_end: Optional[date] = None
    insurance_id: Optional[int] = None
    authorization_number: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None

class RentalInvoiceResponse(RentalInvoiceBase):
    """Schema for rental invoice responses."""
    id: int
    items: List[RentalInvoiceItemResponse]
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Payment schemas
class PaymentBase(BaseModel):
    """Base schema for payments."""
    payment_number: constr(min_length=1, max_length=50)
    payment_date: date
    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    customer_id: int
    invoice_id: Optional[int] = None
    rental_invoice_id: Optional[int] = None
    amount: condecimal(ge=0, decimal_places=2)
    reference_number: Optional[str] = None
    authorization_code: Optional[str] = None
    payment_gateway_id: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    """Schema for creating payments."""
    pass

class PaymentUpdate(BaseModel):
    """Schema for updating payments."""
    status: Optional[PaymentStatus] = None
    authorization_code: Optional[str] = None
    payment_gateway_id: Optional[str] = None
    notes: Optional[str] = None

class PaymentResponse(PaymentBase):
    """Schema for payment responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Claim schemas
class ClaimItemBase(BaseModel):
    """Base schema for claim items."""
    service_date: date
    hcpcs_code: constr(min_length=1, max_length=20)
    diagnosis_code: Optional[str] = None
    modifier_1: Optional[constr(min_length=2, max_length=2)] = None
    modifier_2: Optional[constr(min_length=2, max_length=2)] = None
    modifier_3: Optional[constr(min_length=2, max_length=2)] = None
    modifier_4: Optional[constr(min_length=2, max_length=2)] = None
    quantity: conint(gt=0) = 1
    charge_amount: condecimal(ge=0, decimal_places=2)
    allowed_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    paid_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    adjustment_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    patient_responsibility: Optional[condecimal(ge=0, decimal_places=2)] = None
    status_code: Optional[str] = None
    rejection_reason: Optional[str] = None

class ClaimItemCreate(ClaimItemBase):
    """Schema for creating claim items."""
    pass

class ClaimItemUpdate(BaseModel):
    """Schema for updating claim items."""
    allowed_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    paid_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    adjustment_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    patient_responsibility: Optional[condecimal(ge=0, decimal_places=2)] = None
    status_code: Optional[str] = None
    rejection_reason: Optional[str] = None

class ClaimItemResponse(ClaimItemBase):
    """Schema for claim item responses."""
    id: int
    claim_id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

class ClaimBase(BillingDocumentBase):
    """Base schema for claims."""
    claim_number: constr(min_length=1, max_length=50)
    claim_status: ClaimStatus = ClaimStatus.DRAFT
    payer_id: int
    subscriber_id: Optional[str] = None
    group_number: Optional[str] = None
    service_start_date: Optional[date] = None
    service_end_date: Optional[date] = None
    place_of_service: Optional[str] = None
    payer_claim_number: Optional[str] = None
    adjudication_date: Optional[date] = None
    paid_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    denied_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    adjustment_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    patient_responsibility: Optional[condecimal(ge=0, decimal_places=2)] = None

class ClaimCreate(ClaimBase):
    """Schema for creating claims."""
    items: List[ClaimItemCreate]

class ClaimUpdate(BaseModel):
    """Schema for updating claims."""
    claim_status: Optional[ClaimStatus] = None
    payer_claim_number: Optional[str] = None
    adjudication_date: Optional[date] = None
    paid_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    denied_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    adjustment_amount: Optional[condecimal(ge=0, decimal_places=2)] = None
    patient_responsibility: Optional[condecimal(ge=0, decimal_places=2)] = None

class ClaimResponse(ClaimBase):
    """Schema for claim responses."""
    id: int
    items: List[ClaimItemResponse]
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True
