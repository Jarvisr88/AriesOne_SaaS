"""
Base models for the AriesOne SaaS platform.
These models represent the core entities in the system.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base
from ..core.interfaces import IAuditableEntity

class AuditableModel(Base):
    """Base class for all auditable entities."""
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=False)

class User(AuditableModel):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="users")
    roles = relationship("UserRole", back_populates="user")

class Company(AuditableModel):
    """Company model for multi-tenant support."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="company")
    locations = relationship("Location", back_populates="company")
    price_lists = relationship("PriceList", back_populates="company")

class Location(AuditableModel):
    """Location model for company locations."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address_line1 = Column(String(100), nullable=False)
    address_line2 = Column(String(100))
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="locations")

class PriceList(AuditableModel):
    """Price list model for managing item prices."""
    __tablename__ = "price_lists"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Relationships
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="price_lists")
    items = relationship("PriceListItem", back_populates="price_list")

class PriceListItem(AuditableModel):
    """Price list item model for individual item prices."""
    __tablename__ = "price_list_items"

    id = Column(Integer, primary_key=True)
    item_code = Column(String(20), nullable=False)
    description = Column(String(255), nullable=False)
    unit_price = Column(Integer, nullable=False)  # Stored in cents
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    price_list_id = Column(Integer, ForeignKey("price_lists.id"), nullable=False)
    price_list = relationship("PriceList", back_populates="items")

class Role(AuditableModel):
    """Role model for user permissions."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role")

class UserRole(AuditableModel):
    """User-Role association model."""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")
