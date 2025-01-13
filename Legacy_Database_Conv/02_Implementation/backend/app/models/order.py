"""
Order domain models for AriesOne SaaS application.
This module contains SQLAlchemy models for order-related entities including
orders, order details, and serial transactions.
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class OrderStatus(str, Enum):
    """Order status types."""
    DRAFT = "Draft"
    PENDING = "Pending"
    APPROVED = "Approved"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    ON_HOLD = "On Hold"

class OrderType(str, Enum):
    """Order types."""
    SALE = "Sale"
    RENTAL = "Rental"
    REPAIR = "Repair"
    EXCHANGE = "Exchange"
    RETURN = "Return"

class Order(Base):
    """
    Order information.
    Maps to the modernized version of tbl_order.
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Order Classification
    order_type = Column(SQLEnum(OrderType), nullable=False)
    order_status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.DRAFT)
    priority = Column(Integer, default=3)
    
    # Dates
    order_date = Column(Date, nullable=False, default=func.current_date())
    required_date = Column(Date)
    ship_date = Column(Date)
    delivery_date = Column(Date)
    pickup_date = Column(Date)
    
    # Locations
    location_id = Column(Integer, ForeignKey('locations.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    
    # Medical Information
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    diagnosis_code = Column(String(8), ForeignKey('icd10_codes.code'))
    
    # Financial Information
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Insurance Information
    insurance_id = Column(Integer, ForeignKey('customer_insurance.id'))
    authorization_number = Column(String(50))
    authorization_start_date = Column(Date)
    authorization_end_date = Column(Date)
    
    # Notes
    special_instructions = Column(String(500))
    internal_notes = Column(String(500))
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    location = relationship("Location")
    warehouse = relationship("Warehouse")
    doctor = relationship("Doctor")
    facility = relationship("Facility")
    diagnosis = relationship("ICD10Code")
    insurance = relationship("CustomerInsurance")
    details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")
    serial_transactions = relationship("SerialTransaction", back_populates="order")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<Order {self.order_number}: {self.order_type} - {self.order_status}>"

class OrderDetail(Base):
    """
    Order line item details.
    Maps to the modernized version of tbl_orderdetails.
    """
    __tablename__ = 'order_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    
    # Item Details
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0.0)
    discount_percent = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    
    # Rental Information
    rental_frequency = Column(String(20))  # Daily, Weekly, Monthly
    rental_duration = Column(Integer)
    rental_start_date = Column(Date)
    rental_end_date = Column(Date)
    
    # Status
    status = Column(String(20), nullable=False, default='Pending')
    is_completed = Column(Boolean, default=False)
    completed_date = Column(Date)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="details")
    item = relationship("InventoryItem")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<OrderDetail {self.id}: {self.item_id} x {self.quantity}>"

class SerialTransaction(Base):
    """
    Serial number tracking for inventory items.
    Maps to the modernized version of tbl_serial_transaction.
    """
    __tablename__ = 'serial_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    order_detail_id = Column(Integer, ForeignKey('order_details.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    serial_number = Column(String(50), nullable=False)
    
    # Transaction Details
    transaction_type = Column(String(20), nullable=False)  # Delivery, Pickup, Exchange
    transaction_date = Column(Date, nullable=False)
    previous_serial_number = Column(String(50))  # For exchanges
    
    # Status
    status = Column(String(20), nullable=False, default='Active')
    is_returned = Column(Boolean, default=False)
    return_date = Column(Date)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="serial_transactions")
    order_detail = relationship("OrderDetail")
    item = relationship("InventoryItem")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<SerialTransaction {self.id}: {self.serial_number} - {self.transaction_type}>"

class OrderSurvey(Base):
    """
    Customer satisfaction surveys for orders.
    """
    __tablename__ = 'order_surveys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    
    # Survey Details
    survey_date = Column(Date, nullable=False)
    satisfaction_rating = Column(Integer)  # 1-5 scale
    delivery_rating = Column(Integer)  # 1-5 scale
    service_rating = Column(Integer)  # 1-5 scale
    comments = Column(String(1000))
    
    # Follow-up
    requires_followup = Column(Boolean, default=False)
    followup_notes = Column(String(500))
    followup_date = Column(Date)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<OrderSurvey {self.id}: Order {self.order_id}>"
