"""
Invoice Service Module

This module handles invoice-related operations and calculations.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class InvoiceDetail:
    """Data class for invoice detail records"""
    id: int
    invoice_id: int
    item_id: int
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal
    tax_percent: Decimal
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class Invoice:
    """Data class for invoice records"""
    id: int
    customer_id: int
    invoice_date: datetime
    due_date: datetime
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    total_amount: Decimal
    balance: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    details: List[InvoiceDetail]

class InvoiceStatus(Enum):
    """Invoice status types"""
    DRAFT = "draft"
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    """Payment status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    VOIDED = "voided"

@dataclass
class Payment:
    """Data class for payment records"""
    id: int
    invoice_id: int
    amount: Decimal
    payment_date: datetime
    payment_method: str
    reference_number: str
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class StatusTransitionError(Exception):
    """Error raised when an invalid status transition is attempted"""
    pass

class InvoiceService:
    """Handles invoice-related operations and calculations"""
    
    # Valid status transitions
    _STATUS_TRANSITIONS = {
        InvoiceStatus.DRAFT.value: [
            InvoiceStatus.PENDING.value,
            InvoiceStatus.SUBMITTED.value,
            InvoiceStatus.CANCELLED.value
        ],
        InvoiceStatus.PENDING.value: [
            InvoiceStatus.SUBMITTED.value,
            InvoiceStatus.CANCELLED.value
        ],
        InvoiceStatus.SUBMITTED.value: [
            InvoiceStatus.APPROVED.value,
            InvoiceStatus.CANCELLED.value
        ],
        InvoiceStatus.APPROVED.value: [
            InvoiceStatus.PAID.value,
            InvoiceStatus.CANCELLED.value
        ],
        InvoiceStatus.PAID.value: [
            InvoiceStatus.CANCELLED.value
        ],
        InvoiceStatus.CANCELLED.value: []  # Terminal state
    }
    
    # Skip conditions
    _SKIP_STATUSES = {
        InvoiceStatus.CANCELLED.value,
        InvoiceStatus.PAID.value
    }
    
    _SKIP_PAYMENT_STATUSES = {
        PaymentStatus.COMPLETED.value,
        PaymentStatus.VOIDED.value,
        PaymentStatus.FAILED.value
    }
    
    @staticmethod
    def add_auto_split_details(
        invoice_id: int,
        item_id: int,
        total_quantity: Decimal,
        unit_price: Decimal,
        split_dates: List[datetime],
        split_quantities: List[Decimal],
        tax_percent: Decimal = Decimal('0'),
        discount_percent: Decimal = Decimal('0')
    ) -> List[InvoiceDetail]:
        """
        Add multiple invoice detail records with split quantities.
        
        Args:
            invoice_id: ID of the invoice
            item_id: ID of the item
            total_quantity: Total quantity to split
            unit_price: Price per unit
            split_dates: List of dates for splits
            split_quantities: List of quantities for splits
            tax_percent: Tax percentage
            discount_percent: Discount percentage
            
        Returns:
            List of created invoice detail records
        """
        if len(split_dates) != len(split_quantities):
            raise ValueError("Split dates and quantities must have same length")
            
        if sum(split_quantities) != total_quantity:
            raise ValueError("Split quantities must sum to total quantity")
            
        details = []
        now = datetime.now()
        
        for date, quantity in zip(split_dates, split_quantities):
            # Calculate amounts
            subtotal = quantity * unit_price
            discount_amount = subtotal * (discount_percent / Decimal('100'))
            tax_amount = (subtotal - discount_amount) * (tax_percent / Decimal('100'))
            total = subtotal - discount_amount + tax_amount
            
            # Create detail record
            detail = InvoiceDetail(
                id=0,  # Will be set by database
                invoice_id=invoice_id,
                item_id=item_id,
                quantity=quantity,
                unit_price=unit_price,
                discount_percent=discount_percent,
                tax_percent=tax_percent,
                total_amount=total,
                status=InvoiceStatus.DRAFT.value,
                created_at=now,
                updated_at=now
            )
            
            details.append(detail)
            
        return details
        
    @staticmethod
    def recalculate_internals(
        invoice: Invoice,
        apply_tax: bool = True,
        apply_discount: bool = True
    ) -> Tuple[Invoice, List[str]]:
        """
        Recalculate internal amounts for an invoice.
        
        Args:
            invoice: Invoice to recalculate
            apply_tax: Whether to apply tax calculations
            apply_discount: Whether to apply discount calculations
            
        Returns:
            Tuple containing:
                - Updated invoice
                - List of changes made
        """
        changes = []
        
        # Reset totals
        old_subtotal = invoice.subtotal
        old_discount = invoice.discount_total
        old_tax = invoice.tax_total
        old_total = invoice.total_amount
        
        invoice.subtotal = Decimal('0')
        invoice.discount_total = Decimal('0')
        invoice.tax_total = Decimal('0')
        invoice.total_amount = Decimal('0')
        
        # Recalculate from details
        for detail in invoice.details:
            if detail.status != InvoiceStatus.CANCELLED.value:
                # Calculate detail amounts
                subtotal = detail.quantity * detail.unit_price
                
                discount_amount = Decimal('0')
                if apply_discount and detail.discount_percent > 0:
                    discount_amount = subtotal * (detail.discount_percent / Decimal('100'))
                    
                tax_amount = Decimal('0')
                if apply_tax and detail.tax_percent > 0:
                    tax_amount = (subtotal - discount_amount) * (detail.tax_percent / Decimal('100'))
                    
                total = subtotal - discount_amount + tax_amount
                
                # Update detail if changed
                if total != detail.total_amount:
                    detail.total_amount = total
                    detail.updated_at = datetime.now()
                    changes.append(f"Updated detail {detail.id} total to {total}")
                
                # Add to invoice totals
                invoice.subtotal += subtotal
                invoice.discount_total += discount_amount
                invoice.tax_total += tax_amount
                invoice.total_amount += total
        
        # Record changes in totals
        if invoice.subtotal != old_subtotal:
            changes.append(
                f"Updated subtotal from {old_subtotal} to {invoice.subtotal}"
            )
            
        if invoice.discount_total != old_discount:
            changes.append(
                f"Updated discount from {old_discount} to {invoice.discount_total}"
            )
            
        if invoice.tax_total != old_tax:
            changes.append(
                f"Updated tax from {old_tax} to {invoice.tax_total}"
            )
            
        if invoice.total_amount != old_total:
            changes.append(
                f"Updated total from {old_total} to {invoice.total_amount}"
            )
            
        if changes:
            invoice.updated_at = datetime.now()
            
        return invoice, changes

    @staticmethod
    def recalculate_detail(
        detail: InvoiceDetail,
        apply_tax: bool = True,
        apply_discount: bool = True
    ) -> Tuple[InvoiceDetail, List[str]]:
        """
        Recalculate amounts for a single invoice detail.
        
        Args:
            detail: Detail to recalculate
            apply_tax: Whether to apply tax calculations
            apply_discount: Whether to apply discount calculations
            
        Returns:
            Tuple containing:
                - Updated detail
                - List of changes made
        """
        changes = []
        now = datetime.now()
        
        # Skip cancelled details
        if detail.status == InvoiceStatus.CANCELLED.value:
            return detail, ["Detail is cancelled - no recalculation needed"]
            
        # Calculate amounts
        old_total = detail.total_amount
        subtotal = detail.quantity * detail.unit_price
        
        discount_amount = Decimal('0')
        if apply_discount and detail.discount_percent > 0:
            discount_amount = subtotal * (detail.discount_percent / Decimal('100'))
            
        tax_amount = Decimal('0')
        if apply_tax and detail.tax_percent > 0:
            tax_amount = (subtotal - discount_amount) * (detail.tax_percent / Decimal('100'))
            
        total = subtotal - discount_amount + tax_amount
        
        # Update if changed
        if total != old_total:
            detail.total_amount = total
            detail.updated_at = now
            changes.append(
                f"Updated detail {detail.id} total from {old_total} to {total}"
            )
            
        return detail, changes
        
    @staticmethod
    def update_balance(
        invoice: Invoice,
        include_pending: bool = True
    ) -> Tuple[Invoice, List[str]]:
        """
        Update invoice balance based on payments.
        
        Args:
            invoice: Invoice to update
            include_pending: Whether to include pending payments
            
        Returns:
            Tuple containing:
                - Updated invoice
                - List of changes made
        """
        changes = []
        now = datetime.now()
        
        # Get all payments
        payment_statuses = [PaymentStatus.COMPLETED.value]
        if include_pending:
            payment_statuses.extend([
                PaymentStatus.PENDING.value,
                PaymentStatus.PROCESSING.value
            ])
            
        # Calculate total payments
        total_payments = sum(
            payment.amount
            for payment in invoice.payments
            if payment.status in payment_statuses
        )
        
        # Update balance
        old_balance = invoice.balance
        invoice.balance = invoice.total_amount - total_payments
        
        if invoice.balance != old_balance:
            invoice.updated_at = now
            changes.append(
                f"Updated balance from {old_balance} to {invoice.balance}"
            )
            
            # Update status if fully paid
            if invoice.balance == 0:
                old_status = invoice.status
                invoice.status = InvoiceStatus.PAID.value
                changes.append(
                    f"Updated status from {old_status} to {invoice.status}"
                )
                
        return invoice, changes

    @staticmethod
    def add_payment(
        invoice: Invoice,
        amount: Decimal,
        payment_method: str,
        reference_number: str,
        payment_date: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Tuple[Invoice, Payment, List[str]]:
        """
        Add a payment to an invoice.
        
        Args:
            invoice: Invoice to add payment to
            amount: Payment amount
            payment_method: Method of payment
            reference_number: Payment reference number
            payment_date: Date of payment (defaults to now)
            notes: Optional payment notes
            
        Returns:
            Tuple containing:
                - Updated invoice
                - Created payment
                - List of changes made
        """
        changes = []
        now = datetime.now()
        payment_date = payment_date or now
        
        # Validate payment amount
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
            
        if amount > invoice.balance:
            raise ValueError(f"Payment amount {amount} exceeds invoice balance {invoice.balance}")
            
        # Create payment record
        payment = Payment(
            id=0,  # Will be set by database
            invoice_id=invoice.id,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            status=PaymentStatus.PENDING.value,
            notes=notes,
            created_at=now,
            updated_at=now
        )
        
        # Update invoice balance
        old_balance = invoice.balance
        invoice.balance -= amount
        invoice.updated_at = now
        
        # Update invoice status if fully paid
        if invoice.balance == 0:
            invoice.status = InvoiceStatus.PAID.value
            changes.append(f"Invoice {invoice.id} marked as paid")
            
        changes.append(
            f"Added payment {amount} ({payment_method}), "
            f"balance updated from {old_balance} to {invoice.balance}"
        )
        
        return invoice, payment, changes
        
    @staticmethod
    def submit_invoice(
        invoice: Invoice,
        submission_date: Optional[datetime] = None,
        auto_submit: bool = False
    ) -> Tuple[Invoice, List[str]]:
        """
        Submit an invoice for processing.
        
        Args:
            invoice: Invoice to submit
            submission_date: Date of submission (defaults to now)
            auto_submit: Whether this is an automatic submission
            
        Returns:
            Tuple containing:
                - Updated invoice
                - List of changes made
        """
        changes = []
        now = datetime.now()
        submission_date = submission_date or now
        
        # Validate invoice state
        if invoice.status not in [InvoiceStatus.DRAFT.value, InvoiceStatus.PENDING.value]:
            raise ValueError(
                f"Cannot submit invoice in {invoice.status} status"
            )
            
        if not invoice.details:
            raise ValueError("Cannot submit invoice with no details")
            
        # Validate all details
        for detail in invoice.details:
            if detail.status == InvoiceStatus.CANCELLED.value:
                continue
                
            if detail.total_amount <= 0:
                raise ValueError(
                    f"Invalid amount {detail.total_amount} for detail {detail.id}"
                )
                
        # Update invoice
        old_status = invoice.status
        invoice.status = InvoiceStatus.SUBMITTED.value
        invoice.updated_at = now
        
        # Update all non-cancelled details
        for detail in invoice.details:
            if detail.status != InvoiceStatus.CANCELLED.value:
                detail.status = InvoiceStatus.SUBMITTED.value
                detail.updated_at = now
                
        changes.append(
            f"Invoice {invoice.id} submitted "
            f"(auto={auto_submit}), status changed from {old_status}"
        )
        
        return invoice, changes
        
    @staticmethod
    def update_pending_submissions(
        invoices: List[Invoice],
        submission_cutoff: datetime
    ) -> Tuple[List[Invoice], List[str]]:
        """
        Update status of pending invoice submissions.
        
        Args:
            invoices: List of invoices to check
            submission_cutoff: Cutoff date for submissions
            
        Returns:
            Tuple containing:
                - List of updated invoices
                - List of changes made
        """
        changes = []
        updated_invoices = []
        now = datetime.now()
        
        for invoice in invoices:
            if invoice.status != InvoiceStatus.SUBMITTED.value:
                continue
                
            # Check if past cutoff
            if invoice.updated_at <= submission_cutoff:
                invoice.status = InvoiceStatus.APPROVED.value
                invoice.updated_at = now
                
                # Update all submitted details
                for detail in invoice.details:
                    if detail.status == InvoiceStatus.SUBMITTED.value:
                        detail.status = InvoiceStatus.APPROVED.value
                        detail.updated_at = now
                        
                changes.append(
                    f"Invoice {invoice.id} auto-approved "
                    f"(submitted on {invoice.updated_at})"
                )
                updated_invoices.append(invoice)
                
        return updated_invoices, changes

    @classmethod
    def validate_status_transition(
        cls,
        current_status: str,
        new_status: str
    ) -> None:
        """
        Validate if a status transition is allowed.
        
        Args:
            current_status: Current status value
            new_status: New status value
            
        Raises:
            StatusTransitionError: If transition is invalid
        """
        if new_status not in cls._STATUS_TRANSITIONS.get(current_status, []):
            raise StatusTransitionError(
                f"Cannot transition from {current_status} to {new_status}"
            )
    
    @classmethod
    def update_invoice_status(
        cls,
        invoice: Invoice,
        new_status: str,
        update_details: bool = True,
        notes: Optional[str] = None
    ) -> Tuple[Invoice, List[str]]:
        """
        Update invoice status with validation.
        
        Args:
            invoice: Invoice to update
            new_status: New status value
            update_details: Whether to update detail statuses
            notes: Optional status change notes
            
        Returns:
            Tuple containing:
                - Updated invoice
                - List of changes made
        """
        changes = []
        now = datetime.now()
        
        # Validate transition
        cls.validate_status_transition(invoice.status, new_status)
        
        # Update invoice
        old_status = invoice.status
        invoice.status = new_status
        invoice.updated_at = now
        
        status_note = f" ({notes})" if notes else ""
        changes.append(
            f"Updated invoice {invoice.id} status from {old_status} "
            f"to {new_status}{status_note}"
        )
        
        # Update details if requested
        if update_details:
            for detail in invoice.details:
                if detail.status != InvoiceStatus.CANCELLED.value:
                    old_detail_status = detail.status
                    detail.status = new_status
                    detail.updated_at = now
                    changes.append(
                        f"Updated detail {detail.id} status from "
                        f"{old_detail_status} to {new_status}"
                    )
                    
        return invoice, changes
        
    @classmethod
    def cancel_invoice(
        cls,
        invoice: Invoice,
        reason: str,
        cancel_payments: bool = True
    ) -> Tuple[Invoice, List[str]]:
        """
        Cancel an invoice and optionally its payments.
        
        Args:
            invoice: Invoice to cancel
            reason: Cancellation reason
            cancel_payments: Whether to cancel pending payments
            
        Returns:
            Tuple containing:
                - Updated invoice
                - List of changes made
        """
        changes = []
        now = datetime.now()
        
        # Validate cancellation
        cls.validate_status_transition(
            invoice.status,
            InvoiceStatus.CANCELLED.value
        )
        
        # Cancel invoice
        old_status = invoice.status
        invoice.status = InvoiceStatus.CANCELLED.value
        invoice.updated_at = now
        changes.append(
            f"Cancelled invoice {invoice.id} (was {old_status}): {reason}"
        )
        
        # Cancel details
        for detail in invoice.details:
            if detail.status != InvoiceStatus.CANCELLED.value:
                old_detail_status = detail.status
                detail.status = InvoiceStatus.CANCELLED.value
                detail.updated_at = now
                changes.append(
                    f"Cancelled detail {detail.id} (was {old_detail_status})"
                )
                
        # Cancel pending payments if requested
        if cancel_payments:
            for payment in invoice.payments:
                if payment.status in [
                    PaymentStatus.PENDING.value,
                    PaymentStatus.PROCESSING.value
                ]:
                    old_payment_status = payment.status
                    payment.status = PaymentStatus.VOIDED.value
                    payment.updated_at = now
                    changes.append(
                        f"Voided payment {payment.id} (was {old_payment_status})"
                    )
                    
        return invoice, changes

    @classmethod
    def should_skip_invoice(
        cls,
        invoice: Invoice,
        check_details: bool = True,
        check_payments: bool = True,
        check_dates: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if an invoice should be skipped during processing.
        
        Args:
            invoice: Invoice to check
            check_details: Whether to check detail statuses
            check_payments: Whether to check payment statuses
            check_dates: Whether to check invoice dates
            
        Returns:
            Tuple containing:
                - Whether to skip the invoice
                - Reason for skipping (if applicable)
        """
        # Check invoice status
        if invoice.status in cls._SKIP_STATUSES:
            return True, f"Invoice status is {invoice.status}"
            
        # Check invoice dates
        if check_dates:
            now = datetime.now()
            
            if invoice.invoice_date > now:
                return True, "Invoice date is in the future"
                
            if invoice.due_date and invoice.due_date < now:
                return True, "Invoice is past due"
                
        # Check details
        if check_details and invoice.details:
            active_details = [
                d for d in invoice.details
                if d.status not in cls._SKIP_STATUSES
            ]
            
            if not active_details:
                return True, "No active details"
                
        # Check payments
        if check_payments and invoice.payments:
            pending_payments = [
                p for p in invoice.payments
                if p.status not in cls._SKIP_PAYMENT_STATUSES
            ]
            
            if pending_payments:
                return True, "Has pending payments"
                
        return False, None
        
    @classmethod
    def filter_processable_invoices(
        cls,
        invoices: List[Invoice],
        check_details: bool = True,
        check_payments: bool = True,
        check_dates: bool = True
    ) -> Tuple[List[Invoice], List[Tuple[Invoice, str]]]:
        """
        Filter a list of invoices to only those that should be processed.
        
        Args:
            invoices: List of invoices to filter
            check_details: Whether to check detail statuses
            check_payments: Whether to check payment statuses
            check_dates: Whether to check invoice dates
            
        Returns:
            Tuple containing:
                - List of processable invoices
                - List of skipped invoices with reasons
        """
        processable = []
        skipped = []
        
        for invoice in invoices:
            should_skip, reason = cls.should_skip_invoice(
                invoice=invoice,
                check_details=check_details,
                check_payments=check_payments,
                check_dates=check_dates
            )
            
            if should_skip:
                skipped.append((invoice, reason))
            else:
                processable.append(invoice)
                
        return processable, skipped
