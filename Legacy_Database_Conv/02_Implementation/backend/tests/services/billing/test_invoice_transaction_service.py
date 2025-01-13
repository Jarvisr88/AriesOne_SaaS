"""
Tests for invoice transaction service
"""

from datetime import datetime
from decimal import Decimal
import pytest

from app.services.billing.invoice_transaction_service import (
    InvoiceTransactionService,
    InvoiceTransaction,
    InvoiceDetail,
    TransactionType
)

def test_process_transaction_adjust_allowable():
    """Test processing allowable amount adjustment"""
    service = InvoiceTransactionService()
    now = datetime.now()
    
    # Create test transaction
    transaction = InvoiceTransaction(
        id=1,
        customer_id=100,
        invoice_id=200,
        invoice_details_id=300,
        transaction_type_id=1,
        transaction_type=TransactionType.ADJUST_ALLOWABLE,
        amount=Decimal('150.00'),
        quantity=0,  # Will be set from invoice detail
        comments=None,
        created_at=now,
        updated_at=now
    )
    
    # Create test invoice detail
    invoice_detail = InvoiceDetail(
        id=300,
        customer_id=100,
        invoice_id=200,
        allowable_amount=Decimal('100.00'),
        billable_amount=Decimal('200.00'),
        taxes=Decimal('20.00'),
        quantity=2.0
    )
    
    # Process transaction
    updated_transaction, updated_detail = service.process_transaction(
        transaction,
        invoice_detail
    )
    
    # Verify transaction updates
    assert updated_transaction.quantity == 2.0
    assert "Previous Value=100.00" in updated_transaction.comments
    
    # Verify invoice detail updates
    assert updated_detail.allowable_amount == Decimal('150.00')
    assert updated_detail.billable_amount == Decimal('200.00')  # Unchanged
    assert updated_detail.taxes == Decimal('20.00')  # Unchanged

def test_process_transaction_adjust_customary():
    """Test processing billable amount adjustment"""
    service = InvoiceTransactionService()
    now = datetime.now()
    
    # Create test transaction
    transaction = InvoiceTransaction(
        id=1,
        customer_id=100,
        invoice_id=200,
        invoice_details_id=300,
        transaction_type_id=2,
        transaction_type=TransactionType.ADJUST_CUSTOMARY,
        amount=Decimal('250.00'),
        quantity=0,  # Will be set from invoice detail
        comments=None,
        created_at=now,
        updated_at=now
    )
    
    # Create test invoice detail
    invoice_detail = InvoiceDetail(
        id=300,
        customer_id=100,
        invoice_id=200,
        allowable_amount=Decimal('100.00'),
        billable_amount=Decimal('200.00'),
        taxes=Decimal('20.00'),
        quantity=2.0
    )
    
    # Process transaction
    updated_transaction, updated_detail = service.process_transaction(
        transaction,
        invoice_detail
    )
    
    # Verify transaction updates
    assert updated_transaction.quantity == 2.0
    assert "Previous Value=200.00" in updated_transaction.comments
    
    # Verify invoice detail updates
    assert updated_detail.allowable_amount == Decimal('100.00')  # Unchanged
    assert updated_detail.billable_amount == Decimal('250.00')
    assert updated_detail.taxes == Decimal('20.00')  # Unchanged

def test_process_transaction_adjust_taxes():
    """Test processing tax adjustment"""
    service = InvoiceTransactionService()
    now = datetime.now()
    
    # Create test transaction
    transaction = InvoiceTransaction(
        id=1,
        customer_id=100,
        invoice_id=200,
        invoice_details_id=300,
        transaction_type_id=3,
        transaction_type=TransactionType.ADJUST_TAXES,
        amount=Decimal('25.00'),
        quantity=0,  # Will be set from invoice detail
        comments=None,
        created_at=now,
        updated_at=now
    )
    
    # Create test invoice detail
    invoice_detail = InvoiceDetail(
        id=300,
        customer_id=100,
        invoice_id=200,
        allowable_amount=Decimal('100.00'),
        billable_amount=Decimal('200.00'),
        taxes=Decimal('20.00'),
        quantity=2.0
    )
    
    # Process transaction
    updated_transaction, updated_detail = service.process_transaction(
        transaction,
        invoice_detail
    )
    
    # Verify transaction updates
    assert updated_transaction.quantity == 2.0
    assert "Previous Value=20.00" in updated_transaction.comments
    
    # Verify invoice detail updates
    assert updated_detail.allowable_amount == Decimal('100.00')  # Unchanged
    assert updated_detail.billable_amount == Decimal('200.00')  # Unchanged
    assert updated_detail.taxes == Decimal('25.00')

def test_process_transaction_small_change():
    """Test processing transaction with small amount change"""
    service = InvoiceTransactionService()
    now = datetime.now()
    
    # Create test transaction with tiny difference
    transaction = InvoiceTransaction(
        id=1,
        customer_id=100,
        invoice_id=200,
        invoice_details_id=300,
        transaction_type_id=1,
        transaction_type=TransactionType.ADJUST_ALLOWABLE,
        amount=Decimal('100.0009'),  # Tiny difference
        quantity=0,
        comments=None,
        created_at=now,
        updated_at=now
    )
    
    # Create test invoice detail
    invoice_detail = InvoiceDetail(
        id=300,
        customer_id=100,
        invoice_id=200,
        allowable_amount=Decimal('100.00'),
        billable_amount=Decimal('200.00'),
        taxes=Decimal('20.00'),
        quantity=2.0
    )
    
    # Process transaction
    updated_transaction, updated_detail = service.process_transaction(
        transaction,
        invoice_detail
    )
    
    # Verify no changes due to small difference
    assert updated_detail.allowable_amount == Decimal('100.00')  # Unchanged
    assert "Previous Value=100.00" in updated_transaction.comments
