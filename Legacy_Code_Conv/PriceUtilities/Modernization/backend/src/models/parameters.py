"""
Price Parameters Model
Version: 1.0.0
Last Updated: 2025-01-12

This module defines the pricing parameters and rules models.
"""
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from core.database import Base
from core.models import AuditMixin

class PriceParameter(Base, AuditMixin):
    """
    Represents a pricing parameter used in price calculations.
    """
    __tablename__ = 'price_parameters'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    parameter_type = Column(String(50), nullable=False)  # e.g., 'percentage', 'fixed', 'multiplier'
    value = Column(Numeric(10, 4), nullable=False)
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    
    # Additional configuration
    config = Column(JSON)  # Stores additional parameter-specific configuration
    
    # Relationships
    rules = relationship("PriceRule", back_populates="parameter")
    history = relationship("ParameterHistory", back_populates="parameter")

    def __repr__(self):
        return f"<PriceParameter(name='{self.name}', value={self.value})>"

class PriceRule(Base, AuditMixin):
    """
    Defines rules for applying pricing parameters.
    """
    __tablename__ = 'price_rules'

    id = Column(Integer, primary_key=True)
    parameter_id = Column(Integer, ForeignKey('price_parameters.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    rule_type = Column(String(50), nullable=False)  # e.g., 'markup', 'discount', 'adjustment'
    priority = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    
    # Rule conditions and actions
    conditions = Column(JSON)  # JSON object defining when rule applies
    actions = Column(JSON)     # JSON object defining what rule does
    
    # Relationships
    parameter = relationship("PriceParameter", back_populates="rules")

    def __repr__(self):
        return f"<PriceRule(name='{self.name}', type='{self.rule_type}')>"

class ParameterHistory(Base, AuditMixin):
    """
    Tracks historical changes to price parameters.
    """
    __tablename__ = 'parameter_history'

    id = Column(Integer, primary_key=True)
    parameter_id = Column(Integer, ForeignKey('price_parameters.id'), nullable=False)
    change_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Value changes
    previous_value = Column(Numeric(10, 4))
    new_value = Column(Numeric(10, 4))
    
    # Change metadata
    change_reason = Column(String(500))
    change_type = Column(String(50))  # e.g., 'manual', 'scheduled', 'system'
    
    # Previous configuration
    previous_config = Column(JSON)
    new_config = Column(JSON)
    
    # Relationships
    parameter = relationship("PriceParameter", back_populates="history")

    def __repr__(self):
        return f"<ParameterHistory(parameter_id={self.parameter_id}, date='{self.change_date}')>"
