from typing import Optional, List
from datetime import datetime
import uuid
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Numeric, Boolean, Enum, Text, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base
from app.core.monitoring import metrics
from app.core.logging import logger

class AuditMixin:
    """Mixin for audit fields"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

class Transaction(Base, AuditMixin):
    """Financial transaction model"""
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum("DEPOSIT", "WITHDRAWAL", "TRANSFER", "PAYMENT", name="transaction_type"), nullable=False)
    status = Column(Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="transaction_status"), nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), nullable=False)
    description = Column(Text)
    reference = Column(String(50), unique=True)
    metadata = Column(JSONB)

    # Relationships
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    account = relationship("Account", back_populates="transactions")
    
    # Audit trail
    audit_trail = relationship("TransactionAudit", back_populates="transaction")

    __table_args__ = (
        Index("ix_transactions_account_created", account_id, created_at),
        Index("ix_transactions_status_created", status, created_at),
    )

    @validates("amount")
    def validate_amount(self, key, amount):
        """Validate transaction amount"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount

    @validates("currency")
    def validate_currency(self, key, currency):
        """Validate currency code"""
        if len(currency) != 3:
            raise ValueError("Invalid currency code")
        return currency.upper()

class Account(Base, AuditMixin):
    """Financial account model"""
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum("CHECKING", "SAVINGS", "CREDIT", name="account_type"), nullable=False)
    status = Column(Enum("ACTIVE", "FROZEN", "CLOSED", name="account_status"), nullable=False)
    balance = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    currency = Column(String(3), nullable=False)
    name = Column(String(100), nullable=False)
    number = Column(String(20), unique=True, nullable=False)

    # Relationships
    transactions = relationship("Transaction", back_populates="account")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="accounts")

    __table_args__ = (
        Index("ix_accounts_owner_type", owner_id, type),
        Index("ix_accounts_number", number, unique=True),
    )

    @validates("balance")
    def validate_balance(self, key, balance):
        """Validate account balance"""
        if isinstance(balance, str):
            balance = Decimal(balance)
        return balance

    @hybrid_property
    def available_balance(self):
        """Calculate available balance considering pending transactions"""
        pending_sum = sum(
            t.amount for t in self.transactions 
            if t.status == "PENDING" and t.type in ["WITHDRAWAL", "TRANSFER"]
        )
        return self.balance - pending_sum

class PurchaseOrder(Base, AuditMixin):
    """Purchase order model"""
    __tablename__ = "purchase_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number = Column(String(20), unique=True, nullable=False)
    status = Column(
        Enum("DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "COMPLETED", name="po_status"),
        nullable=False
    )
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    description = Column(Text)
    notes = Column(Text)
    metadata = Column(JSONB)

    # Relationships
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")
    approvals = relationship("PurchaseOrderApproval", back_populates="purchase_order")
    
    __table_args__ = (
        Index("ix_purchase_orders_vendor_status", vendor_id, status),
        Index("ix_purchase_orders_number", number, unique=True),
    )

    @validates("total_amount")
    def validate_total_amount(self, key, amount):
        """Validate purchase order amount"""
        if amount <= 0:
            raise ValueError("Total amount must be positive")
        return amount

class PurchaseOrderItem(Base):
    """Purchase order item model"""
    __tablename__ = "purchase_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(precision=10, scale=2), nullable=False)
    total_price = Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(Text)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")

    @validates("quantity")
    def validate_quantity(self, key, quantity):
        """Validate item quantity"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return quantity

class Claim(Base, AuditMixin):
    """Insurance claim model"""
    __tablename__ = "claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number = Column(String(20), unique=True, nullable=False)
    status = Column(
        Enum("SUBMITTED", "REVIEWING", "APPROVED", "REJECTED", "PAID", name="claim_status"),
        nullable=False
    )
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    service_date = Column(DateTime, nullable=False)
    diagnosis_codes = Column(JSONB)
    procedure_codes = Column(JSONB)
    notes = Column(Text)
    metadata = Column(JSONB)

    # Relationships
    documents = relationship("ClaimDocument", back_populates="claim")
    reviews = relationship("ClaimReview", back_populates="claim")
    payments = relationship("ClaimPayment", back_populates="claim")

    __table_args__ = (
        Index("ix_claims_patient_status", patient_id, status),
        Index("ix_claims_provider_status", provider_id, status),
        Index("ix_claims_number", number, unique=True),
    )

    @validates("amount")
    def validate_amount(self, key, amount):
        """Validate claim amount"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount

class TransactionAudit(Base):
    """Transaction audit trail model"""
    __tablename__ = "transaction_audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    action = Column(String(50), nullable=False)
    old_status = Column(String(50))
    new_status = Column(String(50))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSONB)

    # Relationships
    transaction = relationship("Transaction", back_populates="audit_trail")

    __table_args__ = (
        Index("ix_transaction_audits_transaction", transaction_id, timestamp),
    )

# Set up monitoring
def setup_model_monitoring():
    """Setup monitoring metrics for financial models"""
    metrics.transaction_count = metrics.counter(
        "financial_transactions_total",
        "Total number of financial transactions"
    )
    metrics.transaction_amount = metrics.gauge(
        "financial_transaction_amount",
        "Total amount of financial transactions"
    )
    metrics.account_balance = metrics.gauge(
        "financial_account_balance",
        "Current account balance"
    )
    metrics.purchase_order_count = metrics.counter(
        "financial_purchase_orders_total",
        "Total number of purchase orders"
    )
    metrics.claim_count = metrics.counter(
        "financial_claims_total",
        "Total number of insurance claims"
    )

# Initialize monitoring
setup_model_monitoring()
