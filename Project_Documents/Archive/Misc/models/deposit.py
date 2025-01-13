"""Deposit models module."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class Deposit(Base):
    """Model for deposits."""
    
    __tablename__ = 'deposits'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    deposit_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(String(500))
    metadata = Column(JSONB)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="deposits")
    order = relationship("Order", back_populates="deposits")
    line_items = relationship("DepositLineItem", back_populates="deposit")

    def __repr__(self):
        return f"<Deposit(id={self.id}, customer_id={self.customer_id}, amount={self.amount})>"

class DepositLineItem(Base):
    """Model for deposit line items."""
    
    __tablename__ = 'deposit_line_items'

    id = Column(Integer, primary_key=True)
    deposit_id = Column(Integer, ForeignKey('deposits.id'), nullable=False)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    amount = Column(Float, nullable=False)
    notes = Column(String(500))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    deposit = relationship("Deposit", back_populates="line_items")
    invoice = relationship("Invoice", back_populates="deposit_line_items")

    def __repr__(self):
        return f"<DepositLineItem(id={self.id}, deposit_id={self.deposit_id}, amount={self.amount})>"
