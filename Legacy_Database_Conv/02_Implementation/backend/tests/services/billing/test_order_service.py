"""
Tests for the order service module
"""

from decimal import Decimal
import pytest
from app.services.billing.order_service import OrderService, RoundingMethod, BillingType, DeliverySchedule
from datetime import datetime

def test_ordered_qty_to_billed_qty_no_constraints():
    """Test quantity conversion with no constraints"""
    service = OrderService()
    
    ordered_qty = Decimal('10.5')
    billed_qty, message = service.ordered_qty_to_billed_qty(ordered_qty)
    
    assert billed_qty == ordered_qty
    assert message == "No adjustments needed"

def test_ordered_qty_to_billed_qty_min_qty():
    """Test quantity conversion with minimum quantity"""
    service = OrderService()
    
    # Test below minimum
    ordered_qty = Decimal('5')
    min_qty = Decimal('10')
    billed_qty, message = service.ordered_qty_to_billed_qty(
        ordered_qty,
        min_qty=min_qty
    )
    
    assert billed_qty == min_qty
    assert "increased to minimum" in message
    
    # Test above minimum
    ordered_qty = Decimal('15')
    billed_qty, message = service.ordered_qty_to_billed_qty(
        ordered_qty,
        min_qty=min_qty
    )
    
    assert billed_qty == ordered_qty
    assert message == "No adjustments needed"

def test_ordered_qty_to_billed_qty_max_qty():
    """Test quantity conversion with maximum quantity"""
    service = OrderService()
    
    # Test above maximum
    ordered_qty = Decimal('100')
    max_qty = Decimal('50')
    billed_qty, message = service.ordered_qty_to_billed_qty(
        ordered_qty,
        max_qty=max_qty
    )
    
    assert billed_qty == max_qty
    assert "reduced to maximum" in message
    
    # Test below maximum
    ordered_qty = Decimal('25')
    billed_qty, message = service.ordered_qty_to_billed_qty(
        ordered_qty,
        max_qty=max_qty
    )
    
    assert billed_qty == ordered_qty
    assert message == "No adjustments needed"

def test_ordered_qty_to_billed_qty_increment():
    """Test quantity conversion with increment"""
    service = OrderService()
    
    ordered_qty = Decimal('7.3')
    increment = Decimal('5')
    
    # Test round up
    billed_qty, message = service.ordered_qty_to_billed_qty(
        ordered_qty,
        increment=increment,
        rounding_method=RoundingMethod.ROUND_UP
    )
    assert billed_qty == Decimal('10')
    assert "rounded to nearest increment" in message
    
    # Test round down
    billed_qty, message = service.ordered_qty_to_billed_qty(
        ordered_qty,
        increment=increment,
        rounding_method=RoundingMethod.ROUND_DOWN
    )
    assert billed_qty == Decimal('5')
    assert "rounded to nearest increment" in message
    
    # Test round nearest
    billed_qty, message = service.ordered_qty_to_billed_qty(
        ordered_qty,
        increment=increment,
        rounding_method=RoundingMethod.ROUND_NEAREST
    )
    assert billed_qty == Decimal('5')
    assert "rounded to nearest increment" in message

def test_ordered_qty_to_billed_qty_all_constraints():
    """Test quantity conversion with all constraints"""
    service = OrderService()
    
    ordered_qty = Decimal('7.3')
    min_qty = Decimal('5')
    max_qty = Decimal('20')
    increment = Decimal('5')
    
    billed_qty, message = service.ordered_qty_to_billed_qty(
        ordered_qty,
        min_qty=min_qty,
        max_qty=max_qty,
        increment=increment,
        rounding_method=RoundingMethod.ROUND_UP
    )
    
    assert billed_qty == Decimal('10')
    assert "rounded to nearest increment" in message

def test_get_ordered_qty_flat_rate():
    """Test ordered quantity calculation for flat rate billing"""
    service = OrderService()
    
    base_qty = Decimal('10')
    ordered_qty, message = service.get_ordered_qty(
        base_qty=base_qty,
        billing_type=BillingType.FLAT_RATE
    )
    
    assert ordered_qty == base_qty
    assert "Flat rate billing" in message

def test_get_ordered_qty_per_use():
    """Test ordered quantity calculation for per-use billing"""
    service = OrderService()
    
    base_qty = Decimal('10')
    usage_qty = Decimal('15')
    billing_params = {
        'min_usage': '5',
        'multiplier': '1.5'
    }
    
    # Test with usage above minimum
    ordered_qty, message = service.get_ordered_qty(
        base_qty=base_qty,
        billing_type=BillingType.PER_USE,
        billing_params=billing_params,
        usage_qty=usage_qty
    )
    
    assert ordered_qty == Decimal('22.5')  # 15 * 1.5
    assert "Per-use billing" in message
    
    # Test with usage below minimum
    usage_qty = Decimal('3')
    ordered_qty, message = service.get_ordered_qty(
        base_qty=base_qty,
        billing_type=BillingType.PER_USE,
        billing_params=billing_params,
        usage_qty=usage_qty
    )
    
    assert ordered_qty == Decimal('7.5')  # 5 * 1.5
    assert "Per-use billing" in message

def test_get_ordered_qty_tiered():
    """Test ordered quantity calculation for tiered billing"""
    service = OrderService()
    
    base_qty = Decimal('100')
    tier_rates = {
        Decimal('0'): Decimal('1.0'),
        Decimal('50'): Decimal('0.9'),
        Decimal('100'): Decimal('0.8'),
        Decimal('200'): Decimal('0.7')
    }
    
    ordered_qty, message = service.get_ordered_qty(
        base_qty=base_qty,
        billing_type=BillingType.TIERED,
        tier_rates=tier_rates
    )
    
    assert ordered_qty == Decimal('80')  # 100 * 0.8
    assert "Tiered billing" in message
    assert "0.8" in message
    assert "100" in message

def test_get_ordered_qty_custom():
    """Test ordered quantity calculation with custom calculation"""
    service = OrderService()
    
    def custom_calc(qty: Decimal, factor: Decimal) -> Decimal:
        return qty * factor
    
    base_qty = Decimal('10')
    billing_params = {'factor': Decimal('2.5')}
    
    ordered_qty, message = service.get_ordered_qty(
        base_qty=base_qty,
        billing_type=BillingType.CUSTOM,
        billing_params=billing_params,
        custom_calc=custom_calc
    )
    
    assert ordered_qty == Decimal('25')
    assert "Custom calculation applied" in message

def test_get_ordered_qty_fallback():
    """Test ordered quantity calculation fallback behavior"""
    service = OrderService()
    
    base_qty = Decimal('10')
    
    # Test missing usage data
    ordered_qty, message = service.get_ordered_qty(
        base_qty=base_qty,
        billing_type=BillingType.PER_USE
    )
    
    assert ordered_qty == base_qty
    assert "No usage data" in message
    
    # Test missing tier rates
    ordered_qty, message = service.get_ordered_qty(
        base_qty=base_qty,
        billing_type=BillingType.TIERED
    )
    
    assert ordered_qty == base_qty
    assert "No tier rates" in message
    
    # Test missing custom calculation
    ordered_qty, message = service.get_ordered_qty(
        base_qty=base_qty,
        billing_type=BillingType.CUSTOM
    )
    
    assert ordered_qty == base_qty
    assert "No custom calculation" in message

def test_ordered_qty_to_delivery_qty_immediate():
    """Test delivery quantity calculation for immediate delivery"""
    service = OrderService()
    
    ordered_qty = Decimal('100')
    delivery_qty, message = service.ordered_qty_to_delivery_qty(
        ordered_qty=ordered_qty,
        delivery_schedule=DeliverySchedule.IMMEDIATE
    )
    
    assert delivery_qty == ordered_qty
    assert "immediate delivery" in message

def test_ordered_qty_to_delivery_qty_scheduled():
    """Test delivery quantity calculation for scheduled delivery"""
    service = OrderService()
    
    ordered_qty = Decimal('100')
    delivery_date = datetime(2025, 1, 15)
    window_start = datetime(2025, 1, 1)
    window_end = datetime(2025, 1, 31)
    
    # Test delivery within window
    schedule_params = {
        'delivery_date': delivery_date,
        'window_start': window_start,
        'window_end': window_end,
        'prorate': True
    }
    
    delivery_qty, message = service.ordered_qty_to_delivery_qty(
        ordered_qty=ordered_qty,
        delivery_schedule=DeliverySchedule.SCHEDULED,
        schedule_params=schedule_params
    )
    
    assert delivery_qty == Decimal('54.84')  # 17/31 * 100
    assert "Prorated delivery" in message
    
    # Test delivery outside window
    schedule_params['delivery_date'] = datetime(2025, 2, 1)
    delivery_qty, message = service.ordered_qty_to_delivery_qty(
        ordered_qty=ordered_qty,
        delivery_schedule=DeliverySchedule.SCHEDULED,
        schedule_params=schedule_params
    )
    
    assert delivery_qty == Decimal('0')
    assert "outside window" in message

def test_ordered_qty_to_delivery_qty_recurring():
    """Test delivery quantity calculation for recurring delivery"""
    service = OrderService()
    
    ordered_qty = Decimal('100')
    schedule_params = {
        'frequency': 7,  # days
        'total_deliveries': 4
    }
    
    delivery_qty, message = service.ordered_qty_to_delivery_qty(
        ordered_qty=ordered_qty,
        delivery_schedule=DeliverySchedule.RECURRING,
        schedule_params=schedule_params
    )
    
    assert delivery_qty == Decimal('25')  # 100/4
    assert "Recurring delivery" in message
    assert "4 deliveries" in message

def test_ordered_qty_to_delivery_qty_custom():
    """Test delivery quantity calculation with custom schedule"""
    service = OrderService()
    
    def custom_schedule(qty: Decimal, factor: Decimal) -> Decimal:
        return qty * factor
    
    ordered_qty = Decimal('100')
    schedule_params = {'factor': Decimal('0.5')}
    
    delivery_qty, message = service.ordered_qty_to_delivery_qty(
        ordered_qty=ordered_qty,
        delivery_schedule=DeliverySchedule.CUSTOM,
        schedule_params=schedule_params,
        custom_schedule=custom_schedule
    )
    
    assert delivery_qty == Decimal('50')
    assert "Custom schedule applied" in message

def test_ordered_qty_to_delivery_qty_constraints():
    """Test delivery quantity calculation with constraints"""
    service = OrderService()
    
    ordered_qty = Decimal('100')
    delivery_constraints = {
        'min_delivery': '20',
        'max_delivery': '80',
        'increment': '10'
    }
    
    # Test maximum constraint
    delivery_qty, message = service.ordered_qty_to_delivery_qty(
        ordered_qty=ordered_qty,
        delivery_schedule=DeliverySchedule.IMMEDIATE,
        delivery_constraints=delivery_constraints
    )
    
    assert delivery_qty == Decimal('80')
    assert "max=80" in message
    
    # Test minimum constraint
    ordered_qty = Decimal('10')
    delivery_qty, message = service.ordered_qty_to_delivery_qty(
        ordered_qty=ordered_qty,
        delivery_schedule=DeliverySchedule.IMMEDIATE,
        delivery_constraints=delivery_constraints
    )
    
    assert delivery_qty == Decimal('20')
    assert "min=20" in message
    
    # Test increment constraint
    ordered_qty = Decimal('75')
    delivery_qty, message = service.ordered_qty_to_delivery_qty(
        ordered_qty=ordered_qty,
        delivery_schedule=DeliverySchedule.IMMEDIATE,
        delivery_constraints=delivery_constraints
    )
    
    assert delivery_qty == Decimal('80')  # Rounded up to nearest 10
    assert "increment=10" in message

from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from app.services.billing.order_service import (
    OrderService,
    OrderStatus,
    OrderItemStatus,
    Order,
    OrderItem
)

def test_should_close_order():
    """Test order close logic"""
    service = OrderService()
    now = datetime.now()
    
    # Create base order for testing
    order = Order(
        id=1,
        customer_id=1000,
        order_date=now,
        ship_date=now,
        delivery_date=now,
        subtotal=Decimal('1000'),
        total_amount=Decimal('1000'),
        status=OrderStatus.DELIVERED.value,
        created_at=now,
        updated_at=now,
        items=[]
    )
    
    # Test already closed
    order.status = OrderStatus.CLOSED.value
    should_close, reason = service.should_close_order(order)
    assert not should_close
    assert "already closed" in reason.lower()
    
    # Test invalid status
    order.status = OrderStatus.DRAFT.value
    should_close, reason = service.should_close_order(order)
    assert not should_close
    assert "not closeable" in reason.lower()
    
    # Test non-closeable items
    order.status = OrderStatus.DELIVERED.value
    order.items = [
        OrderItem(
            id=1,
            order_id=1,
            product_id=100,
            quantity=Decimal('10'),
            unit_price=Decimal('100'),
            total_amount=Decimal('1000'),
            status=OrderItemStatus.SHIPPED.value,
            ship_date=now,
            delivery_date=None,
            created_at=now,
            updated_at=now
        )
    ]
    should_close, reason = service.should_close_order(order)
    assert not should_close
    assert "non-closeable items" in reason.lower()
    
    # Test auto-close period
    order.items[0].status = OrderItemStatus.DELIVERED.value
    order.delivery_date = now - timedelta(days=31)
    should_close, reason = service.should_close_order(order)
    assert should_close
    assert "auto-closing" in reason.lower()
    
    # Test cancelled order
    order.status = OrderStatus.CANCELLED.value
    should_close, reason = service.should_close_order(order)
    assert should_close
    assert "cancelled" in reason.lower()

def test_should_skip_order():
    """Test order skip logic"""
    service = OrderService()
    now = datetime.now()
    
    # Create base order for testing
    order = Order(
        id=1,
        customer_id=1000,
        order_date=now,
        ship_date=None,
        delivery_date=None,
        subtotal=Decimal('1000'),
        total_amount=Decimal('1000'),
        status=OrderStatus.DRAFT.value,
        created_at=now,
        updated_at=now,
        items=[]
    )
    
    # Test status checks
    order.status = OrderStatus.CLOSED.value
    should_skip, reason = service.should_skip_order(order)
    assert should_skip
    assert "status" in reason.lower()
    
    order.status = OrderStatus.CANCELLED.value
    should_skip, reason = service.should_skip_order(order)
    assert should_skip
    assert "status" in reason.lower()
    
    # Test date checks
    order.status = OrderStatus.DRAFT.value
    order.order_date = now + timedelta(days=1)
    should_skip, reason = service.should_skip_order(order)
    assert should_skip
    assert "future" in reason.lower()
    
    order.order_date = now
    order.delivery_date = now + timedelta(days=1)
    should_skip, reason = service.should_skip_order(order)
    assert should_skip
    assert "future" in reason.lower()
    
    # Test item checks
    order.delivery_date = None
    order.items = [
        OrderItem(
            id=1,
            order_id=1,
            product_id=100,
            quantity=Decimal('10'),
            unit_price=Decimal('100'),
            total_amount=Decimal('1000'),
            status=OrderItemStatus.CLOSED.value,
            ship_date=None,
            delivery_date=None,
            created_at=now,
            updated_at=now
        )
    ]
    should_skip, reason = service.should_skip_order(order)
    assert should_skip
    assert "active items" in reason.lower()
    
    # Test processable order
    order.items[0].status = OrderItemStatus.DRAFT.value
    should_skip, reason = service.should_skip_order(order)
    assert not should_skip
    assert reason is None

def test_filter_processable_orders():
    """Test order filtering"""
    service = OrderService()
    now = datetime.now()
    
    # Create test orders
    orders = [
        # Processable order
        Order(
            id=1,
            customer_id=1000,
            order_date=now,
            ship_date=None,
            delivery_date=None,
            subtotal=Decimal('1000'),
            total_amount=Decimal('1000'),
            status=OrderStatus.DRAFT.value,
            created_at=now,
            updated_at=now,
            items=[
                OrderItem(
                    id=1,
                    order_id=1,
                    product_id=100,
                    quantity=Decimal('10'),
                    unit_price=Decimal('100'),
                    total_amount=Decimal('1000'),
                    status=OrderItemStatus.DRAFT.value,
                    ship_date=None,
                    delivery_date=None,
                    created_at=now,
                    updated_at=now
                )
            ]
        ),
        # Closed order
        Order(
            id=2,
            customer_id=1000,
            order_date=now,
            ship_date=now,
            delivery_date=now,
            subtotal=Decimal('500'),
            total_amount=Decimal('500'),
            status=OrderStatus.CLOSED.value,
            created_at=now,
            updated_at=now,
            items=[]
        ),
        # Future order
        Order(
            id=3,
            customer_id=1000,
            order_date=now + timedelta(days=1),
            ship_date=None,
            delivery_date=None,
            subtotal=Decimal('750'),
            total_amount=Decimal('750'),
            status=OrderStatus.DRAFT.value,
            created_at=now,
            updated_at=now,
            items=[]
        )
    ]
    
    # Test filtering
    processable, skipped = service.filter_processable_orders(orders)
    
    assert len(processable) == 1
    assert processable[0].id == 1
    
    assert len(skipped) == 2
    assert {o.id for o, _ in skipped} == {2, 3}
    assert any("status" in r.lower() for _, r in skipped)
    assert any("future" in r.lower() for _, r in skipped)
    
    # Test without date checks
    processable, skipped = service.filter_processable_orders(
        orders,
        check_dates=False
    )
    
    assert len(processable) == 2
    assert {o.id for o in processable} == {1, 3}
    
    assert len(skipped) == 1
    assert skipped[0][0].id == 2
