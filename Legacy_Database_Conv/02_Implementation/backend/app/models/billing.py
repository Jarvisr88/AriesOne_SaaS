"""
Billing domain models for AriesOne SaaS application.
This module implements the core billing functionality including
invoices, claims, payments, and financial transactions.
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, ForeignKey, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.sql import func

from .base import Base

class DocumentType(str, Enum):
    """Billing document types."""
    INVOICE = "Invoice"
    RENTAL_INVOICE = "RentalInvoice"
    CLAIM = "Claim"
    CREDIT_MEMO = "CreditMemo"

class DocumentStatus(str, Enum):
    """Billing document status types."""
    DRAFT = "Draft"
    PENDING = "Pending"
    SUBMITTED = "Submitted"
    PAID = "Paid"
    PARTIAL = "Partial"
    VOID = "Void"

class PaymentMethod(str, Enum):
    """Payment method types."""
    CASH = "Cash"
    CHECK = "Check"
    CREDIT_CARD = "CreditCard"
    ACH = "ACH"
    INSURANCE = "Insurance"

class PaymentStatus(str, Enum):
    """Payment status types."""
    PENDING = "Pending"
    AUTHORIZED = "Authorized"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"
    VOIDED = "Voided"

class ClaimStatus(str, Enum):
    """Insurance claim status types."""
    DRAFT = "Draft"
    READY = "Ready"
    SUBMITTED = "Submitted"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    PAID = "Paid"
    DENIED = "Denied"

class BaseBillingDocument(Base):
    """
    Abstract base class for billing documents.
    Provides common attributes and methods for all billing types.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_number = Column(String(50), unique=True, nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    document_date = Column(Date, nullable=False)
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)
    
    # References
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    
    # Amounts
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Insurance
    insurance_id = Column(Integer, ForeignKey('insurance.id'))
    authorization_number = Column(String(50))
    
    # Notes
    internal_notes = Column(String(1000))
    customer_notes = Column(String(1000))
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Common relationships
    customer = relationship("Customer")
    order = relationship("Order")
    insurance = relationship("Insurance")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

class Invoice(BaseBillingDocument):
    """
    Invoice for sales and services.
    """
    __tablename__ = 'invoices'

    # Additional fields
    due_date = Column(Date)
    payment_terms = Column(String(50))
    
    # Insurance billing
    insurance_billed = Column(Boolean, default=False)
    insurance_amount = Column(Numeric(10, 2), default=0)
    patient_amount = Column(Numeric(10, 2), default=0)
    
    # Relationships
    items = relationship("InvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")

    def __repr__(self):
        return f"<Invoice {self.document_number}: {self.total_amount}>"

class RentalInvoice(BaseBillingDocument):
    """
    Invoice for rental billing.
    """
    __tablename__ = 'rental_invoices'

    # Rental specific fields
    rental_period_start = Column(Date, nullable=False)
    rental_period_end = Column(Date, nullable=False)
    recurring_frequency = Column(String(20), nullable=False)
    next_bill_date = Column(Date)
    
    # Insurance coverage
    coverage_start = Column(Date)
    coverage_end = Column(Date)
    
    # Relationships
    items = relationship("RentalInvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="rental_invoice")

    def __repr__(self):
        return f"<RentalInvoice {self.document_number}: {self.total_amount}>"

class InvoiceItem(Base):
    """
    Line items for invoices.
    """
    __tablename__ = 'invoice_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    
    # Quantities and amounts
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Insurance billing
    hcpcs_code = Column(String(20))
    diagnosis_code = Column(String(20))
    insurance_amount = Column(Numeric(10, 2), default=0)
    patient_amount = Column(Numeric(10, 2), default=0)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    item = relationship("InventoryItem")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<InvoiceItem {self.id}: {self.total_amount}>"

class RentalInvoiceItem(Base):
    """
    Line items for rental invoices.
    """
    __tablename__ = 'rental_invoice_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('rental_invoices.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'))
    
    # Rental details
    rental_start = Column(Date, nullable=False)
    rental_end = Column(Date, nullable=False)
    rental_rate = Column(Numeric(10, 2), nullable=False)
    
    # Amounts
    quantity = Column(Integer, nullable=False, default=1)
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Insurance billing
    hcpcs_code = Column(String(20))
    diagnosis_code = Column(String(20))
    insurance_amount = Column(Numeric(10, 2), default=0)
    patient_amount = Column(Numeric(10, 2), default=0)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    invoice = relationship("RentalInvoice", back_populates="items")
    item = relationship("InventoryItem")
    serial_number = relationship("SerialNumber")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<RentalInvoiceItem {self.id}: {self.total_amount}>"

class Payment(Base):
    """
    Payment transactions.
    """
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_number = Column(String(50), unique=True, nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # References
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    rental_invoice_id = Column(Integer, ForeignKey('rental_invoices.id'))
    
    # Amounts
    amount = Column(Numeric(10, 2), nullable=False)
    
    # Payment details
    reference_number = Column(String(50))
    authorization_code = Column(String(50))
    payment_gateway_id = Column(String(100))
    
    # Notes
    notes = Column(String(500))
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer")
    invoice = relationship("Invoice", back_populates="payments")
    rental_invoice = relationship("RentalInvoice", back_populates="payments")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<Payment {self.payment_number}: {self.amount}>"

class Claim(BaseBillingDocument):
    """
    Insurance claims.
    """
    __tablename__ = 'claims'

    # Claim specific fields
    claim_number = Column(String(50), unique=True, nullable=False)
    claim_status = Column(SQLEnum(ClaimStatus), nullable=False, default=ClaimStatus.DRAFT)
    
    # Payer information
    payer_id = Column(Integer, ForeignKey('insurance.id'), nullable=False)
    subscriber_id = Column(String(50))
    group_number = Column(String(50))
    
    # Claim details
    service_start_date = Column(Date)
    service_end_date = Column(Date)
    place_of_service = Column(String(20))
    
    # Response
    payer_claim_number = Column(String(50))
    adjudication_date = Column(Date)
    paid_amount = Column(Numeric(10, 2))
    denied_amount = Column(Numeric(10, 2))
    adjustment_amount = Column(Numeric(10, 2))
    patient_responsibility = Column(Numeric(10, 2))
    
    # Relationships
    items = relationship("ClaimItem", back_populates="claim")
    payer = relationship("Insurance", foreign_keys=[payer_id])

    def __repr__(self):
        return f"<Claim {self.claim_number}: {self.total_amount}>"

class ClaimItem(Base):
    """
    Line items for insurance claims.
    """
    __tablename__ = 'claim_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(Integer, ForeignKey('claims.id'), nullable=False)
    
    # Service information
    service_date = Column(Date, nullable=False)
    hcpcs_code = Column(String(20), nullable=False)
    diagnosis_code = Column(String(20))
    modifier_1 = Column(String(2))
    modifier_2 = Column(String(2))
    modifier_3 = Column(String(2))
    modifier_4 = Column(String(2))
    
    # Amounts
    quantity = Column(Integer, nullable=False, default=1)
    charge_amount = Column(Numeric(10, 2), nullable=False)
    allowed_amount = Column(Numeric(10, 2))
    paid_amount = Column(Numeric(10, 2))
    adjustment_amount = Column(Numeric(10, 2))
    patient_responsibility = Column(Numeric(10, 2))
    
    # Response
    status_code = Column(String(20))
    rejection_reason = Column(String(200))
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    claim = relationship("Claim", back_populates="items")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<ClaimItem {self.id}: {self.charge_amount}>"
