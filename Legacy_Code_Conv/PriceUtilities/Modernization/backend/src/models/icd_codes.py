"""
ICD Code Model
Version: 1.0.0
Last Updated: 2025-01-12

This module defines the ICD code models for the pricing system.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from core.database import Base
from core.models import AuditMixin

# Association table for ICD codes and price list items
icd_price_list_association = Table(
    'icd_price_list_items',
    Base.metadata,
    Column('icd_code_id', Integer, ForeignKey('icd_codes.id'), primary_key=True),
    Column('price_list_item_id', Integer, ForeignKey('price_list_items.id'), primary_key=True)
)

class ICDCode(Base, AuditMixin):
    """
    Represents an ICD-9/10 code in the system.
    """
    __tablename__ = 'icd_codes'

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, unique=True)
    description = Column(String(500), nullable=False)
    version = Column(String(10), nullable=False)  # ICD-9 or ICD-10
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    # Relationships
    price_list_items = relationship(
        "PriceListItem",
        secondary=icd_price_list_association,
        backref="icd_codes"
    )
    mappings = relationship("ICDCodeMapping", back_populates="source_code")

    def __repr__(self):
        return f"<ICDCode(code='{self.code}', version='{self.version}')>"

class ICDCodeMapping(Base, AuditMixin):
    """
    Maps relationships between ICD codes (e.g., ICD-9 to ICD-10 mappings).
    """
    __tablename__ = 'icd_code_mappings'

    id = Column(Integer, primary_key=True)
    source_code_id = Column(Integer, ForeignKey('icd_codes.id'), nullable=False)
    target_code_id = Column(Integer, ForeignKey('icd_codes.id'), nullable=False)
    mapping_type = Column(String(50), nullable=False)  # e.g., 'exact', 'approximate'
    notes = Column(String(500))
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    # Relationships
    source_code = relationship("ICDCode", foreign_keys=[source_code_id], back_populates="mappings")
    target_code = relationship("ICDCode", foreign_keys=[target_code_id])

    def __repr__(self):
        return f"<ICDCodeMapping(source='{self.source_code_id}', target='{self.target_code_id}')>"
