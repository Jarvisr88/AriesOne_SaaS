"""
Unit tests for billing domain.
Tests models, services, and API routes.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import Session

from ..app.models.billing import (
    Invoice, RentalInvoice, Payment, Claim,
    DocumentStatus, PaymentStatus, ClaimStatus
)
from ..app.schemas.billing import (
    InvoiceCreate, InvoiceItemCreate,
    RentalInvoiceCreate, RentalInvoiceItemCreate,
    PaymentCreate, ClaimCreate, ClaimItemCreate
)
from ..app.services.billing import (
    InvoiceService, RentalInvoiceService,
    PaymentService, ClaimService
)

# Test data fixtures
@pytest.fixture
def invoice_create_data():
    """Sample invoice creation data."""
    return InvoiceCreate(
        document_number="INV-001",
        document_type="Invoice",
        document_date=date.today(),
        customer_id=1,
        order_id=1,
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("110.00"),
        items=[
            InvoiceItemCreate(
                item_id=1,
                quantity=1,
                unit_price=Decimal("100.00"),
                tax_rate=Decimal("10.00"),
                tax_amount=Decimal("10.00"),
                total_amount=Decimal("110.00")
            )
        ]
    )

@pytest.fixture
def rental_invoice_create_data():
    """Sample rental invoice creation data."""
    return RentalInvoiceCreate(
        document_number="RINV-001",
        document_type="RentalInvoice",
        document_date=date.today(),
        customer_id=1,
        order_id=1,
        subtotal=Decimal("50.00"),
        tax_amount=Decimal("5.00"),
        total_amount=Decimal("55.00"),
        rental_period_start=date.today(),
        rental_period_end=date.today() + timedelta(days=30),
        recurring_frequency="Monthly",
        items=[
            RentalInvoiceItemCreate(
                item_id=1,
                rental_start=date.today(),
                rental_end=date.today() + timedelta(days=30),
                rental_rate=Decimal("50.00"),
                quantity=1,
                tax_rate=Decimal("10.00"),
                tax_amount=Decimal("5.00"),
                total_amount=Decimal("55.00")
            )
        ]
    )

@pytest.fixture
def payment_create_data():
    """Sample payment creation data."""
    return PaymentCreate(
        payment_number="PAY-001",
        payment_date=date.today(),
        payment_method="CreditCard",
        customer_id=1,
        invoice_id=1,
        amount=Decimal("110.00")
    )

@pytest.fixture
def claim_create_data():
    """Sample claim creation data."""
    return ClaimCreate(
        document_number="CLM-001",
        document_type="Claim",
        document_date=date.today(),
        customer_id=1,
        claim_number="CLM001",
        payer_id=1,
        total_amount=Decimal("110.00"),
        items=[
            ClaimItemCreate(
                service_date=date.today(),
                hcpcs_code="E0601",
                quantity=1,
                charge_amount=Decimal("110.00")
            )
        ]
    )

# Model tests
class TestBillingModels:
    """Test billing domain models."""

    def test_invoice_creation(self, db: Session):
        """Test invoice model creation."""
        invoice = Invoice(
            document_number="INV-001",
            document_type="Invoice",
            document_date=date.today(),
            customer_id=1,
            total_amount=Decimal("110.00"),
            created_by_id=1
        )
        db.add(invoice)
        db.commit()
        
        assert invoice.id is not None
        assert invoice.document_number == "INV-001"
        assert invoice.status == DocumentStatus.DRAFT

    def test_rental_invoice_creation(self, db: Session):
        """Test rental invoice model creation."""
        invoice = RentalInvoice(
            document_number="RINV-001",
            document_type="RentalInvoice",
            document_date=date.today(),
            customer_id=1,
            total_amount=Decimal("55.00"),
            rental_period_start=date.today(),
            rental_period_end=date.today() + timedelta(days=30),
            recurring_frequency="Monthly",
            created_by_id=1
        )
        db.add(invoice)
        db.commit()
        
        assert invoice.id is not None
        assert invoice.document_number == "RINV-001"
        assert invoice.recurring_frequency == "Monthly"

# Service tests
class TestBillingServices:
    """Test billing domain services."""

    @pytest.mark.asyncio
    async def test_create_invoice(
        self,
        db: Session,
        invoice_create_data: InvoiceCreate
    ):
        """Test invoice creation service."""
        invoice = await InvoiceService.create_invoice(
            db=db,
            invoice=invoice_create_data,
            user_id=1
        )
        
        assert invoice.id is not None
        assert invoice.document_number == "INV-001"
        assert invoice.total_amount == Decimal("110.00")
        assert len(invoice.items) == 1

    @pytest.mark.asyncio
    async def test_create_rental_invoice(
        self,
        db: Session,
        rental_invoice_create_data: RentalInvoiceCreate
    ):
        """Test rental invoice creation service."""
        invoice = await RentalInvoiceService.create_rental_invoice(
            db=db,
            invoice=rental_invoice_create_data,
            user_id=1
        )
        
        assert invoice.id is not None
        assert invoice.document_number == "RINV-001"
        assert invoice.total_amount == Decimal("55.00")
        assert len(invoice.items) == 1

    @pytest.mark.asyncio
    async def test_create_payment(
        self,
        db: Session,
        payment_create_data: PaymentCreate
    ):
        """Test payment creation service."""
        payment = await PaymentService.create_payment(
            db=db,
            payment=payment_create_data,
            user_id=1
        )
        
        assert payment.id is not None
        assert payment.payment_number == "PAY-001"
        assert payment.amount == Decimal("110.00")
        assert payment.status == PaymentStatus.PENDING

# API route tests
class TestBillingRoutes:
    """Test billing domain API routes."""

    @pytest.mark.asyncio
    async def test_create_invoice_endpoint(
        self,
        app: FastAPI,
        client: AsyncClient,
        invoice_create_data: InvoiceCreate,
        auth_headers: dict
    ):
        """Test create invoice endpoint."""
        response = await client.post(
            "/billing/invoices",
            json=invoice_create_data.model_dump(),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["document_number"] == "INV-001"
        assert data["total_amount"] == "110.00"

    @pytest.mark.asyncio
    async def test_create_rental_invoice_endpoint(
        self,
        app: FastAPI,
        client: AsyncClient,
        rental_invoice_create_data: RentalInvoiceCreate,
        auth_headers: dict
    ):
        """Test create rental invoice endpoint."""
        response = await client.post(
            "/billing/rental-invoices",
            json=rental_invoice_create_data.model_dump(),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["document_number"] == "RINV-001"
        assert data["total_amount"] == "55.00"

    @pytest.mark.asyncio
    async def test_create_payment_endpoint(
        self,
        app: FastAPI,
        client: AsyncClient,
        payment_create_data: PaymentCreate,
        auth_headers: dict
    ):
        """Test create payment endpoint."""
        response = await client.post(
            "/billing/payments",
            json=payment_create_data.model_dump(),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["payment_number"] == "PAY-001"
        assert data["amount"] == "110.00"

    @pytest.mark.asyncio
    async def test_list_invoices_endpoint(
        self,
        app: FastAPI,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test list invoices endpoint."""
        response = await client.get(
            "/billing/invoices",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

# Integration tests
class TestBillingIntegration:
    """Test billing domain integration scenarios."""

    @pytest.mark.asyncio
    async def test_payment_updates_invoice_status(
        self,
        db: Session,
        invoice_create_data: InvoiceCreate,
        payment_create_data: PaymentCreate
    ):
        """Test that payment completion updates invoice status."""
        # Create invoice
        invoice = await InvoiceService.create_invoice(
            db=db,
            invoice=invoice_create_data,
            user_id=1
        )
        
        # Create and complete payment
        payment_create_data.invoice_id = invoice.id
        payment = await PaymentService.create_payment(
            db=db,
            payment=payment_create_data,
            user_id=1
        )
        
        # Update payment status to completed
        payment.status = PaymentStatus.COMPLETED
        db.commit()
        db.refresh(invoice)
        
        assert invoice.status == DocumentStatus.PAID

    @pytest.mark.asyncio
    async def test_partial_payment_updates_invoice_status(
        self,
        db: Session,
        invoice_create_data: InvoiceCreate,
        payment_create_data: PaymentCreate
    ):
        """Test that partial payment updates invoice status correctly."""
        # Create invoice
        invoice = await InvoiceService.create_invoice(
            db=db,
            invoice=invoice_create_data,
            user_id=1
        )
        
        # Create partial payment
        payment_create_data.invoice_id = invoice.id
        payment_create_data.amount = Decimal("50.00")
        payment = await PaymentService.create_payment(
            db=db,
            payment=payment_create_data,
            user_id=1
        )
        
        # Update payment status to completed
        payment.status = PaymentStatus.COMPLETED
        db.commit()
        db.refresh(invoice)
        
        assert invoice.status == DocumentStatus.PARTIAL
