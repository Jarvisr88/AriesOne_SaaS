"""Purchase order service module."""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models.purchase_order import PurchaseOrder, PurchaseOrderItem

class PurchaseOrderService:
    """Service for handling purchase orders."""

    def __init__(self, db: Session):
        """Initialize the purchase order service."""
        self.db = db

    def create_purchase_order(
        self,
        vendor_id: int,
        order_number: str,
        items: List[Dict],
        metadata: Optional[dict] = None
    ) -> PurchaseOrder:
        """Create a new purchase order."""
        # Calculate total amount
        total_amount = sum(
            item['quantity'] * item['unit_price'] 
            for item in items
        )

        # Create purchase order
        po = PurchaseOrder(
            vendor_id=vendor_id,
            order_number=order_number,
            total_amount=total_amount,
            status='pending',
            metadata=metadata
        )
        self.db.add(po)
        self.db.flush()  # Get PO ID

        # Add items
        for item in items:
            po_item = PurchaseOrderItem(
                purchase_order_id=po.id,
                product_id=item['product_id'],
                barcode=item.get('barcode'),
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                notes=item.get('notes')
            )
            self.db.add(po_item)

        self.db.commit()
        return po

    def get_purchase_order(self, po_id: int) -> Optional[PurchaseOrder]:
        """Get a purchase order by ID."""
        return self.db.query(PurchaseOrder).filter(
            PurchaseOrder.id == po_id
        ).first()

    def get_purchase_orders_by_vendor(self, vendor_id: int) -> List[PurchaseOrder]:
        """Get all purchase orders for a vendor."""
        return self.db.query(PurchaseOrder).filter(
            PurchaseOrder.vendor_id == vendor_id
        ).all()

    def receive_items(
        self,
        po_id: int,
        received_items: List[Dict]
    ) -> Optional[PurchaseOrder]:
        """Process received items for a purchase order."""
        po = self.get_purchase_order(po_id)
        if not po or po.status == 'received':
            return None

        # Process received items
        po.receive_items(received_items)
        self.db.commit()
        return po

    def get_item_by_barcode(
        self,
        po_id: int,
        barcode: str
    ) -> Optional[PurchaseOrderItem]:
        """Get a purchase order item by barcode."""
        return self.db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.purchase_order_id == po_id,
            PurchaseOrderItem.barcode == barcode
        ).first()

    def update_item_quantity(
        self,
        item_id: int,
        received_quantity: int
    ) -> Optional[PurchaseOrderItem]:
        """Update received quantity for an item."""
        item = self.db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.id == item_id
        ).first()

        if not item:
            return None

        item.received_quantity = received_quantity
        item.received_date = datetime.utcnow()

        # Check if PO is fully received
        po = item.purchase_order
        if all(i.is_fully_received for i in po.items):
            po.status = 'received'
            po.received_date = datetime.utcnow()

        self.db.commit()
        return item

    def get_pending_orders(self) -> List[PurchaseOrder]:
        """Get all pending purchase orders."""
        return self.db.query(PurchaseOrder).filter(
            PurchaseOrder.status == 'pending'
        ).all()

    def get_received_orders(self) -> List[PurchaseOrder]:
        """Get all received purchase orders."""
        return self.db.query(PurchaseOrder).filter(
            PurchaseOrder.status == 'received'
        ).all()

    def cancel_purchase_order(self, po_id: int) -> Optional[PurchaseOrder]:
        """Cancel a purchase order."""
        po = self.get_purchase_order(po_id)
        if not po or po.status != 'pending':
            return None

        po.status = 'cancelled'
        self.db.commit()
        return po
