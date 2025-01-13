"""API router for miscellaneous operations."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.misc_models import (
    DepositCreate,
    DepositResponse,
    DepositUpdate,
    VoidSubmissionRequest,
    VoidSubmissionResponse,
    OrderItem,
    OrderSummary,
    ScanRequest,
    ScanResponse
)
from ..services.misc_service import (
    DepositService,
    ClaimService,
    PurchaseOrderService
)
from ...Core.Modernization.dependencies import (
    get_session,
    get_current_user
)


router = APIRouter()


# Deposit endpoints
@router.post(
    "/deposits",
    response_model=DepositResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create deposit",
    description="Create new customer deposit"
)
async def create_deposit(
    deposit: DepositCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> DepositResponse:
    """Create new deposit.
    
    Args:
        deposit: Deposit details
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Created deposit
        
    Raises:
        HTTPException: If validation fails
    """
    if not current_user.has_permission('deposits.create'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create deposits"
        )
    
    service = DepositService(session)
    return await service.create_deposit(deposit, current_user.id)


@router.put(
    "/deposits/{deposit_id}/status",
    response_model=DepositResponse,
    summary="Update deposit status",
    description="Update status of existing deposit"
)
async def update_deposit_status(
    deposit_id: int = Path(..., description="Deposit identifier"),
    update: DepositUpdate = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> DepositResponse:
    """Update deposit status.
    
    Args:
        deposit_id: Deposit ID
        update: Status update
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Updated deposit
        
    Raises:
        HTTPException: If deposit not found
    """
    if not current_user.has_permission('deposits.update'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update deposits"
        )
    
    service = DepositService(session)
    return await service.update_deposit(deposit_id, update, current_user.id)


# Claim endpoints
@router.post(
    "/claims/{claim_number}/void",
    response_model=VoidSubmissionResponse,
    summary="Void claim",
    description="Void or replace existing claim"
)
async def void_claim(
    claim_number: str = Path(..., description="Claim number"),
    request: VoidSubmissionRequest = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> VoidSubmissionResponse:
    """Void or replace claim.
    
    Args:
        claim_number: Claim number
        request: Void request
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Void response
        
    Raises:
        HTTPException: If claim not found
    """
    if not current_user.has_permission('claims.void'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to void claims"
        )
    
    service = ClaimService(session)
    return await service.void_submission(request, current_user.id)


# Purchase order endpoints
@router.post(
    "/purchase-orders/{order_id}/scan",
    response_model=ScanResponse,
    summary="Process scan",
    description="Process barcode scan for order"
)
async def process_scan(
    order_id: int = Path(..., description="Order identifier"),
    scan: ScanRequest = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> ScanResponse:
    """Process barcode scan.
    
    Args:
        order_id: Order ID
        scan: Scan request
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Scan response
        
    Raises:
        HTTPException: If item not found
    """
    if not current_user.has_permission('orders.receive'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to receive orders"
        )
    
    service = PurchaseOrderService(session)
    return await service.process_scan(order_id, scan, current_user.id)


@router.get(
    "/purchase-orders/{order_id}",
    response_model=OrderSummary,
    summary="Get order summary",
    description="Get summary of purchase order"
)
async def get_order_summary(
    order_id: int = Path(..., description="Order identifier"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> OrderSummary:
    """Get order summary.
    
    Args:
        order_id: Order ID
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Order summary
        
    Raises:
        HTTPException: If order not found
    """
    if not current_user.has_permission('orders.view'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view orders"
        )
    
    service = PurchaseOrderService(session)
    return await service.get_order_summary(order_id)
