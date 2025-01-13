"""
Purchase Order Service Module

This module handles purchase order operations and management.
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Tuple, Dict

class POStatus(Enum):
    """Purchase order status values"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    CLOSED = "closed"

class POItemStatus(Enum):
    """Purchase order item status values"""
    PENDING = "pending"
    ORDERED = "ordered"
    PARTIAL = "partial"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    CLOSED = "closed"

@dataclass
class PurchaseOrder:
    """Purchase order details"""
    id: int
    vendor_id: int
    order_number: str
    order_date: Optional[date]
    expected_date: Optional[date]
    received_date: Optional[date]
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class POItem:
    """Purchase order item details"""
    id: int
    po_id: int
    product_id: int
    ordered_qty: Decimal
    received_qty: Decimal
    unit_price: Decimal
    total_amount: Decimal
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class PurchaseOrderService:
    """Handles purchase order operations"""
    
    # Approval thresholds
    MANAGER_APPROVAL_THRESHOLD = Decimal('1000')
    DIRECTOR_APPROVAL_THRESHOLD = Decimal('5000')
    
    @classmethod
    def calculate_po_status(
        cls,
        po: PurchaseOrder,
        items: List[POItem]
    ) -> Tuple[str, Optional[str]]:
        """
        Calculate the current status of a purchase order.
        
        Args:
            po: Purchase order to check
            items: PO items to check
            
        Returns:
            Tuple containing:
                - New status value
                - Reason for status (if changed)
        """
        if po.status == POStatus.CANCELLED.value:
            return po.status, None
            
        if po.status == POStatus.CLOSED.value:
            return po.status, None
            
        if not items:
            return POStatus.DRAFT.value, "No items"
            
        # Check if all items received
        all_received = all(
            item.status == POItemStatus.RECEIVED.value
            for item in items
        )
        if all_received:
            return POStatus.RECEIVED.value, "All items received"
            
        # Check if any items received
        any_received = any(
            item.status == POItemStatus.RECEIVED.value
            for item in items
        )
        if any_received:
            return POStatus.PARTIAL.value, "Some items received"
            
        # Check if ordered
        if po.order_date:
            return POStatus.ORDERED.value, None
            
        # Check approval status
        if po.status == POStatus.APPROVED.value:
            return po.status, None
            
        if po.status == POStatus.REJECTED.value:
            return po.status, None
            
        return POStatus.PENDING.value, None
        
    @classmethod
    def calculate_approval_requirements(
        cls,
        po: PurchaseOrder
    ) -> Tuple[List[str], Optional[str]]:
        """
        Calculate approval requirements for a PO.
        
        Args:
            po: Purchase order to check
            
        Returns:
            Tuple containing:
                - List of required approval levels
                - Reason for requirements
        """
        required_levels = []
        
        if po.total_amount >= cls.DIRECTOR_APPROVAL_THRESHOLD:
            required_levels.extend([
                "manager",
                "director"
            ])
            reason = "Amount exceeds director threshold"
            
        elif po.total_amount >= cls.MANAGER_APPROVAL_THRESHOLD:
            required_levels.append("manager")
            reason = "Amount exceeds manager threshold"
            
        else:
            reason = None
            
        return required_levels, reason
        
    @classmethod
    def update_item_status(
        cls,
        item: POItem,
        received_qty: Optional[Decimal] = None
    ) -> Tuple[POItem, List[str]]:
        """
        Update status of a PO item.
        
        Args:
            item: Item to update
            received_qty: New received quantity
            
        Returns:
            Tuple containing:
                - Updated item
                - List of changes made
        """
        changes = []
        now = datetime.now()
        
        if received_qty is not None:
            old_qty = item.received_qty
            item.received_qty = received_qty
            
            if received_qty > item.ordered_qty:
                changes.append(
                    f"Warning: Received {received_qty} exceeds "
                    f"ordered {item.ordered_qty}"
                )
                
            changes.append(
                f"Updated received quantity from {old_qty} to {received_qty}"
            )
            
            # Update status based on quantity
            old_status = item.status
            if received_qty >= item.ordered_qty:
                item.status = POItemStatus.RECEIVED.value
            elif received_qty > 0:
                item.status = POItemStatus.PARTIAL.value
            else:
                item.status = POItemStatus.ORDERED.value
                
            if item.status != old_status:
                changes.append(
                    f"Updated status from {old_status} to {item.status}"
                )
                
        item.updated_at = now
        
        return item, changes
        
    @classmethod
    def calculate_totals(
        cls,
        items: List[POItem],
        tax_rate: Decimal
    ) -> Tuple[Dict[str, Decimal], List[str]]:
        """
        Calculate PO totals from items.
        
        Args:
            items: Items to calculate from
            tax_rate: Tax rate to apply
            
        Returns:
            Tuple containing:
                - Dictionary of calculated values
                - List of calculation notes
        """
        notes = []
        
        # Calculate subtotal
        subtotal = sum(
            item.total_amount
            for item in items
        )
        notes.append(f"Subtotal: ${subtotal}")
        
        # Calculate tax
        tax_amount = (subtotal * tax_rate).quantize(Decimal('0.01'))
        notes.append(
            f"Tax at {tax_rate * 100}%: ${tax_amount}"
        )
        
        # Calculate total
        total_amount = subtotal + tax_amount
        notes.append(f"Total: ${total_amount}")
        
        return (
            {
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total_amount": total_amount
            },
            notes
        )
