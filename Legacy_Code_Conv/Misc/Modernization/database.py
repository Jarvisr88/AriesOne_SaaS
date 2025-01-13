"""
Database configuration and models.
"""
from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Enum,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .deposits.models import PaymentMethod
from .voids.models import VoidAction


Base = declarative_base()


class Deposit(Base):
    """Deposit database model."""
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    order_id = Column(Integer, nullable=False)
    deposit_date = Column(DateTime, nullable=False)
    deposit_amount = Column(
        Numeric(precision=10, scale=2),
        nullable=False
    )
    payment_method = Column(
        Enum(PaymentMethod),
        nullable=False
    )
    notes = Column(Text)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=False)


class Void(Base):
    """Void database model."""
    __tablename__ = "voids"

    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String(50), nullable=False)
    action = Column(Enum(VoidAction), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=False)


class PurchaseOrder(Base):
    """Purchase order database model."""
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, nullable=False)
    order_date = Column(DateTime, nullable=False)
    expected_date = Column(DateTime)
    notes = Column(Text)
    status = Column(String(20), nullable=False)
    total_amount = Column(
        Numeric(precision=10, scale=2),
        nullable=False
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=False)

    items = relationship("PurchaseOrderItem", back_populates="order")


class PurchaseOrderItem(Base):
    """Purchase order item database model."""
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        nullable=False
    )
    barcode = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(
        Numeric(precision=10, scale=2),
        nullable=False
    )
    description = Column(Text)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    order = relationship("PurchaseOrder", back_populates="items")
