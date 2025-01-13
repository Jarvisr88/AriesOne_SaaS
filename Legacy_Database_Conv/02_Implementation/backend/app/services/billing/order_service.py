"""
Order Service Module

This module handles order-related operations and processing.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Tuple, Set

class OrderStatus(Enum):
    """Order status values"""
    DRAFT = "draft"
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    CLOSED = "closed"

class OrderItemStatus(Enum):
    """Order item status values"""
    DRAFT = "draft"
    PENDING = "pending"
    ALLOCATED = "allocated"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    CLOSED = "closed"

@dataclass
class OrderItem:
    """Order item details"""
    id: int
    order_id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    status: str
    ship_date: Optional[datetime]
    delivery_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

@dataclass
class Order:
    """Order details"""
    id: int
    customer_id: int
    order_date: datetime
    ship_date: Optional[datetime]
    delivery_date: Optional[datetime]
    subtotal: Decimal
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem]

class OrderService:
    """Handles order-related operations"""
    
    # Skip conditions
    _SKIP_STATUSES = {
        OrderStatus.CANCELLED.value,
        OrderStatus.CLOSED.value
    }
    
    _SKIP_ITEM_STATUSES = {
        OrderItemStatus.CANCELLED.value,
        OrderItemStatus.CLOSED.value
    }
    
    # Close conditions
    _CLOSEABLE_STATUSES = {
        OrderStatus.DELIVERED.value,
        OrderStatus.CANCELLED.value
    }
    
    _CLOSEABLE_ITEM_STATUSES = {
        OrderItemStatus.DELIVERED.value,
        OrderItemStatus.CANCELLED.value
    }
    
    @classmethod
    def should_close_order(
        cls,
        order: Order,
        check_items: bool = True,
        auto_close_days: Optional[int] = 30
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if an order should be closed.
        
        Args:
            order: Order to check
            check_items: Whether to check item statuses
            auto_close_days: Days after delivery to auto-close
            
        Returns:
            Tuple containing:
                - Whether to close the order
                - Reason for closing (if applicable)
        """
        # Check if already closed
        if order.status == OrderStatus.CLOSED.value:
            return False, "Order is already closed"
            
        # Check order status
        if order.status not in cls._CLOSEABLE_STATUSES:
            return False, f"Order status {order.status} is not closeable"
            
        # Check items if requested
        if check_items and order.items:
            non_closeable_items = [
                i for i in order.items
                if i.status not in cls._CLOSEABLE_ITEM_STATUSES
            ]
            
            if non_closeable_items:
                return False, "Has non-closeable items"
                
        # Check auto-close period
        if (
            auto_close_days and
            order.delivery_date and
            order.status == OrderStatus.DELIVERED.value
        ):
            close_date = order.delivery_date + timedelta(days=auto_close_days)
            if datetime.now() >= close_date:
                return True, f"Auto-closing after {auto_close_days} days"
                
        # Close cancelled orders immediately
        if order.status == OrderStatus.CANCELLED.value:
            return True, "Order is cancelled"
            
        return False, None
        
    @classmethod
    def should_skip_order(
        cls,
        order: Order,
        check_items: bool = True,
        check_dates: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if an order should be skipped during processing.
        
        Args:
            order: Order to check
            check_items: Whether to check item statuses
            check_dates: Whether to check order dates
            
        Returns:
            Tuple containing:
                - Whether to skip the order
                - Reason for skipping (if applicable)
        """
        # Check order status
        if order.status in cls._SKIP_STATUSES:
            return True, f"Order status is {order.status}"
            
        # Check order dates
        if check_dates:
            now = datetime.now()
            
            if order.order_date > now:
                return True, "Order date is in the future"
                
            if (
                order.delivery_date and
                order.delivery_date > now
            ):
                return True, "Delivery date is in the future"
                
        # Check items
        if check_items and order.items:
            active_items = [
                i for i in order.items
                if i.status not in cls._SKIP_ITEM_STATUSES
            ]
            
            if not active_items:
                return True, "No active items"
                
        return False, None
        
    @classmethod
    def filter_processable_orders(
        cls,
        orders: List[Order],
        check_items: bool = True,
        check_dates: bool = True
    ) -> Tuple[List[Order], List[Tuple[Order, str]]]:
        """
        Filter a list of orders to only those that should be processed.
        
        Args:
            orders: List of orders to filter
            check_items: Whether to check item statuses
            check_dates: Whether to check order dates
            
        Returns:
            Tuple containing:
                - List of processable orders
                - List of skipped orders with reasons
        """
        processable = []
        skipped = []
        
        for order in orders:
            should_skip, reason = cls.should_skip_order(
                order=order,
                check_items=check_items,
                check_dates=check_dates
            )
            
            if should_skip:
                skipped.append((order, reason))
            else:
                processable.append(order)
                
        return processable, skipped
