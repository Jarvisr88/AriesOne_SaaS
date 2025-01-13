"""Test cases for miscellaneous operations."""
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from ..models.misc_models import (
    DepositCreate,
    DepositResponse,
    DepositUpdate,
    DepositStatus,
    PaymentMethod,
    VoidSubmissionRequest,
    VoidSubmissionResponse,
    ClaimAction,
    ClaimStatus,
    OrderItem,
    OrderItemStatus,
    ScanRequest,
    ScanResponse,
    OrderSummary
)
from ..services.misc_service import (
    DepositService,
    ClaimService,
    PurchaseOrderService
)


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_user():
    """Create mock user."""
    return AsyncMock(
        id=1,
        has_permission=lambda x: True
    )


class TestDepositService:
    """Test cases for deposit service."""
    
    @pytest.mark.asyncio
    async def test_create_deposit_success(self, mock_session, mock_user):
        """Test successful deposit creation."""
        # Setup
        service = DepositService(mock_session)
        deposit = DepositCreate(
            customer_id=1,
            amount=Decimal('100.00'),
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        # Mock customer check
        service.customer_exists = AsyncMock(return_value=True)
        
        # Execute
        response = await service.create_deposit(deposit, mock_user.id)
        
        # Verify
        assert isinstance(response, DepositResponse)
        assert response.customer_id == deposit.customer_id
        assert response.amount == deposit.amount
        assert response.status == DepositStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_create_deposit_invalid_customer(self, mock_session, mock_user):
        """Test deposit creation with invalid customer."""
        # Setup
        service = DepositService(mock_session)
        deposit = DepositCreate(
            customer_id=999,
            amount=Decimal('100.00'),
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        # Mock customer check
        service.customer_exists = AsyncMock(return_value=False)
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc:
            await service.create_deposit(deposit, mock_user.id)
        assert exc.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_deposit_success(self, mock_session, mock_user):
        """Test successful deposit status update."""
        # Setup
        service = DepositService(mock_session)
        update = DepositUpdate(
            status=DepositStatus.COMPLETED,
            reason="Payment received"
        )
        
        # Mock deposit query
        mock_deposit = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_deposit
        mock_session.execute.return_value = mock_result
        
        # Execute
        response = await service.update_deposit(1, update, mock_user.id)
        
        # Verify
        assert mock_deposit.status == DepositStatus.COMPLETED
        assert mock_deposit.updated_by == mock_user.id


class TestClaimService:
    """Test cases for claim service."""
    
    @pytest.mark.asyncio
    async def test_void_submission_success(self, mock_session, mock_user):
        """Test successful claim void."""
        # Setup
        service = ClaimService(mock_session)
        request = VoidSubmissionRequest(
            claim_number="CLM123",
            action=ClaimAction.VOID,
            reason="Test void"
        )
        
        # Mock claim query
        mock_claim = AsyncMock(status=ClaimStatus.ACTIVE)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_claim
        mock_session.execute.return_value = mock_result
        
        # Execute
        response = await service.void_submission(request, mock_user.id)
        
        # Verify
        assert isinstance(response, VoidSubmissionResponse)
        assert response.claim_number == request.claim_number
        assert response.status == ClaimStatus.VOIDED
        assert response.reason == request.reason
    
    @pytest.mark.asyncio
    async def test_void_submission_not_found(self, mock_session, mock_user):
        """Test void submission with non-existent claim."""
        # Setup
        service = ClaimService(mock_session)
        request = VoidSubmissionRequest(
            claim_number="CLM999",
            action=ClaimAction.VOID,
            reason="Test void"
        )
        
        # Mock claim query
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc:
            await service.void_submission(request, mock_user.id)
        assert exc.value.status_code == 404


class TestPurchaseOrderService:
    """Test cases for purchase order service."""
    
    @pytest.mark.asyncio
    async def test_process_scan_success(self, mock_session, mock_user):
        """Test successful barcode scan."""
        # Setup
        service = PurchaseOrderService(mock_session)
        scan = ScanRequest(
            barcode="12345",
            quantity=1
        )
        
        # Mock item query
        mock_item = AsyncMock(
            order_id=1,
            quantity=10,
            received_quantity=0,
            status=OrderItemStatus.PENDING
        )
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_item
        mock_session.execute.return_value = mock_result
        
        # Execute
        response = await service.process_scan(1, scan, mock_user.id)
        
        # Verify
        assert isinstance(response, ScanResponse)
        assert response.item.received_quantity == 1
        assert response.item.status == OrderItemStatus.PARTIAL
        assert response.status == "success"
    
    @pytest.mark.asyncio
    async def test_process_scan_quantity_exceeded(self, mock_session, mock_user):
        """Test scan with quantity exceeding order."""
        # Setup
        service = PurchaseOrderService(mock_session)
        scan = ScanRequest(
            barcode="12345",
            quantity=2
        )
        
        # Mock item query
        mock_item = AsyncMock(
            order_id=1,
            quantity=1,
            received_quantity=0,
            status=OrderItemStatus.PENDING
        )
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_item
        mock_session.execute.return_value = mock_result
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc:
            await service.process_scan(1, scan, mock_user.id)
        assert exc.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_order_summary(self, mock_session):
        """Test order summary retrieval."""
        # Setup
        service = PurchaseOrderService(mock_session)
        mock_items = [
            AsyncMock(
                status=OrderItemStatus.RECEIVED,
                updated_at=datetime.utcnow()
            ),
            AsyncMock(
                status=OrderItemStatus.PARTIAL,
                updated_at=datetime.utcnow()
            ),
            AsyncMock(
                status=OrderItemStatus.PENDING,
                updated_at=datetime.utcnow()
            )
        ]
        
        # Mock items query
        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = mock_items
        mock_session.execute.return_value = mock_result
        
        # Execute
        response = await service.get_order_summary(1)
        
        # Verify
        assert isinstance(response, OrderSummary)
        assert response.total_items == 3
        assert response.received_items == 1
        assert response.completion_percentage == pytest.approx(33.33)
