"""
Inventory domain models for AriesOne SaaS application.
This module implements the core inventory management functionality including
items, serial numbers, warehouses, and kits.
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.sql import func

from .base import Base

class ItemType(str, Enum):
    """Item types in the system."""
    EQUIPMENT = "Equipment"
    SUPPLY = "Supply"
    KIT = "Kit"
    ACCESSORY = "Accessory"

class ItemStatus(str, Enum):
    """Item status types."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DISCONTINUED = "Discontinued"
    ON_HOLD = "On Hold"

class PricingModel(str, Enum):
    """Pricing model types."""
    SALE = "Sale"
    RENTAL = "Rental"
    BOTH = "Both"

class BaseInventoryItem(Base):
    """
    Abstract base class for inventory items.
    Provides common attributes and methods for all inventory types.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    item_type = Column(SQLEnum(ItemType), nullable=False)
    status = Column(SQLEnum(ItemStatus), nullable=False, default=ItemStatus.ACTIVE)
    
    # Classification
    category = Column(String(50))
    subcategory = Column(String(50))
    manufacturer = Column(String(100))
    model = Column(String(100))
    
    # Pricing
    pricing_model = Column(SQLEnum(PricingModel), nullable=False)
    sale_price = Column(Float)
    rental_price = Column(Float)
    cost = Column(Float)
    
    # Tracking
    requires_serial = Column(Boolean, default=False)
    requires_lot = Column(Boolean, default=False)
    is_billable = Column(Boolean, default=True)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Common relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

class InventoryItem(BaseInventoryItem):
    """
    Concrete implementation of inventory item.
    Maps to the modernized version of tbl_inventoryitem.
    """
    __tablename__ = 'inventory_items'

    # Additional fields specific to regular items
    hcpcs_code = Column(String(20))
    upc_code = Column(String(20))
    warranty_months = Column(Integer)
    
    # Reordering
    reorder_point = Column(Integer)
    reorder_quantity = Column(Integer)
    minimum_stock = Column(Integer)
    maximum_stock = Column(Integer)
    
    # Relationships
    stock_levels = relationship("StockLevel", back_populates="item")
    serial_numbers = relationship("SerialNumber", back_populates="item")
    kit_components = relationship("KitComponent", back_populates="component")

    def __repr__(self):
        return f"<InventoryItem {self.item_number}: {self.name}>"

class Kit(BaseInventoryItem):
    """
    Kit definition for bundled items.
    """
    __tablename__ = 'kits'

    # Additional fields specific to kits
    assembly_instructions = Column(String(1000))
    is_customizable = Column(Boolean, default=False)
    
    # Relationships
    components = relationship("KitComponent", back_populates="kit")

    def __repr__(self):
        return f"<Kit {self.item_number}: {self.name}>"

class KitComponent(Base):
    """
    Components that make up a kit.
    """
    __tablename__ = 'kit_components'

    id = Column(Integer, primary_key=True, autoincrement=True)
    kit_id = Column(Integer, ForeignKey('kits.id'), nullable=False)
    component_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    is_required = Column(Boolean, default=True)
    sequence = Column(Integer)
    notes = Column(String(500))
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    kit = relationship("Kit", back_populates="components")
    component = relationship("InventoryItem", back_populates="kit_components")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<KitComponent {self.kit_id} - {self.component_id}: {self.quantity}>"

class SerialNumber(Base):
    """
    Serial number tracking for equipment.
    """
    __tablename__ = 'serial_numbers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    serial_number = Column(String(50), unique=True, nullable=False)
    
    # Details
    manufacturer_serial = Column(String(50))
    manufacture_date = Column(Date)
    purchase_date = Column(Date)
    warranty_start = Column(Date)
    warranty_end = Column(Date)
    
    # Status
    status = Column(String(20), nullable=False, default='Available')
    condition = Column(String(20))
    location_id = Column(Integer, ForeignKey('locations.id'))
    last_inspection_date = Column(Date)
    next_inspection_date = Column(Date)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    item = relationship("InventoryItem", back_populates="serial_numbers")
    location = relationship("Location")
    maintenance_records = relationship("MaintenanceRecord", back_populates="serial_number")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<SerialNumber {self.serial_number}: {self.status}>"

class MaintenanceRecord(Base):
    """
    Maintenance history for serialized equipment.
    """
    __tablename__ = 'maintenance_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number_id = Column(Integer, ForeignKey('serial_numbers.id'), nullable=False)
    
    # Maintenance Details
    maintenance_type = Column(String(50), nullable=False)
    maintenance_date = Column(Date, nullable=False)
    performed_by = Column(String(100))
    cost = Column(Float)
    description = Column(String(500))
    resolution = Column(String(500))
    next_maintenance_date = Column(Date)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    serial_number = relationship("SerialNumber", back_populates="maintenance_records")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<MaintenanceRecord {self.id}: {self.maintenance_type}>"

class Warehouse(Base):
    """
    Warehouse/storage location information.
    """
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    
    # Location
    address1 = Column(String(100), nullable=False)
    address2 = Column(String(100))
    city = Column(String(50), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    
    # Contact
    phone = Column(String(20))
    email = Column(String(100))
    manager_id = Column(Integer, ForeignKey('users.id'))
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    stock_levels = relationship("StockLevel", back_populates="warehouse")
    manager = relationship("User", foreign_keys=[manager_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<Warehouse {self.code}: {self.name}>"

class StockLevel(Base):
    """
    Current stock levels by item and warehouse.
    """
    __tablename__ = 'stock_levels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    
    # Quantities
    quantity_on_hand = Column(Integer, nullable=False, default=0)
    quantity_allocated = Column(Integer, nullable=False, default=0)
    quantity_available = Column(Integer, nullable=False, default=0)
    quantity_on_order = Column(Integer, nullable=False, default=0)
    
    # Location
    bin_location = Column(String(20))
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    item = relationship("InventoryItem", back_populates="stock_levels")
    warehouse = relationship("Warehouse", back_populates="stock_levels")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<StockLevel {self.item_id}@{self.warehouse_id}: {self.quantity_available}>"
