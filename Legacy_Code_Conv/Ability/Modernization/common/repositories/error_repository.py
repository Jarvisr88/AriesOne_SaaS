"""
Error Repository Module

This module provides data access for error management.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.common_models import Error, ErrorDetail
from ..models.database.common_models import ErrorDB, ErrorDetailDB

class ErrorRepository:
    """Repository for error data access."""

    async def create_error(
        self,
        error: Error,
        db: AsyncSession
    ) -> Error:
        """
        Create a new error log.
        
        Args:
            error: Error to create
            db: Database session
        
        Returns:
            Created error
        """
        # Convert to DB model
        error_db = ErrorDB(
            error_id=error.error_id,
            source=error.source,
            severity=error.severity,
            message=error.message,
            stack_trace=error.stack_trace,
            timestamp=error.timestamp
        )

        # Add error details
        details_db = [
            ErrorDetailDB(
                error_id=error.error_id,
                code=detail.code,
                message=detail.message,
                field=detail.field,
                details=detail.details
            )
            for detail in error.details
        ]

        # Add to session
        db.add(error_db)
        db.add_all(details_db)
        await db.commit()
        await db.refresh(error_db)

        # Convert back to Pydantic model with details
        return await self.get_error(error.error_id, db)

    async def get_error(
        self,
        error_id: UUID,
        db: AsyncSession
    ) -> Optional[Error]:
        """
        Get error by ID.
        
        Args:
            error_id: Error ID
            db: Database session
        
        Returns:
            Error if found, None otherwise
        """
        # Get error
        stmt = select(ErrorDB).where(ErrorDB.error_id == error_id)
        result = await db.execute(stmt)
        error_db = result.scalar_one_or_none()

        if not error_db:
            return None

        # Get error details
        stmt = select(ErrorDetailDB).where(ErrorDetailDB.error_id == error_id)
        result = await db.execute(stmt)
        details_db = result.scalars().all()

        # Convert to Pydantic models
        details = [
            ErrorDetail(
                code=detail.code,
                message=detail.message,
                field=detail.field,
                details=detail.details
            )
            for detail in details_db
        ]

        return Error(
            error_id=error_db.error_id,
            source=error_db.source,
            severity=error_db.severity,
            message=error_db.message,
            stack_trace=error_db.stack_trace,
            timestamp=error_db.timestamp,
            details=details
        )

    async def list_errors(
        self,
        app_id: Optional[str] = None,
        severity: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession
    ) -> List[Error]:
        """
        List errors with optional filtering.
        
        Args:
            app_id: Optional application ID filter
            severity: Optional severity filter
            source: Optional source filter
            limit: Maximum number of results
            offset: Result offset
            db: Database session
        
        Returns:
            List of matching errors
        """
        query = select(ErrorDB)

        # Apply filters
        conditions = []
        if app_id:
            conditions.append(ErrorDB.app_id == app_id)
        if severity:
            conditions.append(ErrorDB.severity == severity)
        if source:
            conditions.append(ErrorDB.source == source)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        errors_db = result.scalars().all()

        # Convert to Pydantic models with details
        return [await self.get_error(error.error_id, db) for error in errors_db]

    async def delete_error(
        self,
        error_id: UUID,
        db: AsyncSession
    ) -> None:
        """
        Delete error.
        
        Args:
            error_id: Error ID
            db: Database session
        
        Raises:
            ValueError: If error not found
        """
        stmt = select(ErrorDB).where(ErrorDB.error_id == error_id)
        result = await db.execute(stmt)
        error_db = result.scalar_one_or_none()

        if not error_db:
            raise ValueError(f"Error {error_id} not found")

        await db.delete(error_db)
        await db.commit()

    async def clear_errors(
        self,
        app_id: str,
        before_date: Optional[str] = None,
        db: AsyncSession
    ) -> int:
        """
        Clear errors for an application.
        
        Args:
            app_id: Application ID
            before_date: Optional date filter
            db: Database session
        
        Returns:
            Number of errors cleared
        """
        query = select(ErrorDB).where(ErrorDB.app_id == app_id)

        if before_date:
            query = query.where(ErrorDB.timestamp < datetime.fromisoformat(before_date))

        result = await db.execute(query)
        errors = result.scalars().all()

        for error in errors:
            await db.delete(error)

        await db.commit()
        return len(errors)
