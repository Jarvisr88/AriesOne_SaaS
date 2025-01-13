"""Services for handling deposits, claims, and purchase orders."""
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.misc_models import (
    DepositCreate,
    DepositResponse,
    DepositUpdate,
    DepositStatus,
    VoidSubmissionRequest,
    VoidSubmissionResponse,
    ClaimStatus,
    OrderItem,
    OrderSummary,
    ScanRequest,
    ScanResponse
)


class DepositService:
    """Service for handling deposit operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize deposit service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def create_deposit(
        self,
        deposit: DepositCreate,
        user_id: int
    ) -> DepositResponse:
        """Create new deposit.
        
        Args:
            deposit: Deposit details
            user_id: Creating user ID
            
        Returns:
            Created deposit
            
        Raises:
            HTTPException: If validation fails
        """
        # Verify customer exists
        if not await self.customer_exists(deposit.customer_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Verify order if provided
        if deposit.order_id and not await self.order_exists(deposit.order_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        try:
            # Create deposit record
            db_deposit = Deposit(
                customer_id=deposit.customer_id,
                order_id=deposit.order_id,
                amount=deposit.amount,
                payment_method=deposit.payment_method,
                reference=deposit.reference,
                notes=deposit.notes,
                status=DepositStatus.PENDING,
                created_by=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(db_deposit)
            await self.session.commit()
            
            return DepositResponse.from_orm(db_deposit)
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_deposit(
        self,
        deposit_id: int,
        update: DepositUpdate,
        user_id: int
    ) -> DepositResponse:
        """Update deposit status.
        
        Args:
            deposit_id: Deposit ID
            update: Status update
            user_id: Updating user ID
            
        Returns:
            Updated deposit
            
        Raises:
            HTTPException: If deposit not found
        """
        stmt = select(Deposit).where(Deposit.id == deposit_id)
        result = await self.session.execute(stmt)
        deposit = result.scalar_one_or_none()
        
        if not deposit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deposit not found"
            )
        
        try:
            deposit.status = update.status
            deposit.updated_at = datetime.utcnow()
            deposit.updated_by = user_id
            
            if update.reason:
                deposit.notes = (deposit.notes or '') + f"\nStatus update: {update.reason}"
            
            await self.session.commit()
            return DepositResponse.from_orm(deposit)
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


class ClaimService:
    """Service for handling claim operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize claim service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def void_submission(
        self,
        request: VoidSubmissionRequest,
        user_id: int
    ) -> VoidSubmissionResponse:
        """Void or replace claim submission.
        
        Args:
            request: Void request
            user_id: User ID
            
        Returns:
            Void response
            
        Raises:
            HTTPException: If claim not found or invalid
        """
        # Get claim
        stmt = select(Claim).where(Claim.number == request.claim_number)
        result = await self.session.execute(stmt)
        claim = result.scalar_one_or_none()
        
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        if claim.status != ClaimStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Claim is already {claim.status}"
            )
        
        try:
            # Update claim status
            claim.status = (
                ClaimStatus.REPLACED
                if request.action == ClaimAction.REPLACE
                else ClaimStatus.VOIDED
            )
            claim.void_reason = request.reason
            claim.replacement_claim = request.replacement_claim
            claim.updated_at = datetime.utcnow()
            claim.updated_by = user_id
            
            await self.session.commit()
            
            return VoidSubmissionResponse(
                claim_number=claim.number,
                action=request.action,
                status=claim.status,
                processed_at=datetime.utcnow(),
                replacement_claim=request.replacement_claim,
                reason=request.reason
            )
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


class PurchaseOrderService:
    """Service for handling purchase order operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize purchase order service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def process_scan(
        self,
        order_id: int,
        scan: ScanRequest,
        user_id: int
    ) -> ScanResponse:
        """Process barcode scan for order.
        
        Args:
            order_id: Order ID
            scan: Scan request
            user_id: User ID
            
        Returns:
            Scan response
            
        Raises:
            HTTPException: If item not found or invalid
        """
        # Get order item
        stmt = select(OrderItem).where(
            and_(
                OrderItem.order_id == order_id,
                OrderItem.barcode == scan.barcode
            )
        )
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in order"
            )
        
        try:
            # Update received quantity
            new_quantity = item.received_quantity + scan.quantity
            
            if new_quantity > item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Scan quantity exceeds order amount"
                )
            
            item.received_quantity = new_quantity
            item.status = (
                OrderItemStatus.RECEIVED
                if new_quantity == item.quantity
                else OrderItemStatus.PARTIAL
            )
            item.updated_at = datetime.utcnow()
            item.updated_by = user_id
            
            await self.session.commit()
            
            return ScanResponse(
                item=item,
                message="Item received successfully",
                status="success"
            )
            
        except HTTPException:
            raise
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_order_summary(self, order_id: int) -> OrderSummary:
        """Get order summary.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order summary
            
        Raises:
            HTTPException: If order not found
        """
        # Get order items
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        
        if not items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Calculate summary
        total_items = len(items)
        received_items = sum(
            1 for item in items
            if item.status == OrderItemStatus.RECEIVED
        )
        completion = (received_items / total_items) * 100 if total_items > 0 else 0
        
        status = (
            'completed'
            if completion == 100
            else 'in_progress'
            if completion > 0
            else 'pending'
        )
        
        last_updated = max(item.updated_at for item in items)
        
        return OrderSummary(
            id=order_id,
            total_items=total_items,
            received_items=received_items,
            completion_percentage=completion,
            status=status,
            last_updated=last_updated
        )
