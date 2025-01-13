"""
Inventory Service Module

This module handles inventory-related operations and stock management.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Tuple, Dict

class StockStatus(Enum):
    """Stock status values"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    ON_HOLD = "on_hold"

class AllocationStatus(Enum):
    """Allocation status values"""
    PENDING = "pending"
    ALLOCATED = "allocated"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class StockItem:
    """Stock item details"""
    id: int
    product_id: int
    location_id: int
    quantity: Decimal
    allocated_qty: Decimal
    available_qty: Decimal
    reorder_point: Decimal
    reorder_qty: Decimal
    status: str
    last_count_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

@dataclass
class StockAllocation:
    """Stock allocation details"""
    id: int
    stock_item_id: int
    order_item_id: int
    requested_qty: Decimal
    allocated_qty: Decimal
    status: str
    allocation_date: datetime
    created_at: datetime
    updated_at: datetime

class InventoryService:
    """Handles inventory-related operations"""
    
    # Stock thresholds
    LOW_STOCK_THRESHOLD = Decimal('0.25')  # 25% of reorder point
    
    @classmethod
    def calculate_stock_status(
        cls,
        stock_item: StockItem
    ) -> Tuple[str, Optional[str]]:
        """
        Calculate the current status of a stock item.
        
        Args:
            stock_item: Stock item to check
            
        Returns:
            Tuple containing:
                - New status value
                - Reason for status (if changed)
        """
        if stock_item.status == StockStatus.DISCONTINUED.value:
            return stock_item.status, None
            
        if stock_item.status == StockStatus.ON_HOLD.value:
            return stock_item.status, None
            
        if stock_item.available_qty <= 0:
            return StockStatus.OUT_OF_STOCK.value, "No available quantity"
            
        if stock_item.available_qty <= (
            stock_item.reorder_point * cls.LOW_STOCK_THRESHOLD
        ):
            return StockStatus.LOW_STOCK.value, "Below low stock threshold"
            
        return StockStatus.IN_STOCK.value, None
        
    @classmethod
    def update_stock_levels(
        cls,
        stock_item: StockItem,
        quantity_change: Decimal,
        is_allocation: bool = False
    ) -> Tuple[StockItem, List[str]]:
        """
        Update stock levels for an item.
        
        Args:
            stock_item: Stock item to update
            quantity_change: Change in quantity (positive or negative)
            is_allocation: Whether this is an allocation update
            
        Returns:
            Tuple containing:
                - Updated stock item
                - List of changes made
        """
        changes = []
        now = datetime.now()
        
        # Update quantities
        old_qty = stock_item.quantity
        old_allocated = stock_item.allocated_qty
        old_available = stock_item.available_qty
        
        if is_allocation:
            stock_item.allocated_qty += quantity_change
        else:
            stock_item.quantity += quantity_change
            
        stock_item.available_qty = (
            stock_item.quantity - stock_item.allocated_qty
        )
        
        # Track changes
        if stock_item.quantity != old_qty:
            changes.append(
                f"Updated quantity from {old_qty} to {stock_item.quantity}"
            )
            
        if stock_item.allocated_qty != old_allocated:
            changes.append(
                f"Updated allocated from {old_allocated} "
                f"to {stock_item.allocated_qty}"
            )
            
        if stock_item.available_qty != old_available:
            changes.append(
                f"Updated available from {old_available} "
                f"to {stock_item.available_qty}"
            )
            
        # Update status if needed
        new_status, reason = cls.calculate_stock_status(stock_item)
        if new_status != stock_item.status:
            old_status = stock_item.status
            stock_item.status = new_status
            changes.append(
                f"Updated status from {old_status} to {new_status}: {reason}"
            )
            
        # Update timestamps
        stock_item.updated_at = now
        
        return stock_item, changes
        
    @classmethod
    def allocate_stock(
        cls,
        stock_item: StockItem,
        order_item_id: int,
        requested_qty: Decimal
    ) -> Tuple[StockAllocation, List[str]]:
        """
        Attempt to allocate stock for an order.
        
        Args:
            stock_item: Stock item to allocate from
            order_item_id: Order item to allocate for
            requested_qty: Quantity requested
            
        Returns:
            Tuple containing:
                - Created allocation
                - List of changes made
        """
        changes = []
        now = datetime.now()
        
        # Check if allocation possible
        if stock_item.status in [
            StockStatus.DISCONTINUED.value,
            StockStatus.ON_HOLD.value
        ]:
            allocation = StockAllocation(
                id=0,  # Set by database
                stock_item_id=stock_item.id,
                order_item_id=order_item_id,
                requested_qty=requested_qty,
                allocated_qty=Decimal('0'),
                status=AllocationStatus.FAILED.value,
                allocation_date=now,
                created_at=now,
                updated_at=now
            )
            changes.append(f"Cannot allocate - stock {stock_item.status}")
            return allocation, changes
            
        # Calculate allocation
        available = stock_item.available_qty
        allocated_qty = min(requested_qty, available)
        
        # Create allocation
        allocation = StockAllocation(
            id=0,  # Set by database
            stock_item_id=stock_item.id,
            order_item_id=order_item_id,
            requested_qty=requested_qty,
            allocated_qty=allocated_qty,
            status=(
                AllocationStatus.ALLOCATED.value
                if allocated_qty == requested_qty
                else AllocationStatus.PARTIAL.value
                if allocated_qty > 0
                else AllocationStatus.FAILED.value
            ),
            allocation_date=now,
            created_at=now,
            updated_at=now
        )
        
        # Update stock if allocated
        if allocated_qty > 0:
            stock_item, stock_changes = cls.update_stock_levels(
                stock_item=stock_item,
                quantity_change=allocated_qty,
                is_allocation=True
            )
            changes.extend(stock_changes)
            
        changes.append(
            f"Allocated {allocated_qty} of {requested_qty} requested"
        )
        
        return allocation, changes
