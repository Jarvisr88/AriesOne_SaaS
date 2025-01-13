"""
Purchase order service implementation.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import (
    PurchaseOrder as PurchaseOrderDB,
    PurchaseOrderItem as PurchaseOrderItemDB
)
from .models import (
    PurchaseOrder,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    Item,
    ItemCreate
)


class PurchaseOrderService:
    """Service for managing purchase orders."""

    def __init__(self, db: Session):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db

    async def create_purchase_order(
        self,
        order: PurchaseOrderCreate,
        user: str
    ) -> PurchaseOrder:
        """Create new purchase order.
        
        Args:
            order: Order data
            user: Username
            
        Returns:
            Created order
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            # Calculate total
            total = sum(
                item.unit_price * item.quantity
                for item in order.items
            )
            
            # Create order
            db_order = PurchaseOrderDB(
                **order.dict(exclude={"items"}),
                status="pending",
                total_amount=total,
                created_by=user,
                updated_by=user
            )
            self.db.add(db_order)
            await self.db.flush()
            
            # Create items
            for item in order.items:
                db_item = PurchaseOrderItemDB(
                    purchase_order_id=db_order.id,
                    **item.dict()
                )
                self.db.add(db_item)
                
            await self.db.flush()
            await self.db.refresh(db_order)
            return PurchaseOrder.from_orm(db_order)
            
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def get_purchase_order(
        self,
        order_id: int
    ) -> Optional[PurchaseOrder]:
        """Get purchase order by ID.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order if found, None otherwise
        """
        order = await self.db.query(PurchaseOrderDB).filter(
            PurchaseOrderDB.id == order_id
        ).first()
        
        return PurchaseOrder.from_orm(order) if order else None

    async def update_purchase_order(
        self,
        order_id: int,
        order: PurchaseOrderUpdate,
        user: str
    ) -> Optional[PurchaseOrder]:
        """Update purchase order.
        
        Args:
            order_id: Order identifier
            order: Updated data
            user: Username
            
        Returns:
            Updated order if found
            
        Raises:
            HTTPException: If update fails
        """
        try:
            db_order = await self.db.query(PurchaseOrderDB).filter(
                PurchaseOrderDB.id == order_id
            ).first()
            
            if not db_order:
                return None
                
            update_data = order.dict(exclude_unset=True)
            update_data["updated_by"] = user
            update_data["updated_at"] = datetime.utcnow()
            
            for key, value in update_data.items():
                setattr(db_order, key, value)
                
            await self.db.flush()
            await self.db.refresh(db_order)
            return PurchaseOrder.from_orm(db_order)
            
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def receive_items(
        self,
        order_id: int,
        barcodes: List[str],
        user: str
    ) -> Optional[PurchaseOrder]:
        """Receive order items.
        
        Args:
            order_id: Order identifier
            barcodes: List of received barcodes
            user: Username
            
        Returns:
            Updated order if found
            
        Raises:
            HTTPException: If receiving fails
        """
        try:
            db_order = await self.db.query(PurchaseOrderDB).filter(
                PurchaseOrderDB.id == order_id
            ).first()
            
            if not db_order:
                return None
                
            # Get items
            items = await self.db.query(PurchaseOrderItemDB).filter(
                PurchaseOrderItemDB.purchase_order_id == order_id,
                PurchaseOrderItemDB.barcode.in_(barcodes)
            ).all()
            
            if not items:
                raise HTTPException(
                    status_code=400,
                    detail="No matching items found"
                )
                
            # Update order status
            all_items = await self.db.query(PurchaseOrderItemDB).filter(
                PurchaseOrderItemDB.purchase_order_id == order_id
            ).all()
            
            if len(items) == len(all_items):
                db_order.status = "received"
            else:
                db_order.status = "partial"
                
            db_order.updated_by = user
            db_order.updated_at = datetime.utcnow()
            
            await self.db.flush()
            await self.db.refresh(db_order)
            return PurchaseOrder.from_orm(db_order)
            
        except HTTPException:
            await self.db.rollback()
            raise
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def get_orders_by_vendor(
        self,
        vendor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseOrder]:
        """Get orders by vendor.
        
        Args:
            vendor_id: Vendor identifier
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of orders
        """
        orders = await self.db.query(PurchaseOrderDB).filter(
            PurchaseOrderDB.vendor_id == vendor_id
        ).offset(skip).limit(limit).all()
        
        return [PurchaseOrder.from_orm(o) for o in orders]

    async def get_pending_orders(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseOrder]:
        """Get pending orders.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of pending orders
        """
        orders = await self.db.query(PurchaseOrderDB).filter(
            PurchaseOrderDB.status == "pending"
        ).offset(skip).limit(limit).all()
        
        return [PurchaseOrder.from_orm(o) for o in orders]
