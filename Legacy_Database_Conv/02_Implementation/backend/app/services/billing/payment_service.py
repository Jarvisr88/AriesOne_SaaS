"""
Payment Service Module

This module handles payment processing and transaction management.
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Tuple, Dict

class PaymentStatus(Enum):
    """Payment status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VOIDED = "voided"
    REFUNDED = "refunded"

class PaymentType(Enum):
    """Payment type values"""
    CASH = "cash"
    CHECK = "check"
    CREDIT = "credit"
    DEBIT = "debit"
    INSURANCE = "insurance"
    ADJUSTMENT = "adjustment"

class TransactionType(Enum):
    """Transaction type values"""
    PAYMENT = "payment"
    REFUND = "refund"
    VOID = "void"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"

@dataclass
class Payment:
    """Payment details"""
    id: int
    invoice_id: Optional[int]
    order_id: Optional[int]
    payment_type: str
    payment_date: date
    amount: Decimal
    reference_number: Optional[str]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Transaction:
    """Transaction details"""
    id: int
    payment_id: int
    transaction_type: str
    transaction_date: datetime
    amount: Decimal
    reference_number: Optional[str]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class PaymentService:
    """Handles payment operations"""
    
    # Payment thresholds
    LARGE_PAYMENT_THRESHOLD = Decimal('10000')
    
    @classmethod
    def calculate_payment_status(
        cls,
        payment: Payment,
        transactions: List[Transaction]
    ) -> Tuple[str, Optional[str]]:
        """
        Calculate the current status of a payment.
        
        Args:
            payment: Payment to check
            transactions: Payment transactions to check
            
        Returns:
            Tuple containing:
                - New status value
                - Reason for status (if changed)
        """
        if payment.status == PaymentStatus.VOIDED.value:
            return payment.status, None
            
        if payment.status == PaymentStatus.REFUNDED.value:
            return payment.status, None
            
        if not transactions:
            return PaymentStatus.PENDING.value, "No transactions"
            
        # Check for void/refund
        latest_transaction = max(
            transactions,
            key=lambda t: t.transaction_date
        )
        if latest_transaction.transaction_type == TransactionType.VOID.value:
            return PaymentStatus.VOIDED.value, "Payment voided"
            
        if latest_transaction.transaction_type == TransactionType.REFUND.value:
            return PaymentStatus.REFUNDED.value, "Payment refunded"
            
        # Check transaction status
        if any(
            t.status == "failed"
            for t in transactions
        ):
            return PaymentStatus.FAILED.value, "Transaction failed"
            
        if any(
            t.status == "processing"
            for t in transactions
        ):
            return PaymentStatus.PROCESSING.value, "Transaction processing"
            
        return PaymentStatus.COMPLETED.value, None
        
    @classmethod
    def validate_payment(
        cls,
        payment: Payment,
        balance_due: Decimal
    ) -> Tuple[bool, List[str]]:
        """
        Validate a payment before processing.
        
        Args:
            payment: Payment to validate
            balance_due: Expected balance
            
        Returns:
            Tuple containing:
                - Whether payment is valid
                - List of validation messages
        """
        messages = []
        
        # Check payment type
        if payment.payment_type not in [
            pt.value for pt in PaymentType
        ]:
            messages.append(f"Invalid payment type: {payment.payment_type}")
            
        # Check amount
        if payment.amount <= 0:
            messages.append("Payment amount must be positive")
            
        if payment.amount > balance_due:
            messages.append(
                f"Payment amount ${payment.amount} exceeds "
                f"balance due ${balance_due}"
            )
            
        # Check reference
        if payment.payment_type in [
            PaymentType.CHECK.value,
            PaymentType.CREDIT.value,
            PaymentType.DEBIT.value
        ] and not payment.reference_number:
            messages.append(
                f"Reference number required for {payment.payment_type}"
            )
            
        # Check large payments
        if payment.amount >= cls.LARGE_PAYMENT_THRESHOLD:
            messages.append(
                f"Large payment (${payment.amount}) requires "
                "additional verification"
            )
            
        return not bool(messages), messages
        
    @classmethod
    def create_transaction(
        cls,
        payment: Payment,
        transaction_type: str,
        amount: Optional[Decimal] = None,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[Transaction, List[str]]:
        """
        Create a new transaction for a payment.
        
        Args:
            payment: Payment to create transaction for
            transaction_type: Type of transaction
            amount: Transaction amount (defaults to payment amount)
            reference_number: Transaction reference
            notes: Transaction notes
            
        Returns:
            Tuple containing:
                - Created transaction
                - List of transaction notes
        """
        notes_list = []
        now = datetime.now()
        
        # Validate transaction type
        if transaction_type not in [
            tt.value for tt in TransactionType
        ]:
            raise ValueError(f"Invalid transaction type: {transaction_type}")
            
        # Set amount
        if amount is None:
            amount = payment.amount
            
        if transaction_type in [
            TransactionType.REFUND.value,
            TransactionType.VOID.value
        ]:
            amount = -amount
            
        # Create transaction
        transaction = Transaction(
            id=0,  # Set by database
            payment_id=payment.id,
            transaction_type=transaction_type,
            transaction_date=now,
            amount=amount,
            reference_number=reference_number,
            status="pending",
            notes=notes,
            created_at=now,
            updated_at=now
        )
        
        # Add notes
        notes_list.append(
            f"Created {transaction_type} transaction for ${abs(amount)}"
        )
        if reference_number:
            notes_list.append(f"Reference: {reference_number}")
        if notes:
            notes_list.append(f"Notes: {notes}")
            
        return transaction, notes_list
        
    @classmethod
    def calculate_payment_allocation(
        cls,
        payment_amount: Decimal,
        invoices: List[Tuple[int, Decimal]]
    ) -> Tuple[Dict[int, Decimal], List[str]]:
        """
        Calculate payment allocation across invoices.
        
        Args:
            payment_amount: Amount to allocate
            invoices: List of (invoice_id, balance) tuples
            
        Returns:
            Tuple containing:
                - Dictionary of invoice_id to allocated amount
                - List of allocation notes
        """
        notes = []
        allocations = {}
        remaining = payment_amount
        
        # Sort invoices by balance (highest first)
        sorted_invoices = sorted(
            invoices,
            key=lambda x: x[1],
            reverse=True
        )
        
        # Allocate to each invoice
        for invoice_id, balance in sorted_invoices:
            if remaining <= 0:
                break
                
            allocation = min(balance, remaining)
            allocations[invoice_id] = allocation
            remaining -= allocation
            
            notes.append(
                f"Allocated ${allocation} to invoice {invoice_id}"
            )
            
        if remaining > 0:
            notes.append(
                f"Remaining unallocated amount: ${remaining}"
            )
            
        return allocations, notes
