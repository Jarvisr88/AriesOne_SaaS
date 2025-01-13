"""
API routes for billing domain.
Provides endpoints for invoice, payment, and claim operations.
"""
from datetime import date
from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.billing import DocumentStatus, PaymentStatus, ClaimStatus
from ..schemas.billing import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    RentalInvoiceCreate, RentalInvoiceUpdate, RentalInvoiceResponse,
    PaymentCreate, PaymentUpdate, PaymentResponse,
    ClaimCreate, ClaimUpdate, ClaimResponse
)
from ..services.billing import (
    InvoiceService, RentalInvoiceService,
    PaymentService, ClaimService
)

router = APIRouter(prefix="/billing", tags=["billing"])

# Invoice routes
@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> InvoiceResponse:
    """Create a new invoice."""
    return await InvoiceService.create_invoice(
        db=db,
        invoice=invoice,
        user_id=current_user["id"]
    )

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int = Path(..., title="Invoice ID"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
) -> InvoiceResponse:
    """Get an invoice by ID."""
    return await InvoiceService.get_invoice(db=db, invoice_id=invoice_id)

@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    customer_id: Optional[int] = Query(None, title="Customer ID"),
    status: Optional[DocumentStatus] = Query(None, title="Invoice Status"),
    start_date: Optional[date] = Query(None, title="Start Date"),
    end_date: Optional[date] = Query(None, title="End Date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
) -> List[InvoiceResponse]:
    """List invoices with optional filtering."""
    invoices, _ = await InvoiceService.get_invoices(
        db=db,
        customer_id=customer_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return invoices

@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_update: InvoiceUpdate,
    invoice_id: int = Path(..., title="Invoice ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> InvoiceResponse:
    """Update an invoice."""
    return await InvoiceService.update_invoice(
        db=db,
        invoice_id=invoice_id,
        invoice_update=invoice_update,
        user_id=current_user["id"]
    )

# Rental Invoice routes
@router.post("/rental-invoices", response_model=RentalInvoiceResponse)
async def create_rental_invoice(
    invoice: RentalInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> RentalInvoiceResponse:
    """Create a new rental invoice."""
    return await RentalInvoiceService.create_rental_invoice(
        db=db,
        invoice=invoice,
        user_id=current_user["id"]
    )

@router.get("/rental-invoices/{invoice_id}", response_model=RentalInvoiceResponse)
async def get_rental_invoice(
    invoice_id: int = Path(..., title="Rental Invoice ID"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
) -> RentalInvoiceResponse:
    """Get a rental invoice by ID."""
    return await RentalInvoiceService.get_rental_invoice(
        db=db,
        invoice_id=invoice_id
    )

@router.patch("/rental-invoices/{invoice_id}", response_model=RentalInvoiceResponse)
async def update_rental_invoice(
    invoice_update: RentalInvoiceUpdate,
    invoice_id: int = Path(..., title="Rental Invoice ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> RentalInvoiceResponse:
    """Update a rental invoice."""
    return await RentalInvoiceService.update_rental_invoice(
        db=db,
        invoice_id=invoice_id,
        invoice_update=invoice_update,
        user_id=current_user["id"]
    )

# Payment routes
@router.post("/payments", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> PaymentResponse:
    """Create a new payment."""
    return await PaymentService.create_payment(
        db=db,
        payment=payment,
        user_id=current_user["id"]
    )

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int = Path(..., title="Payment ID"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
) -> PaymentResponse:
    """Get a payment by ID."""
    return await PaymentService.get_payment(db=db, payment_id=payment_id)

@router.patch("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_update: PaymentUpdate,
    payment_id: int = Path(..., title="Payment ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> PaymentResponse:
    """Update a payment."""
    return await PaymentService.update_payment(
        db=db,
        payment_id=payment_id,
        payment_update=payment_update,
        user_id=current_user["id"]
    )

# Claim routes
@router.post("/claims", response_model=ClaimResponse)
async def create_claim(
    claim: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> ClaimResponse:
    """Create a new insurance claim."""
    return await ClaimService.create_claim(
        db=db,
        claim=claim,
        user_id=current_user["id"]
    )

@router.get("/claims/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: int = Path(..., title="Claim ID"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
) -> ClaimResponse:
    """Get a claim by ID."""
    return await ClaimService.get_claim(db=db, claim_id=claim_id)

@router.get("/claims", response_model=List[ClaimResponse])
async def list_claims(
    customer_id: Optional[int] = Query(None, title="Customer ID"),
    payer_id: Optional[int] = Query(None, title="Payer ID"),
    status: Optional[ClaimStatus] = Query(None, title="Claim Status"),
    start_date: Optional[date] = Query(None, title="Start Date"),
    end_date: Optional[date] = Query(None, title="End Date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user)
) -> List[ClaimResponse]:
    """List claims with optional filtering."""
    claims, _ = await ClaimService.get_claims(
        db=db,
        customer_id=customer_id,
        payer_id=payer_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return claims

@router.patch("/claims/{claim_id}", response_model=ClaimResponse)
async def update_claim(
    claim_update: ClaimUpdate,
    claim_id: int = Path(..., title="Claim ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> ClaimResponse:
    """Update a claim."""
    return await ClaimService.update_claim(
        db=db,
        claim_id=claim_id,
        claim_update=claim_update,
        user_id=current_user["id"]
    )
