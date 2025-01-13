"""
Service layer for billing domain.
Implements business logic for billing operations.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
from fastapi import HTTPException

from ..models.billing import (
    Invoice, RentalInvoice, InvoiceItem, RentalInvoiceItem,
    Payment, Claim, ClaimItem, DocumentStatus, PaymentStatus, ClaimStatus
)
from ..schemas.billing import (
    InvoiceCreate, InvoiceUpdate, InvoiceItemCreate, InvoiceItemUpdate,
    RentalInvoiceCreate, RentalInvoiceUpdate,
    RentalInvoiceItemCreate, RentalInvoiceItemUpdate,
    PaymentCreate, PaymentUpdate,
    ClaimCreate, ClaimUpdate, ClaimItemCreate, ClaimItemUpdate
)

class InvoiceService:
    """Service for invoice operations."""

    @staticmethod
    async def create_invoice(db: Session, invoice: InvoiceCreate, user_id: int) -> Invoice:
        """Create a new invoice with items."""
        # Calculate totals
        subtotal = sum(item.total_amount for item in invoice.items)
        tax_amount = sum(item.tax_amount for item in invoice.items)
        total_amount = subtotal + tax_amount - invoice.discount_amount

        # Create invoice
        db_invoice = Invoice(
            **invoice.model_dump(exclude={'items'}),
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_invoice)
        await db.flush()

        # Create invoice items
        for item in invoice.items:
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                **item.model_dump(),
                created_by_id=user_id,
                last_update_user_id=user_id
            )
            db.add(db_item)
        
        await db.flush()
        return db_invoice

    @staticmethod
    async def get_invoice(db: Session, invoice_id: int) -> Invoice:
        """Get an invoice by ID."""
        invoice = await db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice

    @staticmethod
    async def get_invoices(
        db: Session,
        customer_id: Optional[int] = None,
        status: Optional[DocumentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Invoice], int]:
        """Get invoices with filtering and pagination."""
        query = db.query(Invoice)
        
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        if status:
            query = query.filter(Invoice.status == status)
        if start_date:
            query = query.filter(Invoice.document_date >= start_date)
        if end_date:
            query = query.filter(Invoice.document_date <= end_date)

        total = await query.count()
        invoices = await query.offset(skip).limit(limit).all()
        return invoices, total

    @staticmethod
    async def update_invoice(
        db: Session,
        invoice_id: int,
        invoice_update: InvoiceUpdate,
        user_id: int
    ) -> Invoice:
        """Update an invoice."""
        db_invoice = await InvoiceService.get_invoice(db, invoice_id)
        update_data = invoice_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_invoice, field, value)
        
        db_invoice.last_update_user_id = user_id
        db_invoice.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_invoice

class RentalInvoiceService:
    """Service for rental invoice operations."""

    @staticmethod
    async def create_rental_invoice(
        db: Session,
        invoice: RentalInvoiceCreate,
        user_id: int
    ) -> RentalInvoice:
        """Create a new rental invoice with items."""
        # Calculate totals
        subtotal = sum(item.total_amount for item in invoice.items)
        tax_amount = sum(item.tax_amount for item in invoice.items)
        total_amount = subtotal + tax_amount - invoice.discount_amount

        # Create invoice
        db_invoice = RentalInvoice(
            **invoice.model_dump(exclude={'items'}),
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_invoice)
        await db.flush()

        # Create invoice items
        for item in invoice.items:
            db_item = RentalInvoiceItem(
                invoice_id=db_invoice.id,
                **item.model_dump(),
                created_by_id=user_id,
                last_update_user_id=user_id
            )
            db.add(db_item)
        
        await db.flush()
        return db_invoice

    @staticmethod
    async def get_rental_invoice(db: Session, invoice_id: int) -> RentalInvoice:
        """Get a rental invoice by ID."""
        invoice = await db.query(RentalInvoice).filter(
            RentalInvoice.id == invoice_id
        ).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Rental invoice not found")
        return invoice

    @staticmethod
    async def update_rental_invoice(
        db: Session,
        invoice_id: int,
        invoice_update: RentalInvoiceUpdate,
        user_id: int
    ) -> RentalInvoice:
        """Update a rental invoice."""
        db_invoice = await RentalInvoiceService.get_rental_invoice(db, invoice_id)
        update_data = invoice_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_invoice, field, value)
        
        db_invoice.last_update_user_id = user_id
        db_invoice.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_invoice

class PaymentService:
    """Service for payment operations."""

    @staticmethod
    async def create_payment(
        db: Session,
        payment: PaymentCreate,
        user_id: int
    ) -> Payment:
        """Create a new payment."""
        db_payment = Payment(
            **payment.model_dump(),
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_payment)
        await db.flush()

        # Update invoice status if payment is completed
        if payment.status == PaymentStatus.COMPLETED:
            if payment.invoice_id:
                await PaymentService._update_invoice_status(
                    db, payment.invoice_id, payment.amount
                )
            elif payment.rental_invoice_id:
                await PaymentService._update_rental_invoice_status(
                    db, payment.rental_invoice_id, payment.amount
                )

        return db_payment

    @staticmethod
    async def _update_invoice_status(
        db: Session,
        invoice_id: int,
        payment_amount: Decimal
    ) -> None:
        """Update invoice status based on payment."""
        invoice = await db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            return

        total_paid = payment_amount + sum(
            p.amount for p in invoice.payments 
            if p.status == PaymentStatus.COMPLETED
        )

        if total_paid >= invoice.total_amount:
            invoice.status = DocumentStatus.PAID
        elif total_paid > 0:
            invoice.status = DocumentStatus.PARTIAL
        await db.flush()

    @staticmethod
    async def _update_rental_invoice_status(
        db: Session,
        invoice_id: int,
        payment_amount: Decimal
    ) -> None:
        """Update rental invoice status based on payment."""
        invoice = await db.query(RentalInvoice).filter(
            RentalInvoice.id == invoice_id
        ).first()
        if not invoice:
            return

        total_paid = payment_amount + sum(
            p.amount for p in invoice.payments 
            if p.status == PaymentStatus.COMPLETED
        )

        if total_paid >= invoice.total_amount:
            invoice.status = DocumentStatus.PAID
        elif total_paid > 0:
            invoice.status = DocumentStatus.PARTIAL
        await db.flush()

    @staticmethod
    async def get_payment(db: Session, payment_id: int) -> Payment:
        """Get a payment by ID."""
        payment = await db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment

    @staticmethod
    async def update_payment(
        db: Session,
        payment_id: int,
        payment_update: PaymentUpdate,
        user_id: int
    ) -> Payment:
        """Update a payment."""
        db_payment = await PaymentService.get_payment(db, payment_id)
        update_data = payment_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_payment, field, value)
        
        db_payment.last_update_user_id = user_id
        db_payment.last_update_datetime = datetime.utcnow()
        
        # Update invoice status if payment status changed to completed
        if (payment_update.status == PaymentStatus.COMPLETED and 
            db_payment.status != PaymentStatus.COMPLETED):
            if db_payment.invoice_id:
                await PaymentService._update_invoice_status(
                    db, db_payment.invoice_id, db_payment.amount
                )
            elif db_payment.rental_invoice_id:
                await PaymentService._update_rental_invoice_status(
                    db, db_payment.rental_invoice_id, db_payment.amount
                )
        
        await db.flush()
        return db_payment

class ClaimService:
    """Service for insurance claim operations."""

    @staticmethod
    async def create_claim(db: Session, claim: ClaimCreate, user_id: int) -> Claim:
        """Create a new insurance claim with items."""
        # Calculate totals
        total_amount = sum(item.charge_amount for item in claim.items)

        # Create claim
        db_claim = Claim(
            **claim.model_dump(exclude={'items'}),
            total_amount=total_amount,
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_claim)
        await db.flush()

        # Create claim items
        for item in claim.items:
            db_item = ClaimItem(
                claim_id=db_claim.id,
                **item.model_dump(),
                created_by_id=user_id,
                last_update_user_id=user_id
            )
            db.add(db_item)
        
        await db.flush()
        return db_claim

    @staticmethod
    async def get_claim(db: Session, claim_id: int) -> Claim:
        """Get a claim by ID."""
        claim = await db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        return claim

    @staticmethod
    async def get_claims(
        db: Session,
        customer_id: Optional[int] = None,
        payer_id: Optional[int] = None,
        status: Optional[ClaimStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Claim], int]:
        """Get claims with filtering and pagination."""
        query = db.query(Claim)
        
        if customer_id:
            query = query.filter(Claim.customer_id == customer_id)
        if payer_id:
            query = query.filter(Claim.payer_id == payer_id)
        if status:
            query = query.filter(Claim.claim_status == status)
        if start_date:
            query = query.filter(Claim.document_date >= start_date)
        if end_date:
            query = query.filter(Claim.document_date <= end_date)

        total = await query.count()
        claims = await query.offset(skip).limit(limit).all()
        return claims, total

    @staticmethod
    async def update_claim(
        db: Session,
        claim_id: int,
        claim_update: ClaimUpdate,
        user_id: int
    ) -> Claim:
        """Update a claim."""
        db_claim = await ClaimService.get_claim(db, claim_id)
        update_data = claim_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_claim, field, value)
        
        db_claim.last_update_user_id = user_id
        db_claim.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_claim
