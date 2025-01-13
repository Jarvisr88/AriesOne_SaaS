"""
Tests for the invoice service module
"""

from decimal import Decimal
from datetime import datetime, timedelta
import pytest
from app.services.billing.invoice_service import (
    InvoiceService,
    Invoice,
    InvoiceDetail,
    InvoiceStatus,
    Payment,
    PaymentStatus
)

def test_add_auto_split_details():
    """Test adding split invoice details"""
    service = InvoiceService()
    
    # Test parameters
    invoice_id = 1
    item_id = 100
    total_quantity = Decimal('100')
    unit_price = Decimal('10')
    base_date = datetime(2025, 1, 1)
    split_dates = [
        base_date,
        base_date + timedelta(days=30),
        base_date + timedelta(days=60)
    ]
    split_quantities = [
        Decimal('30'),
        Decimal('40'),
        Decimal('30')
    ]
    tax_percent = Decimal('8.25')
    discount_percent = Decimal('10')
    
    # Add split details
    details = service.add_auto_split_details(
        invoice_id=invoice_id,
        item_id=item_id,
        total_quantity=total_quantity,
        unit_price=unit_price,
        split_dates=split_dates,
        split_quantities=split_quantities,
        tax_percent=tax_percent,
        discount_percent=discount_percent
    )
    
    # Verify results
    assert len(details) == 3
    
    # Check first split
    detail = details[0]
    assert detail.invoice_id == invoice_id
    assert detail.item_id == item_id
    assert detail.quantity == Decimal('30')
    assert detail.unit_price == unit_price
    assert detail.tax_percent == tax_percent
    assert detail.discount_percent == discount_percent
    assert detail.status == InvoiceStatus.DRAFT.value
    
    # Verify amounts
    subtotal = Decimal('30') * unit_price
    discount = subtotal * (discount_percent / Decimal('100'))
    tax = (subtotal - discount) * (tax_percent / Decimal('100'))
    total = subtotal - discount + tax
    assert detail.total_amount == total
    
    # Test validation
    with pytest.raises(ValueError):
        service.add_auto_split_details(
            invoice_id=invoice_id,
            item_id=item_id,
            total_quantity=total_quantity,
            unit_price=unit_price,
            split_dates=split_dates[:-1],  # One less date
            split_quantities=split_quantities,
            tax_percent=tax_percent,
            discount_percent=discount_percent
        )
        
    with pytest.raises(ValueError):
        service.add_auto_split_details(
            invoice_id=invoice_id,
            item_id=item_id,
            total_quantity=total_quantity,
            unit_price=unit_price,
            split_dates=split_dates,
            split_quantities=[Decimal('50'), Decimal('20'), Decimal('20')],  # Wrong total
            tax_percent=tax_percent,
            discount_percent=discount_percent
        )

def test_recalculate_internals():
    """Test recalculating invoice internal amounts"""
    service = InvoiceService()
    
    # Create test invoice
    details = [
        InvoiceDetail(
            id=1,
            invoice_id=1,
            item_id=100,
            quantity=Decimal('30'),
            unit_price=Decimal('10'),
            discount_percent=Decimal('10'),
            tax_percent=Decimal('8.25'),
            total_amount=Decimal('0'),  # Will be recalculated
            status=InvoiceStatus.DRAFT.value,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        InvoiceDetail(
            id=2,
            invoice_id=1,
            item_id=101,
            quantity=Decimal('20'),
            unit_price=Decimal('15'),
            discount_percent=Decimal('0'),
            tax_percent=Decimal('8.25'),
            total_amount=Decimal('0'),  # Will be recalculated
            status=InvoiceStatus.DRAFT.value,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    invoice = Invoice(
        id=1,
        customer_id=1000,
        invoice_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        subtotal=Decimal('0'),
        discount_total=Decimal('0'),
        tax_total=Decimal('0'),
        total_amount=Decimal('0'),
        balance=Decimal('0'),
        status=InvoiceStatus.DRAFT.value,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        details=details
    )
    
    # Test full recalculation
    updated_invoice, changes = service.recalculate_internals(
        invoice=invoice,
        apply_tax=True,
        apply_discount=True
    )
    
    # Verify detail amounts
    detail = updated_invoice.details[0]
    subtotal = Decimal('30') * Decimal('10')
    discount = subtotal * (Decimal('10') / Decimal('100'))
    tax = (subtotal - discount) * (Decimal('8.25') / Decimal('100'))
    total = subtotal - discount + tax
    assert detail.total_amount == total
    
    # Verify invoice totals
    assert updated_invoice.subtotal == Decimal('600')  # (30 * 10) + (20 * 15)
    assert updated_invoice.discount_total == Decimal('30')  # Only first detail has discount
    assert updated_invoice.tax_total.quantize(Decimal('.01')) == Decimal('45.71')
    assert len(changes) > 0
    
    # Test without tax
    updated_invoice, changes = service.recalculate_internals(
        invoice=invoice,
        apply_tax=False,
        apply_discount=True
    )
    
    assert updated_invoice.tax_total == Decimal('0')
    assert len(changes) > 0
    
    # Test without discount
    updated_invoice, changes = service.recalculate_internals(
        invoice=invoice,
        apply_tax=True,
        apply_discount=False
    )
    
    assert updated_invoice.discount_total == Decimal('0')
    assert len(changes) > 0
    
    # Test cancelled detail
    invoice.details[0].status = InvoiceStatus.CANCELLED.value
    updated_invoice, changes = service.recalculate_internals(invoice)
    
    assert updated_invoice.subtotal == Decimal('300')  # Only second detail counted
    assert len(changes) > 0

def test_recalculate_detail():
    """Test recalculating single detail"""
    service = InvoiceService()
    now = datetime.now()
    
    # Create test detail
    detail = InvoiceDetail(
        id=1,
        invoice_id=1,
        item_id=100,
        quantity=Decimal('10'),
        unit_price=Decimal('100'),
        discount_percent=Decimal('10'),
        tax_percent=Decimal('8.25'),
        total_amount=Decimal('0'),  # Will be recalculated
        status=InvoiceStatus.DRAFT.value,
        created_at=now,
        updated_at=now
    )
    
    # Test full recalculation
    updated_detail, changes = service.recalculate_detail(
        detail=detail,
        apply_tax=True,
        apply_discount=True
    )
    
    subtotal = Decimal('1000')  # 10 * 100
    discount = Decimal('100')   # 10% of 1000
    tax = Decimal('74.25')     # 8.25% of 900
    total = Decimal('974.25')  # 1000 - 100 + 74.25
    
    assert updated_detail.total_amount == total
    assert len(changes) == 1
    
    # Test without tax
    updated_detail, changes = service.recalculate_detail(
        detail=detail,
        apply_tax=False,
        apply_discount=True
    )
    
    total = Decimal('900')  # 1000 - 100
    assert updated_detail.total_amount == total
    assert len(changes) == 1
    
    # Test without discount
    updated_detail, changes = service.recalculate_detail(
        detail=detail,
        apply_tax=True,
        apply_discount=False
    )
    
    total = Decimal('1082.50')  # 1000 + (1000 * 0.0825)
    assert updated_detail.total_amount == total
    assert len(changes) == 1
    
    # Test cancelled detail
    detail.status = InvoiceStatus.CANCELLED.value
    updated_detail, changes = service.recalculate_detail(detail)
    
    assert updated_detail.total_amount == total  # Unchanged
    assert "cancelled" in changes[0]

def test_add_payment():
    """Test adding payment to invoice"""
    service = InvoiceService()
    
    # Create test invoice
    invoice = Invoice(
        id=1,
        customer_id=1000,
        invoice_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        subtotal=Decimal('1000'),
        discount_total=Decimal('100'),
        tax_total=Decimal('74.25'),
        total_amount=Decimal('974.25'),
        balance=Decimal('974.25'),
        status=InvoiceStatus.APPROVED.value,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        details=[]
    )
    
    # Test full payment
    invoice, payment, changes = service.add_payment(
        invoice=invoice,
        amount=Decimal('974.25'),
        payment_method='credit_card',
        reference_number='REF123',
        notes='Test payment'
    )
    
    assert invoice.balance == Decimal('0')
    assert invoice.status == InvoiceStatus.PAID.value
    assert payment.amount == Decimal('974.25')
    assert payment.status == PaymentStatus.PENDING.value
    assert len(changes) == 2  # Balance update and status change
    
    # Test partial payment
    invoice = Invoice(
        id=2,
        customer_id=1000,
        invoice_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        subtotal=Decimal('1000'),
        discount_total=Decimal('0'),
        tax_total=Decimal('0'),
        total_amount=Decimal('1000'),
        balance=Decimal('1000'),
        status=InvoiceStatus.APPROVED.value,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        details=[]
    )
    
    invoice, payment, changes = service.add_payment(
        invoice=invoice,
        amount=Decimal('500'),
        payment_method='check',
        reference_number='CHECK456'
    )
    
    assert invoice.balance == Decimal('500')
    assert invoice.status == InvoiceStatus.APPROVED.value  # Status unchanged
    assert payment.amount == Decimal('500')
    assert len(changes) == 1  # Only balance update
    
    # Test validation
    with pytest.raises(ValueError):
        service.add_payment(
            invoice=invoice,
            amount=Decimal('0'),
            payment_method='cash',
            reference_number='INVALID'
        )
        
    with pytest.raises(ValueError):
        service.add_payment(
            invoice=invoice,
            amount=Decimal('1000'),  # Exceeds balance
            payment_method='cash',
            reference_number='INVALID'
        )

def test_update_balance():
    """Test updating invoice balance"""
    service = InvoiceService()
    now = datetime.now()
    
    # Create test invoice with payments
    payments = [
        Payment(
            id=1,
            invoice_id=1,
            amount=Decimal('500'),
            payment_date=now,
            payment_method='credit_card',
            reference_number='REF1',
            status=PaymentStatus.COMPLETED.value,
            notes=None,
            created_at=now,
            updated_at=now
        ),
        Payment(
            id=2,
            invoice_id=1,
            amount=Decimal('300'),
            payment_date=now,
            payment_method='check',
            reference_number='REF2',
            status=PaymentStatus.PENDING.value,
            notes=None,
            created_at=now,
            updated_at=now
        ),
        Payment(
            id=3,
            invoice_id=1,
            amount=Decimal('200'),
            payment_date=now,
            payment_method='cash',
            reference_number='REF3',
            status=PaymentStatus.PROCESSING.value,
            notes=None,
            created_at=now,
            updated_at=now
        ),
        Payment(
            id=4,
            invoice_id=1,
            amount=Decimal('100'),
            payment_date=now,
            payment_method='check',
            reference_number='REF4',
            status=PaymentStatus.FAILED.value,
            notes=None,
            created_at=now,
            updated_at=now
        )
    ]
    
    invoice = Invoice(
        id=1,
        customer_id=1000,
        invoice_date=now,
        due_date=now + timedelta(days=30),
        subtotal=Decimal('1000'),
        discount_total=Decimal('0'),
        tax_total=Decimal('0'),
        total_amount=Decimal('1000'),
        balance=Decimal('1000'),
        status=InvoiceStatus.APPROVED.value,
        created_at=now,
        updated_at=now,
        details=[],
        payments=payments
    )
    
    # Test with pending payments
    updated_invoice, changes = service.update_balance(
        invoice=invoice,
        include_pending=True
    )
    
    assert updated_invoice.balance == Decimal('0')  # All payments count
    assert updated_invoice.status == InvoiceStatus.PAID.value
    assert len(changes) == 2  # Balance and status updates
    
    # Test without pending payments
    updated_invoice, changes = service.update_balance(
        invoice=invoice,
        include_pending=False
    )
    
    assert updated_invoice.balance == Decimal('500')  # Only completed payments
    assert updated_invoice.status == InvoiceStatus.APPROVED.value  # Not paid
    assert len(changes) == 1  # Only balance update

def test_submit_invoice():
    """Test submitting invoice"""
    service = InvoiceService()
    
    # Create test invoice
    details = [
        InvoiceDetail(
            id=1,
            invoice_id=1,
            item_id=100,
            quantity=Decimal('10'),
            unit_price=Decimal('100'),
            discount_percent=Decimal('0'),
            tax_percent=Decimal('8.25'),
            total_amount=Decimal('1082.50'),
            status=InvoiceStatus.DRAFT.value,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        InvoiceDetail(
            id=2,
            invoice_id=1,
            item_id=101,
            quantity=Decimal('5'),
            unit_price=Decimal('50'),
            discount_percent=Decimal('0'),
            tax_percent=Decimal('8.25'),
            total_amount=Decimal('270.63'),
            status=InvoiceStatus.DRAFT.value,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    invoice = Invoice(
        id=1,
        customer_id=1000,
        invoice_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        subtotal=Decimal('1250'),
        discount_total=Decimal('0'),
        tax_total=Decimal('103.13'),
        total_amount=Decimal('1353.13'),
        balance=Decimal('1353.13'),
        status=InvoiceStatus.DRAFT.value,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        details=details
    )
    
    # Test submission
    updated_invoice, changes = service.submit_invoice(invoice)
    
    assert updated_invoice.status == InvoiceStatus.SUBMITTED.value
    assert all(d.status == InvoiceStatus.SUBMITTED.value for d in updated_invoice.details)
    assert len(changes) == 1
    
    # Test validation
    with pytest.raises(ValueError):
        service.submit_invoice(
            Invoice(
                id=2,
                customer_id=1000,
                invoice_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                subtotal=Decimal('0'),
                discount_total=Decimal('0'),
                tax_total=Decimal('0'),
                total_amount=Decimal('0'),
                balance=Decimal('0'),
                status=InvoiceStatus.DRAFT.value,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                details=[]  # No details
            )
        )
        
    with pytest.raises(ValueError):
        invoice.status = InvoiceStatus.PAID.value
        service.submit_invoice(invoice)  # Invalid status

def test_update_pending_submissions():
    """Test updating pending submissions"""
    service = InvoiceService()
    now = datetime.now()
    
    # Create test invoices
    invoices = [
        # Should be approved (old submission)
        Invoice(
            id=1,
            customer_id=1000,
            invoice_date=now,
            due_date=now + timedelta(days=30),
            subtotal=Decimal('1000'),
            discount_total=Decimal('0'),
            tax_total=Decimal('0'),
            total_amount=Decimal('1000'),
            balance=Decimal('1000'),
            status=InvoiceStatus.SUBMITTED.value,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2),
            details=[
                InvoiceDetail(
                    id=1,
                    invoice_id=1,
                    item_id=100,
                    quantity=Decimal('10'),
                    unit_price=Decimal('100'),
                    discount_percent=Decimal('0'),
                    tax_percent=Decimal('0'),
                    total_amount=Decimal('1000'),
                    status=InvoiceStatus.SUBMITTED.value,
                    created_at=now - timedelta(days=2),
                    updated_at=now - timedelta(days=2)
                )
            ]
        ),
        # Should not be approved (recent submission)
        Invoice(
            id=2,
            customer_id=1001,
            invoice_date=now,
            due_date=now + timedelta(days=30),
            subtotal=Decimal('500'),
            discount_total=Decimal('0'),
            tax_total=Decimal('0'),
            total_amount=Decimal('500'),
            balance=Decimal('500'),
            status=InvoiceStatus.SUBMITTED.value,
            created_at=now,
            updated_at=now,
            details=[
                InvoiceDetail(
                    id=2,
                    invoice_id=2,
                    item_id=101,
                    quantity=Decimal('5'),
                    unit_price=Decimal('100'),
                    discount_percent=Decimal('0'),
                    tax_percent=Decimal('0'),
                    total_amount=Decimal('500'),
                    status=InvoiceStatus.SUBMITTED.value,
                    created_at=now,
                    updated_at=now
                )
            ]
        ),
        # Should be ignored (wrong status)
        Invoice(
            id=3,
            customer_id=1002,
            invoice_date=now,
            due_date=now + timedelta(days=30),
            subtotal=Decimal('750'),
            discount_total=Decimal('0'),
            tax_total=Decimal('0'),
            total_amount=Decimal('750'),
            balance=Decimal('750'),
            status=InvoiceStatus.DRAFT.value,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=2),
            details=[]
        )
    ]
    
    # Test updates
    cutoff = now - timedelta(days=1)
    updated_invoices, changes = service.update_pending_submissions(
        invoices=invoices,
        submission_cutoff=cutoff
    )
    
    assert len(updated_invoices) == 1
    assert updated_invoices[0].id == 1
    assert updated_invoices[0].status == InvoiceStatus.APPROVED.value
    assert updated_invoices[0].details[0].status == InvoiceStatus.APPROVED.value
    assert len(changes) == 1

def test_validate_status_transition():
    """Test status transition validation"""
    service = InvoiceService()
    
    # Test valid transitions
    service.validate_status_transition(
        InvoiceStatus.DRAFT.value,
        InvoiceStatus.SUBMITTED.value
    )
    
    service.validate_status_transition(
        InvoiceStatus.SUBMITTED.value,
        InvoiceStatus.APPROVED.value
    )
    
    service.validate_status_transition(
        InvoiceStatus.APPROVED.value,
        InvoiceStatus.PAID.value
    )
    
    # Test invalid transitions
    with pytest.raises(StatusTransitionError):
        service.validate_status_transition(
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.PAID.value
        )
        
    with pytest.raises(StatusTransitionError):
        service.validate_status_transition(
            InvoiceStatus.CANCELLED.value,
            InvoiceStatus.DRAFT.value
        )
        
    with pytest.raises(StatusTransitionError):
        service.validate_status_transition(
            InvoiceStatus.PAID.value,
            InvoiceStatus.SUBMITTED.value
        )

def test_update_invoice_status():
    """Test invoice status updates"""
    service = InvoiceService()
    now = datetime.now()
    
    # Create test invoice
    details = [
        InvoiceDetail(
            id=1,
            invoice_id=1,
            item_id=100,
            quantity=Decimal('10'),
            unit_price=Decimal('100'),
            discount_percent=Decimal('0'),
            tax_percent=Decimal('8.25'),
            total_amount=Decimal('1082.50'),
            status=InvoiceStatus.DRAFT.value,
            created_at=now,
            updated_at=now
        ),
        InvoiceDetail(
            id=2,
            invoice_id=1,
            item_id=101,
            quantity=Decimal('5'),
            unit_price=Decimal('50'),
            discount_percent=Decimal('0'),
            tax_percent=Decimal('8.25'),
            total_amount=Decimal('270.63'),
            status=InvoiceStatus.DRAFT.value,
            created_at=now,
            updated_at=now
        )
    ]
    
    invoice = Invoice(
        id=1,
        customer_id=1000,
        invoice_date=now,
        due_date=now + timedelta(days=30),
        subtotal=Decimal('1250'),
        discount_total=Decimal('0'),
        tax_total=Decimal('103.13'),
        total_amount=Decimal('1353.13'),
        balance=Decimal('1353.13'),
        status=InvoiceStatus.DRAFT.value,
        created_at=now,
        updated_at=now,
        details=details
    )
    
    # Test status update with details
    updated_invoice, changes = service.update_invoice_status(
        invoice=invoice,
        new_status=InvoiceStatus.SUBMITTED.value,
        update_details=True,
        notes="Manual submission"
    )
    
    assert updated_invoice.status == InvoiceStatus.SUBMITTED.value
    assert all(d.status == InvoiceStatus.SUBMITTED.value for d in updated_invoice.details)
    assert len(changes) == 3  # Invoice + 2 details
    assert "Manual submission" in changes[0]
    
    # Test status update without details
    updated_invoice, changes = service.update_invoice_status(
        invoice=invoice,
        new_status=InvoiceStatus.APPROVED.value,
        update_details=False
    )
    
    assert updated_invoice.status == InvoiceStatus.APPROVED.value
    assert all(d.status == InvoiceStatus.SUBMITTED.value for d in updated_invoice.details)
    assert len(changes) == 1  # Only invoice
    
    # Test invalid transition
    with pytest.raises(StatusTransitionError):
        service.update_invoice_status(
            invoice=invoice,
            new_status=InvoiceStatus.DRAFT.value
        )

def test_cancel_invoice():
    """Test invoice cancellation"""
    service = InvoiceService()
    now = datetime.now()
    
    # Create test invoice with details and payments
    details = [
        InvoiceDetail(
            id=1,
            invoice_id=1,
            item_id=100,
            quantity=Decimal('10'),
            unit_price=Decimal('100'),
            discount_percent=Decimal('0'),
            tax_percent=Decimal('0'),
            total_amount=Decimal('1000'),
            status=InvoiceStatus.APPROVED.value,
            created_at=now,
            updated_at=now
        )
    ]
    
    payments = [
        Payment(
            id=1,
            invoice_id=1,
            amount=Decimal('500'),
            payment_date=now,
            payment_method='credit_card',
            reference_number='REF1',
            status=PaymentStatus.COMPLETED.value,
            notes=None,
            created_at=now,
            updated_at=now
        ),
        Payment(
            id=2,
            invoice_id=1,
            amount=Decimal('500'),
            payment_date=now,
            payment_method='check',
            reference_number='REF2',
            status=PaymentStatus.PENDING.value,
            notes=None,
            created_at=now,
            updated_at=now
        )
    ]
    
    invoice = Invoice(
        id=1,
        customer_id=1000,
        invoice_date=now,
        due_date=now + timedelta(days=30),
        subtotal=Decimal('1000'),
        discount_total=Decimal('0'),
        tax_total=Decimal('0'),
        total_amount=Decimal('1000'),
        balance=Decimal('500'),
        status=InvoiceStatus.APPROVED.value,
        created_at=now,
        updated_at=now,
        details=details,
        payments=payments
    )
    
    # Test cancellation with payment voiding
    updated_invoice, changes = service.cancel_invoice(
        invoice=invoice,
        reason="Customer request",
        cancel_payments=True
    )
    
    assert updated_invoice.status == InvoiceStatus.CANCELLED.value
    assert all(d.status == InvoiceStatus.CANCELLED.value for d in updated_invoice.details)
    assert any(p.status == PaymentStatus.VOIDED.value for p in updated_invoice.payments)
    assert len(changes) == 3  # Invoice + detail + payment
    assert "Customer request" in changes[0]
    
    # Test cancellation without payment voiding
    invoice.status = InvoiceStatus.APPROVED.value  # Reset for test
    updated_invoice, changes = service.cancel_invoice(
        invoice=invoice,
        reason="System error",
        cancel_payments=False
    )
    
    assert updated_invoice.status == InvoiceStatus.CANCELLED.value
    assert all(d.status == InvoiceStatus.CANCELLED.value for d in updated_invoice.details)
    assert not any(p.status == PaymentStatus.VOIDED.value for p in updated_invoice.payments)
    assert len(changes) == 2  # Invoice + detail
    assert "System error" in changes[0]
    
    # Test invalid cancellation
    invoice.status = InvoiceStatus.CANCELLED.value
    with pytest.raises(StatusTransitionError):
        service.cancel_invoice(
            invoice=invoice,
            reason="Already cancelled"
        )

def test_should_skip_invoice():
    """Test invoice skip logic"""
    service = InvoiceService()
    now = datetime.now()
    
    # Create base invoice for testing
    invoice = Invoice(
        id=1,
        customer_id=1000,
        invoice_date=now,
        due_date=now + timedelta(days=30),
        subtotal=Decimal('1000'),
        discount_total=Decimal('0'),
        tax_total=Decimal('0'),
        total_amount=Decimal('1000'),
        balance=Decimal('1000'),
        status=InvoiceStatus.DRAFT.value,
        created_at=now,
        updated_at=now,
        details=[],
        payments=[]
    )
    
    # Test status checks
    invoice.status = InvoiceStatus.CANCELLED.value
    should_skip, reason = service.should_skip_invoice(invoice)
    assert should_skip
    assert "status" in reason.lower()
    
    invoice.status = InvoiceStatus.PAID.value
    should_skip, reason = service.should_skip_invoice(invoice)
    assert should_skip
    assert "status" in reason.lower()
    
    # Test date checks
    invoice.status = InvoiceStatus.DRAFT.value
    invoice.invoice_date = now + timedelta(days=1)
    should_skip, reason = service.should_skip_invoice(invoice)
    assert should_skip
    assert "future" in reason.lower()
    
    invoice.invoice_date = now
    invoice.due_date = now - timedelta(days=1)
    should_skip, reason = service.should_skip_invoice(invoice)
    assert should_skip
    assert "past due" in reason.lower()
    
    # Test detail checks
    invoice.due_date = now + timedelta(days=30)
    invoice.details = [
        InvoiceDetail(
            id=1,
            invoice_id=1,
            item_id=100,
            quantity=Decimal('10'),
            unit_price=Decimal('100'),
            discount_percent=Decimal('0'),
            tax_percent=Decimal('0'),
            total_amount=Decimal('1000'),
            status=InvoiceStatus.CANCELLED.value,
            created_at=now,
            updated_at=now
        )
    ]
    should_skip, reason = service.should_skip_invoice(invoice)
    assert should_skip
    assert "active details" in reason.lower()
    
    # Test payment checks
    invoice.details[0].status = InvoiceStatus.DRAFT.value
    invoice.payments = [
        Payment(
            id=1,
            invoice_id=1,
            amount=Decimal('500'),
            payment_date=now,
            payment_method='check',
            reference_number='REF1',
            status=PaymentStatus.PENDING.value,
            notes=None,
            created_at=now,
            updated_at=now
        )
    ]
    should_skip, reason = service.should_skip_invoice(invoice)
    assert should_skip
    assert "pending payments" in reason.lower()
    
    # Test processable invoice
    invoice.payments[0].status = PaymentStatus.COMPLETED.value
    should_skip, reason = service.should_skip_invoice(invoice)
    assert not should_skip
    assert reason is None

def test_filter_processable_invoices():
    """Test invoice filtering"""
    service = InvoiceService()
    now = datetime.now()
    
    # Create test invoices
    invoices = [
        # Processable invoice
        Invoice(
            id=1,
            customer_id=1000,
            invoice_date=now,
            due_date=now + timedelta(days=30),
            subtotal=Decimal('1000'),
            discount_total=Decimal('0'),
            tax_total=Decimal('0'),
            total_amount=Decimal('1000'),
            balance=Decimal('1000'),
            status=InvoiceStatus.DRAFT.value,
            created_at=now,
            updated_at=now,
            details=[
                InvoiceDetail(
                    id=1,
                    invoice_id=1,
                    item_id=100,
                    quantity=Decimal('10'),
                    unit_price=Decimal('100'),
                    discount_percent=Decimal('0'),
                    tax_percent=Decimal('0'),
                    total_amount=Decimal('1000'),
                    status=InvoiceStatus.DRAFT.value,
                    created_at=now,
                    updated_at=now
                )
            ],
            payments=[]
        ),
        # Cancelled invoice
        Invoice(
            id=2,
            customer_id=1000,
            invoice_date=now,
            due_date=now + timedelta(days=30),
            subtotal=Decimal('500'),
            discount_total=Decimal('0'),
            tax_total=Decimal('0'),
            total_amount=Decimal('500'),
            balance=Decimal('500'),
            status=InvoiceStatus.CANCELLED.value,
            created_at=now,
            updated_at=now,
            details=[],
            payments=[]
        ),
        # Future invoice
        Invoice(
            id=3,
            customer_id=1000,
            invoice_date=now + timedelta(days=1),
            due_date=now + timedelta(days=30),
            subtotal=Decimal('750'),
            discount_total=Decimal('0'),
            tax_total=Decimal('0'),
            total_amount=Decimal('750'),
            balance=Decimal('750'),
            status=InvoiceStatus.DRAFT.value,
            created_at=now,
            updated_at=now,
            details=[],
            payments=[]
        )
    ]
    
    # Test filtering
    processable, skipped = service.filter_processable_invoices(invoices)
    
    assert len(processable) == 1
    assert processable[0].id == 1
    
    assert len(skipped) == 2
    assert {i.id for i, _ in skipped} == {2, 3}
    assert any("status" in r.lower() for _, r in skipped)
    assert any("future" in r.lower() for _, r in skipped)
    
    # Test without date checks
    processable, skipped = service.filter_processable_invoices(
        invoices,
        check_dates=False
    )
    
    assert len(processable) == 2
    assert {i.id for i in processable} == {1, 3}
    
    assert len(skipped) == 1
    assert skipped[0][0].id == 2
