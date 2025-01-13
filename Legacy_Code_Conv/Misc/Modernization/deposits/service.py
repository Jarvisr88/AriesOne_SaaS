"""
Deposit service implementation.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import Deposit as DepositDB
from .models import (
    Deposit,
    DepositCreate,
    DepositUpdate
)


class DepositService:
    """Service for managing deposits."""

    def __init__(self, db: Session):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db

    async def create_deposit(
        self,
        deposit: DepositCreate,
        user: str
    ) -> Deposit:
        """Create new deposit.
        
        Args:
            deposit: Deposit data
            user: Username
            
        Returns:
            Created deposit
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            db_deposit = DepositDB(
                **deposit.dict(),
                created_by=user,
                updated_by=user
            )
            self.db.add(db_deposit)
            await self.db.flush()
            await self.db.refresh(db_deposit)
            return Deposit.from_orm(db_deposit)
            
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

    async def get_deposit(
        self,
        deposit_id: int
    ) -> Optional[Deposit]:
        """Get deposit by ID.
        
        Args:
            deposit_id: Deposit identifier
            
        Returns:
            Deposit if found, None otherwise
        """
        deposit = await self.db.query(DepositDB).filter(
            DepositDB.id == deposit_id
        ).first()
        
        return Deposit.from_orm(deposit) if deposit else None

    async def update_deposit(
        self,
        deposit_id: int,
        deposit: DepositUpdate,
        user: str
    ) -> Optional[Deposit]:
        """Update deposit.
        
        Args:
            deposit_id: Deposit identifier
            deposit: Updated data
            user: Username
            
        Returns:
            Updated deposit if found
            
        Raises:
            HTTPException: If update fails
        """
        try:
            db_deposit = await self.db.query(DepositDB).filter(
                DepositDB.id == deposit_id
            ).first()
            
            if not db_deposit:
                return None
                
            update_data = deposit.dict(exclude_unset=True)
            update_data["updated_by"] = user
            update_data["updated_at"] = datetime.utcnow()
            
            for key, value in update_data.items():
                setattr(db_deposit, key, value)
                
            await self.db.flush()
            await self.db.refresh(db_deposit)
            return Deposit.from_orm(db_deposit)
            
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

    async def delete_deposit(
        self,
        deposit_id: int
    ) -> bool:
        """Delete deposit.
        
        Args:
            deposit_id: Deposit identifier
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            result = await self.db.query(DepositDB).filter(
                DepositDB.id == deposit_id
            ).delete()
            
            await self.db.flush()
            return bool(result)
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def get_deposits_by_customer(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Deposit]:
        """Get deposits by customer.
        
        Args:
            customer_id: Customer identifier
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of deposits
        """
        deposits = await self.db.query(DepositDB).filter(
            DepositDB.customer_id == customer_id
        ).offset(skip).limit(limit).all()
        
        return [Deposit.from_orm(d) for d in deposits]

    async def get_deposits_by_order(
        self,
        order_id: int
    ) -> List[Deposit]:
        """Get deposits by order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            List of deposits
        """
        deposits = await self.db.query(DepositDB).filter(
            DepositDB.order_id == order_id
        ).all()
        
        return [Deposit.from_orm(d) for d in deposits]
