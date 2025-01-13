"""
Void service implementation.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import Void as VoidDB
from .models import (
    Void,
    VoidCreate,
    VoidUpdate
)


class VoidService:
    """Service for managing voids."""

    def __init__(self, db: Session):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db

    async def create_void(
        self,
        void: VoidCreate,
        user: str
    ) -> Void:
        """Create new void.
        
        Args:
            void: Void data
            user: Username
            
        Returns:
            Created void
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            db_void = VoidDB(
                **void.dict(),
                status="pending",
                created_by=user,
                updated_by=user
            )
            self.db.add(db_void)
            await self.db.flush()
            await self.db.refresh(db_void)
            return Void.from_orm(db_void)
            
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

    async def get_void(
        self,
        void_id: int
    ) -> Optional[Void]:
        """Get void by ID.
        
        Args:
            void_id: Void identifier
            
        Returns:
            Void if found, None otherwise
        """
        void = await self.db.query(VoidDB).filter(
            VoidDB.id == void_id
        ).first()
        
        return Void.from_orm(void) if void else None

    async def update_void(
        self,
        void_id: int,
        void: VoidUpdate,
        user: str
    ) -> Optional[Void]:
        """Update void.
        
        Args:
            void_id: Void identifier
            void: Updated data
            user: Username
            
        Returns:
            Updated void if found
            
        Raises:
            HTTPException: If update fails
        """
        try:
            db_void = await self.db.query(VoidDB).filter(
                VoidDB.id == void_id
            ).first()
            
            if not db_void:
                return None
                
            update_data = void.dict(exclude_unset=True)
            update_data["updated_by"] = user
            update_data["updated_at"] = datetime.utcnow()
            
            for key, value in update_data.items():
                setattr(db_void, key, value)
                
            await self.db.flush()
            await self.db.refresh(db_void)
            return Void.from_orm(db_void)
            
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

    async def process_void(
        self,
        void_id: int,
        status: str,
        user: str
    ) -> Optional[Void]:
        """Process void request.
        
        Args:
            void_id: Void identifier
            status: New status
            user: Username
            
        Returns:
            Updated void if found
            
        Raises:
            HTTPException: If processing fails
        """
        try:
            db_void = await self.db.query(VoidDB).filter(
                VoidDB.id == void_id
            ).first()
            
            if not db_void:
                return None
                
            db_void.status = status
            db_void.updated_by = user
            db_void.updated_at = datetime.utcnow()
            
            await self.db.flush()
            await self.db.refresh(db_void)
            return Void.from_orm(db_void)
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    async def get_voids_by_claim(
        self,
        claim_number: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Void]:
        """Get voids by claim number.
        
        Args:
            claim_number: Claim number
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of voids
        """
        voids = await self.db.query(VoidDB).filter(
            VoidDB.claim_number == claim_number
        ).offset(skip).limit(limit).all()
        
        return [Void.from_orm(v) for v in voids]

    async def get_pending_voids(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Void]:
        """Get pending voids.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of pending voids
        """
        voids = await self.db.query(VoidDB).filter(
            VoidDB.status == "pending"
        ).offset(skip).limit(limit).all()
        
        return [Void.from_orm(v) for v in voids]
