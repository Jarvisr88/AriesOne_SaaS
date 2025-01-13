"""
Tests for the inventory service module
"""

from datetime import datetime
from decimal import Decimal
import pytest

from app.services.billing.inventory_service import (
    InventoryService,
    StockStatus,
    AllocationStatus,
    StockItem,
    StockAllocation
)

def test_calculate_stock_status():
    """Test stock status calculation"""
    service = InventoryService()
    now = datetime.now()
    
    # Create base stock item
    item = StockItem(
        id=1,
        product_id=100,
        location_id=1,
        quantity=Decimal('100'),
        allocated_qty=Decimal('0'),
        available_qty=Decimal('100'),
        reorder_point=Decimal('20'),
        reorder_qty=Decimal('40'),
        status=StockStatus.IN_STOCK.value,
        last_count_date=now,
        created_at=now,
        updated_at=now
    )
    
    # Test discontinued
    item.status = StockStatus.DISCONTINUED.value
    status, reason = service.calculate_stock_status(item)
    assert status == StockStatus.DISCONTINUED.value
    assert reason is None
    
    # Test on hold
    item.status = StockStatus.ON_HOLD.value
    status, reason = service.calculate_stock_status(item)
    assert status == StockStatus.ON_HOLD.value
    assert reason is None
    
    # Test out of stock
    item.status = StockStatus.IN_STOCK.value
    item.available_qty = Decimal('0')
    status, reason = service.calculate_stock_status(item)
    assert status == StockStatus.OUT_OF_STOCK.value
    assert "no available" in reason.lower()
    
    # Test low stock
    item.available_qty = Decimal('4')  # 20% of reorder point
    status, reason = service.calculate_stock_status(item)
    assert status == StockStatus.LOW_STOCK.value
    assert "below" in reason.lower()
    
    # Test in stock
    item.available_qty = Decimal('100')
    status, reason = service.calculate_stock_status(item)
    assert status == StockStatus.IN_STOCK.value
    assert reason is None

def test_update_stock_levels():
    """Test stock level updates"""
    service = InventoryService()
    now = datetime.now()
    
    # Create base stock item
    item = StockItem(
        id=1,
        product_id=100,
        location_id=1,
        quantity=Decimal('100'),
        allocated_qty=Decimal('20'),
        available_qty=Decimal('80'),
        reorder_point=Decimal('20'),
        reorder_qty=Decimal('40'),
        status=StockStatus.IN_STOCK.value,
        last_count_date=now,
        created_at=now,
        updated_at=now
    )
    
    # Test quantity update
    updated, changes = service.update_stock_levels(
        stock_item=item,
        quantity_change=Decimal('-30')
    )
    
    assert updated.quantity == Decimal('70')
    assert updated.allocated_qty == Decimal('20')
    assert updated.available_qty == Decimal('50')
    assert len(changes) == 2  # qty and available changed
    
    # Test allocation update
    updated, changes = service.update_stock_levels(
        stock_item=item,
        quantity_change=Decimal('10'),
        is_allocation=True
    )
    
    assert updated.quantity == Decimal('70')
    assert updated.allocated_qty == Decimal('30')
    assert updated.available_qty == Decimal('40')
    assert len(changes) == 2  # allocated and available changed
    
    # Test status change
    updated, changes = service.update_stock_levels(
        stock_item=item,
        quantity_change=Decimal('-35')
    )
    
    assert updated.quantity == Decimal('35')
    assert updated.allocated_qty == Decimal('30')
    assert updated.available_qty == Decimal('5')
    assert updated.status == StockStatus.LOW_STOCK.value
    assert len(changes) == 3  # qty, available, and status changed

def test_allocate_stock():
    """Test stock allocation"""
    service = InventoryService()
    now = datetime.now()
    
    # Create base stock item
    item = StockItem(
        id=1,
        product_id=100,
        location_id=1,
        quantity=Decimal('100'),
        allocated_qty=Decimal('20'),
        available_qty=Decimal('80'),
        reorder_point=Decimal('20'),
        reorder_qty=Decimal('40'),
        status=StockStatus.IN_STOCK.value,
        last_count_date=now,
        created_at=now,
        updated_at=now
    )
    
    # Test discontinued
    item.status = StockStatus.DISCONTINUED.value
    allocation, changes = service.allocate_stock(
        stock_item=item,
        order_item_id=1,
        requested_qty=Decimal('10')
    )
    
    assert allocation.status == AllocationStatus.FAILED.value
    assert allocation.allocated_qty == Decimal('0')
    assert "cannot allocate" in changes[0].lower()
    
    # Test full allocation
    item.status = StockStatus.IN_STOCK.value
    allocation, changes = service.allocate_stock(
        stock_item=item,
        order_item_id=1,
        requested_qty=Decimal('10')
    )
    
    assert allocation.status == AllocationStatus.ALLOCATED.value
    assert allocation.allocated_qty == Decimal('10')
    assert len(changes) > 1  # Multiple changes from allocation
    
    # Test partial allocation
    allocation, changes = service.allocate_stock(
        stock_item=item,
        order_item_id=2,
        requested_qty=Decimal('100')
    )
    
    assert allocation.status == AllocationStatus.PARTIAL.value
    assert allocation.allocated_qty == Decimal('70')  # Remaining available
    assert len(changes) > 1
    
    # Test failed allocation
    item.available_qty = Decimal('0')
    allocation, changes = service.allocate_stock(
        stock_item=item,
        order_item_id=3,
        requested_qty=Decimal('10')
    )
    
    assert allocation.status == AllocationStatus.FAILED.value
    assert allocation.allocated_qty == Decimal('0')
    assert len(changes) == 1  # Just the allocation message
