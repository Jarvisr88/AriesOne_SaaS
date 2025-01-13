"""
Tests for the purchase order service module
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
import pytest

from app.services.billing.purchase_order_service import (
    PurchaseOrderService,
    POStatus,
    POItemStatus,
    PurchaseOrder,
    POItem
)

def test_calculate_po_status():
    """Test PO status calculation"""
    service = PurchaseOrderService()
    now = datetime.now()
    today = date.today()
    
    # Create base PO
    po = PurchaseOrder(
        id=1,
        vendor_id=100,
        order_number="PO123",
        order_date=None,
        expected_date=None,
        received_date=None,
        subtotal=Decimal('1000'),
        tax_amount=Decimal('80'),
        total_amount=Decimal('1080'),
        status=POStatus.PENDING.value,
        notes=None,
        created_at=now,
        updated_at=now
    )
    
    # Create base items
    items = [
        POItem(
            id=1,
            po_id=1,
            product_id=100,
            ordered_qty=Decimal('10'),
            received_qty=Decimal('0'),
            unit_price=Decimal('100'),
            total_amount=Decimal('1000'),
            status=POItemStatus.PENDING.value,
            notes=None,
            created_at=now,
            updated_at=now
        )
    ]
    
    # Test cancelled
    po.status = POStatus.CANCELLED.value
    status, reason = service.calculate_po_status(po, items)
    assert status == POStatus.CANCELLED.value
    assert reason is None
    
    # Test closed
    po.status = POStatus.CLOSED.value
    status, reason = service.calculate_po_status(po, items)
    assert status == POStatus.CLOSED.value
    assert reason is None
    
    # Test no items
    po.status = POStatus.PENDING.value
    status, reason = service.calculate_po_status(po, [])
    assert status == POStatus.DRAFT.value
    assert "no items" in reason.lower()
    
    # Test all received
    po.status = POStatus.ORDERED.value
    items[0].status = POItemStatus.RECEIVED.value
    status, reason = service.calculate_po_status(po, items)
    assert status == POStatus.RECEIVED.value
    assert "all items" in reason.lower()
    
    # Test partial received
    items.append(
        POItem(
            id=2,
            po_id=1,
            product_id=101,
            ordered_qty=Decimal('5'),
            received_qty=Decimal('0'),
            unit_price=Decimal('100'),
            total_amount=Decimal('500'),
            status=POItemStatus.PENDING.value,
            notes=None,
            created_at=now,
            updated_at=now
        )
    )
    status, reason = service.calculate_po_status(po, items)
    assert status == POStatus.PARTIAL.value
    assert "some items" in reason.lower()
    
    # Test ordered
    items[0].status = POItemStatus.ORDERED.value
    items[1].status = POItemStatus.ORDERED.value
    po.order_date = today
    status, reason = service.calculate_po_status(po, items)
    assert status == POStatus.ORDERED.value
    assert reason is None
    
    # Test approved/rejected
    po.order_date = None
    po.status = POStatus.APPROVED.value
    status, reason = service.calculate_po_status(po, items)
    assert status == POStatus.APPROVED.value
    assert reason is None
    
    po.status = POStatus.REJECTED.value
    status, reason = service.calculate_po_status(po, items)
    assert status == POStatus.REJECTED.value
    assert reason is None

def test_calculate_approval_requirements():
    """Test approval requirements calculation"""
    service = PurchaseOrderService()
    now = datetime.now()
    
    # Create base PO
    po = PurchaseOrder(
        id=1,
        vendor_id=100,
        order_number="PO123",
        order_date=None,
        expected_date=None,
        received_date=None,
        subtotal=Decimal('1000'),
        tax_amount=Decimal('80'),
        total_amount=Decimal('1080'),
        status=POStatus.PENDING.value,
        notes=None,
        created_at=now,
        updated_at=now
    )
    
    # Test no approvals
    po.total_amount = Decimal('500')
    levels, reason = service.calculate_approval_requirements(po)
    assert not levels
    assert reason is None
    
    # Test manager approval
    po.total_amount = Decimal('2500')
    levels, reason = service.calculate_approval_requirements(po)
    assert levels == ["manager"]
    assert "manager threshold" in reason.lower()
    
    # Test director approval
    po.total_amount = Decimal('7500')
    levels, reason = service.calculate_approval_requirements(po)
    assert levels == ["manager", "director"]
    assert "director threshold" in reason.lower()

def test_update_item_status():
    """Test item status updates"""
    service = PurchaseOrderService()
    now = datetime.now()
    
    # Create base item
    item = POItem(
        id=1,
        po_id=1,
        product_id=100,
        ordered_qty=Decimal('10'),
        received_qty=Decimal('0'),
        unit_price=Decimal('100'),
        total_amount=Decimal('1000'),
        status=POItemStatus.ORDERED.value,
        notes=None,
        created_at=now,
        updated_at=now
    )
    
    # Test partial receipt
    updated, changes = service.update_item_status(
        item=item,
        received_qty=Decimal('4')
    )
    assert updated.received_qty == Decimal('4')
    assert updated.status == POItemStatus.PARTIAL.value
    assert len(changes) == 2  # qty and status changes
    
    # Test full receipt
    updated, changes = service.update_item_status(
        item=item,
        received_qty=Decimal('10')
    )
    assert updated.received_qty == Decimal('10')
    assert updated.status == POItemStatus.RECEIVED.value
    assert len(changes) == 2
    
    # Test over receipt
    updated, changes = service.update_item_status(
        item=item,
        received_qty=Decimal('12')
    )
    assert updated.received_qty == Decimal('12')
    assert updated.status == POItemStatus.RECEIVED.value
    assert len(changes) == 3  # includes warning
    assert any("exceeds" in c.lower() for c in changes)

def test_calculate_totals():
    """Test PO totals calculation"""
    service = PurchaseOrderService()
    now = datetime.now()
    
    # Create items
    items = [
        POItem(
            id=1,
            po_id=1,
            product_id=100,
            ordered_qty=Decimal('10'),
            received_qty=Decimal('0'),
            unit_price=Decimal('100'),
            total_amount=Decimal('1000'),
            status=POItemStatus.PENDING.value,
            notes=None,
            created_at=now,
            updated_at=now
        ),
        POItem(
            id=2,
            po_id=1,
            product_id=101,
            ordered_qty=Decimal('5'),
            received_qty=Decimal('0'),
            unit_price=Decimal('100'),
            total_amount=Decimal('500'),
            status=POItemStatus.PENDING.value,
            notes=None,
            created_at=now,
            updated_at=now
        )
    ]
    
    # Test calculation
    totals, notes = service.calculate_totals(
        items=items,
        tax_rate=Decimal('0.08')
    )
    
    assert totals["subtotal"] == Decimal('1500')
    assert totals["tax_amount"] == Decimal('120')
    assert totals["total_amount"] == Decimal('1620')
    
    assert len(notes) == 3
    assert any("subtotal" in n.lower() for n in notes)
    assert any("tax at 8%" in n.lower() for n in notes)
    assert any("total" in n.lower() for n in notes)
