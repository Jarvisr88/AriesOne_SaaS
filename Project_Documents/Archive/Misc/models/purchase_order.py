"""Purchase order models module."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class PurchaseOrder(Base):
    """Model for purchase orders."""
    
    __tablename__ = 'purchase_orders'

    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    order_number = Column(String(100), nullable=False, unique=True)
    status = Column(String(50), nullable=False, default='pending')
    total_amount = Column(Float, nullable=False)
    received_date = Column(DateTime)
    metadata = Column(JSONB)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")

    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, order_number={self.order_number}, status={self.status})>"

    def receive_items(self, received_items: List[dict]):
        """Process received items for the purchase order."""
        for item_data in received_items:
            item = next(
                (i for i in self.items if i.id == item_data['item_id']), 
                None
            )
            if item:
                item.received_quantity = item_data.get('quantity', 0)
                item.received_date = datetime.utcnow()
        
        # Update PO status if all items received
        if all(item.is_fully_received for item in self.items):
            self.status = 'received'
            self.received_date = datetime.utcnow()

class PurchaseOrderItem(Base):
    """Model for purchase order items."""
    
    __tablename__ = 'purchase_order_items'

    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    barcode = Column(String(100))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    received_quantity = Column(Integer, default=0)
    received_date = Column(DateTime)
    notes = Column(String(500))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")

    @property
    def is_fully_received(self) -> bool:
        """Check if item is fully received."""
        return self.received_quantity >= self.quantity

    def __repr__(self):
        return f"<PurchaseOrderItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
