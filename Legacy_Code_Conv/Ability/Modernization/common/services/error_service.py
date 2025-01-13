"""
Error Service Module

This module provides business logic for error management.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.common_models import Error
from ..repositories.error_repository import ErrorRepository

class ErrorService:
    """Service for error management."""

    def __init__(self, repository: ErrorRepository):
        """Initialize error service."""
        self.repository = repository

    async def log_error(
        self,
        error: Error,
        db: AsyncSession
    ) -> Error:
        """
        Log a new error.
        
        Args:
            error: Error to log
            db: Database session
        
        Returns:
            Logged error
        """
        return await self.repository.create_error(error, db)

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
        return await self.repository.get_error(error_id, db)

    async def get_errors(
        self,
        app_id: Optional[str] = None,
        severity: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession
    ) -> List[Error]:
        """
        Get error logs with optional filtering.
        
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
        return await self.repository.list_errors(
            app_id=app_id,
            severity=severity,
            source=source,
            limit=limit,
            offset=offset,
            db=db
        )

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
        existing = await self.repository.get_error(error_id, db)
        if not existing:
            raise ValueError(f"Error {error_id} not found")

        await self.repository.delete_error(error_id, db)

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
        return await self.repository.clear_errors(
            app_id=app_id,
            before_date=before_date,
            db=db
        )
