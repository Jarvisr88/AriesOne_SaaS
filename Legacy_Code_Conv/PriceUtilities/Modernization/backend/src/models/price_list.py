"""
Price List Model
Version: 1.0.0
Last Updated: 2025-01-12

This module defines the PriceList and related models for the pricing system.
"""
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base
from core.models import AuditMixin

class PriceList(Base, AuditMixin):
    """
    Represents a price list in the system.
    """
    __tablename__ = 'price_lists'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime)
    items = relationship("PriceListItem", back_populates="price_list", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PriceList(id={self.id}, name='{self.name}')>"

class PriceListItem(Base, AuditMixin):
    """
    Represents an item in a price list with rental and sale prices.
    """
    __tablename__ = 'price_list_items'

    id = Column(Integer, primary_key=True)
    price_list_id = Column(Integer, ForeignKey('price_lists.id'), nullable=False)
    billing_code = Column(String(20), nullable=False)
    description = Column(String(500))
    
    # Rental prices
    rent_allowable_price = Column(Numeric(10, 2), nullable=False)
    rent_billable_price = Column(Numeric(10, 2), nullable=False)
    
    # Sale prices
    sale_allowable_price = Column(Numeric(10, 2), nullable=False)
    sale_billable_price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    price_list = relationship("PriceList", back_populates="items")
    price_history = relationship("PriceHistory", back_populates="price_list_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PriceListItem(id={self.id}, billing_code='{self.billing_code}')>"

class PriceHistory(Base, AuditMixin):
    """
    Tracks historical changes to prices.
    """
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True)
    price_list_item_id = Column(Integer, ForeignKey('price_list_items.id'), nullable=False)
    change_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Previous prices
    prev_rent_allowable = Column(Numeric(10, 2))
    prev_rent_billable = Column(Numeric(10, 2))
    prev_sale_allowable = Column(Numeric(10, 2))
    prev_sale_billable = Column(Numeric(10, 2))
    
    # New prices
    new_rent_allowable = Column(Numeric(10, 2))
    new_rent_billable = Column(Numeric(10, 2))
    new_sale_allowable = Column(Numeric(10, 2))
    new_sale_billable = Column(Numeric(10, 2))
    
    # Change metadata
    change_reason = Column(String(500))
    change_type = Column(String(50))  # e.g., 'manual', 'bulk_update', 'system'
    
    # Relationships
    price_list_item = relationship("PriceListItem", back_populates="price_history")
