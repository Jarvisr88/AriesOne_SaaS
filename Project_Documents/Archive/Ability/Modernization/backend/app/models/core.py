from typing import Dict, List, Optional
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DeliveryStatus:
    """Delivery status enum"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class Delivery(Base):
    """Delivery model"""
    __tablename__ = "deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(
        Enum(
            DeliveryStatus.PENDING,
            DeliveryStatus.IN_PROGRESS,
            DeliveryStatus.DELIVERED,
            DeliveryStatus.CANCELLED,
            DeliveryStatus.FAILED,
            name="delivery_status"
        ),
        nullable=False
    )
    priority = Column(String(20), default="NORMAL")
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"))
    items = Column(JSONB)  # List of {item_id, quantity}
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    notes = Column(String(500))

    # Relationships
    vehicle = relationship("Vehicle", back_populates="deliveries")
    locations = relationship("Location", back_populates="delivery")
    route = relationship("Route", back_populates="delivery", uselist=False)
    destination = relationship(
        "Location",
        primaryjoin="and_(Delivery.id==Location.delivery_id, Location.is_destination==True)",
        uselist=False
    )

class Location(Base):
    """Location model"""
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id"))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    heading = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_destination = Column(Boolean, default=False)
    address = Column(JSONB)

    # Relationships
    delivery = relationship("Delivery", back_populates="locations")

class Route(Base):
    """Route model"""
    __tablename__ = "routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=False)
    path = Column(JSONB)  # List of [lat, lng] coordinates
    distance = Column(Float)  # Distance in meters
    duration = Column(Float)  # Duration in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    delivery = relationship("Delivery", back_populates="route")

class Vehicle(Base):
    """Vehicle model"""
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(20), default="AVAILABLE")
    capacity = Column(Float)  # Capacity in cubic meters
    max_weight = Column(Float)  # Maximum weight in kg
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    deliveries = relationship("Delivery", back_populates="vehicle")
    last_location = relationship(
        "Location",
        primaryjoin="and_(Vehicle.id==Delivery.vehicle_id, "
                   "Delivery.id==Location.delivery_id)",
        order_by="desc(Location.timestamp)",
        uselist=False
    )

class InventoryItem(Base):
    """Inventory item model"""
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    barcode = Column(String(100), unique=True)
    sku = Column(String(100), unique=True)
    quantity = Column(Integer, default=0)
    unit = Column(String(20))
    weight = Column(Float)  # Weight in kg
    volume = Column(Float)  # Volume in cubic meters
    category = Column(String(100))
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SyncQueue(Base):
    """Offline sync queue model"""
    __tablename__ = "sync_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)
    data = Column(JSONB, nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
