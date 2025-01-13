"""
Base service class for the Core module.
Provides common functionality and utilities for all services.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import HTTPException

from ..models.base import BaseDBModel, BaseSchema, AuditLog, ErrorLog

T = TypeVar('T', bound=BaseDBModel)
S = TypeVar('S', bound=BaseSchema)

class BaseService:
    """Base service class with common CRUD operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create(self, model_class: Type[T], schema: S) -> T:
        """Create a new database record."""
        try:
            db_item = model_class(**schema.dict(exclude_unset=True))
            self.db.add(db_item)
            await self.db.commit()
            await self.db.refresh(db_item)
            await self._log_audit(model_class.__tablename__, db_item.id, "create")
            return db_item
        except Exception as e:
            await self._log_error(str(e), "create_error", model_class.__tablename__)
            raise HTTPException(status_code=400, detail=str(e))

    async def get(self, model_class: Type[T], id: int) -> Optional[T]:
        """Get a record by ID."""
        try:
            query = select(model_class).where(model_class.id == id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self._log_error(str(e), "get_error", model_class.__tablename__)
            raise HTTPException(status_code=400, detail=str(e))

    async def update(self, model_class: Type[T], id: int, schema: S) -> Optional[T]:
        """Update a record by ID."""
        try:
            query = update(model_class).where(model_class.id == id)
            query = query.values(**schema.dict(exclude_unset=True))
            query = query.returning(model_class)
            result = await self.db.execute(query)
            await self.db.commit()
            updated_item = result.scalar_one_or_none()
            if updated_item:
                await self._log_audit(model_class.__tablename__, id, "update")
            return updated_item
        except Exception as e:
            await self._log_error(str(e), "update_error", model_class.__tablename__)
            raise HTTPException(status_code=400, detail=str(e))

    async def delete(self, model_class: Type[T], id: int) -> bool:
        """Delete a record by ID."""
        try:
            query = delete(model_class).where(model_class.id == id)
            result = await self.db.execute(query)
            await self.db.commit()
            if result.rowcount > 0:
                await self._log_audit(model_class.__tablename__, id, "delete")
                return True
            return False
        except Exception as e:
            await self._log_error(str(e), "delete_error", model_class.__tablename__)
            raise HTTPException(status_code=400, detail=str(e))

    async def list(
        self,
        model_class: Type[T],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """List records with optional filtering."""
        try:
            query = select(model_class)
            if filters:
                for key, value in filters.items():
                    if hasattr(model_class, key):
                        query = query.where(getattr(model_class, key) == value)
            query = query.offset(skip).limit(limit)
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self._log_error(str(e), "list_error", model_class.__tablename__)
            raise HTTPException(status_code=400, detail=str(e))

    async def _log_audit(
        self,
        entity_name: str,
        entity_id: int,
        action: str,
        changes: Optional[str] = None
    ) -> None:
        """Log audit information."""
        try:
            audit_log = AuditLog(
                entity_name=entity_name,
                entity_id=entity_id,
                action=action,
                changes=changes,
                user_id="system",  # TODO: Get from auth context
                timestamp=datetime.utcnow()
            )
            self.db.add(audit_log)
            await self.db.commit()
        except Exception as e:
            # Log error but don't raise exception for audit logging
            await self._log_error(str(e), "audit_log_error", "audit_log")

    async def _log_error(
        self,
        error_message: str,
        error_type: str,
        context: Optional[str] = None
    ) -> None:
        """Log error information."""
        try:
            error_log = ErrorLog(
                error_type=error_type,
                error_message=error_message,
                context=context,
                user_id="system",  # TODO: Get from auth context
                timestamp=datetime.utcnow()
            )
            self.db.add(error_log)
            await self.db.commit()
        except Exception:
            # If error logging fails, print to console as last resort
            print(f"Error logging failed: {error_type} - {error_message}")

    async def begin_transaction(self) -> None:
        """Begin a new transaction."""
        await self.db.begin()

    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        await self.db.commit()

    async def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        await self.db.rollback()
