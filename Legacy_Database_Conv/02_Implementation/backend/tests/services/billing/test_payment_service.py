"""
Tests for the payment service module
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
import pytest

from app.services.billing.payment_service import (
    PaymentService,
    PaymentStatus,
    PaymentType,
    TransactionType,
    Payment,
    Transaction
)

def test_calculate_payment_status():
    """Test payment status calculation"""
    service = PaymentService()
    now = datetime.now()
    today = date.today()
    
    # Create base payment
    payment = Payment(
        id=1,
        invoice_id=100,
        order_id=None,
        payment_type=PaymentType.CREDIT.value,
        payment_date=today,
        amount=Decimal('1000'),
        reference_number="REF123",
        status=PaymentStatus.PENDING.value,
        notes=None,
        created_at=now,
        updated_at=now
    )
    
    # Test voided
    payment.status = PaymentStatus.VOIDED.value
    status, reason = service.calculate_payment_status(payment, [])
    assert status == PaymentStatus.VOIDED.value
    assert reason is None
    
    # Test refunded
    payment.status = PaymentStatus.REFUNDED.value
    status, reason = service.calculate_payment_status(payment, [])
    assert status == PaymentStatus.REFUNDED.value
    assert reason is None
    
    # Test no transactions
    payment.status = PaymentStatus.PENDING.value
    status, reason = service.calculate_payment_status(payment, [])
    assert status == PaymentStatus.PENDING.value
    assert "no transactions" in reason.lower()
    
    # Create base transaction
    transaction = Transaction(
        id=1,
        payment_id=1,
        transaction_type=TransactionType.PAYMENT.value,
        transaction_date=now,
        amount=Decimal('1000'),
        reference_number="TXN123",
        status="completed",
        notes=None,
        created_at=now,
        updated_at=now
    )
    
    # Test void transaction
    void_txn = Transaction(
        id=2,
        payment_id=1,
        transaction_type=TransactionType.VOID.value,
        transaction_date=now + timedelta(minutes=1),
        amount=Decimal('-1000'),
        reference_number="TXN124",
        status="completed",
        notes=None,
        created_at=now,
        updated_at=now
    )
    status, reason = service.calculate_payment_status(
        payment,
        [transaction, void_txn]
    )
    assert status == PaymentStatus.VOIDED.value
    assert "voided" in reason.lower()
    
    # Test refund transaction
    refund_txn = Transaction(
        id=2,
        payment_id=1,
        transaction_type=TransactionType.REFUND.value,
        transaction_date=now + timedelta(minutes=1),
        amount=Decimal('-1000'),
        reference_number="TXN124",
        status="completed",
        notes=None,
        created_at=now,
        updated_at=now
    )
    status, reason = service.calculate_payment_status(
        payment,
        [transaction, refund_txn]
    )
    assert status == PaymentStatus.REFUNDED.value
    assert "refunded" in reason.lower()
    
    # Test failed transaction
    transaction.status = "failed"
    status, reason = service.calculate_payment_status(
        payment,
        [transaction]
    )
    assert status == PaymentStatus.FAILED.value
    assert "failed" in reason.lower()
    
    # Test processing transaction
    transaction.status = "processing"
    status, reason = service.calculate_payment_status(
        payment,
        [transaction]
    )
    assert status == PaymentStatus.PROCESSING.value
    assert "processing" in reason.lower()
    
    # Test completed
    transaction.status = "completed"
    status, reason = service.calculate_payment_status(
        payment,
        [transaction]
    )
    assert status == PaymentStatus.COMPLETED.value
    assert reason is None

def test_validate_payment():
    """Test payment validation"""
    service = PaymentService()
    now = datetime.now()
    today = date.today()
    
    # Create base payment
    payment = Payment(
        id=1,
        invoice_id=100,
        order_id=None,
        payment_type=PaymentType.CREDIT.value,
        payment_date=today,
        amount=Decimal('1000'),
        reference_number="REF123",
        status=PaymentStatus.PENDING.value,
        notes=None,
        created_at=now,
        updated_at=now
    )
    
    # Test valid payment
    valid, messages = service.validate_payment(
        payment=payment,
        balance_due=Decimal('1000')
    )
    assert valid
    assert not messages
    
    # Test invalid type
    payment.payment_type = "invalid"
    valid, messages = service.validate_payment(
        payment=payment,
        balance_due=Decimal('1000')
    )
    assert not valid
    assert any("invalid payment type" in m.lower() for m in messages)
    
    # Test zero amount
    payment.payment_type = PaymentType.CREDIT.value
    payment.amount = Decimal('0')
    valid, messages = service.validate_payment(
        payment=payment,
        balance_due=Decimal('1000')
    )
    assert not valid
    assert any("must be positive" in m.lower() for m in messages)
    
    # Test overpayment
    payment.amount = Decimal('2000')
    valid, messages = service.validate_payment(
        payment=payment,
        balance_due=Decimal('1000')
    )
    assert not valid
    assert any("exceeds balance" in m.lower() for m in messages)
    
    # Test missing reference
    payment.amount = Decimal('1000')
    payment.reference_number = None
    valid, messages = service.validate_payment(
        payment=payment,
        balance_due=Decimal('1000')
    )
    assert not valid
    assert any("reference number required" in m.lower() for m in messages)
    
    # Test large payment
    payment.reference_number = "REF123"
    payment.amount = Decimal('15000')
    valid, messages = service.validate_payment(
        payment=payment,
        balance_due=Decimal('15000')
    )
    assert not valid
    assert any("large payment" in m.lower() for m in messages)

def test_create_transaction():
    """Test transaction creation"""
    service = PaymentService()
    now = datetime.now()
    today = date.today()
    
    # Create base payment
    payment = Payment(
        id=1,
        invoice_id=100,
        order_id=None,
        payment_type=PaymentType.CREDIT.value,
        payment_date=today,
        amount=Decimal('1000'),
        reference_number="REF123",
        status=PaymentStatus.PENDING.value,
        notes=None,
        created_at=now,
        updated_at=now
    )
    
    # Test payment transaction
    transaction, notes = service.create_transaction(
        payment=payment,
        transaction_type=TransactionType.PAYMENT.value,
        reference_number="TXN123",
        notes="Test payment"
    )
    
    assert transaction.payment_id == payment.id
    assert transaction.transaction_type == TransactionType.PAYMENT.value
    assert transaction.amount == payment.amount
    assert transaction.reference_number == "TXN123"
    assert transaction.notes == "Test payment"
    assert len(notes) == 3
    
    # Test refund transaction
    transaction, notes = service.create_transaction(
        payment=payment,
        transaction_type=TransactionType.REFUND.value
    )
    
    assert transaction.amount == -payment.amount
    assert "refund" in notes[0].lower()
    
    # Test void transaction
    transaction, notes = service.create_transaction(
        payment=payment,
        transaction_type=TransactionType.VOID.value
    )
    
    assert transaction.amount == -payment.amount
    assert "void" in notes[0].lower()
    
    # Test invalid type
    with pytest.raises(ValueError):
        service.create_transaction(
            payment=payment,
            transaction_type="invalid"
        )

def test_calculate_payment_allocation():
    """Test payment allocation"""
    service = PaymentService()
    
    # Test full allocation
    invoices = [
        (1, Decimal('500')),  # invoice_id, balance
        (2, Decimal('300')),
        (3, Decimal('200'))
    ]
    
    allocations, notes = service.calculate_payment_allocation(
        payment_amount=Decimal('1000'),
        invoices=invoices
    )
    
    assert len(allocations) == 3
    assert allocations[1] == Decimal('500')
    assert allocations[2] == Decimal('300')
    assert allocations[3] == Decimal('200')
    assert len(notes) == 3
    
    # Test partial allocation
    allocations, notes = service.calculate_payment_allocation(
        payment_amount=Decimal('700'),
        invoices=invoices
    )
    
    assert len(allocations) == 2
    assert allocations[1] == Decimal('500')
    assert allocations[2] == Decimal('200')
    assert len(notes) == 2
    
    # Test excess payment
    allocations, notes = service.calculate_payment_allocation(
        payment_amount=Decimal('1200'),
        invoices=invoices
    )
    
    assert len(allocations) == 3
    assert sum(allocations.values()) == Decimal('1000')
    assert "unallocated" in notes[-1].lower()
    assert "200" in notes[-1]
