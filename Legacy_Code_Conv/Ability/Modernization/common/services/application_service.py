"""
Application Service Module

This module provides business logic for application management.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.common_models import Application
from ..repositories.application_repository import ApplicationRepository
from ..utils.validation import validate_application

class ApplicationService:
    """Service for application management."""

    def __init__(self, repository: ApplicationRepository):
        """Initialize application service."""
        self.repository = repository

    async def create_application(
        self,
        application: Application,
        db: AsyncSession
    ) -> Application:
        """
        Create a new application.
        
        Args:
            application: Application to create
            db: Database session
        
        Returns:
            Created application
        
        Raises:
            ValueError: If validation fails
        """
        # Validate application
        validate_application(application)

        # Check if application already exists
        existing = await self.repository.get_application(application.app_id, db)
        if existing:
            raise ValueError(f"Application {application.app_id} already exists")

        return await self.repository.create_application(application, db)

    async def get_application(
        self,
        app_id: str,
        db: AsyncSession
    ) -> Optional[Application]:
        """
        Get application by ID.
        
        Args:
            app_id: Application ID
            db: Database session
        
        Returns:
            Application if found, None otherwise
        """
        return await self.repository.get_application(app_id, db)

    async def update_application(
        self,
        app_id: str,
        application: Application,
        db: AsyncSession
    ) -> Application:
        """
        Update application configuration.
        
        Args:
            app_id: Application ID
            application: Updated application
            db: Database session
        
        Returns:
            Updated application
        
        Raises:
            ValueError: If validation fails or application not found
        """
        # Validate application
        validate_application(application)

        # Check if application exists
        existing = await self.repository.get_application(app_id, db)
        if not existing:
            raise ValueError(f"Application {app_id} not found")

        return await self.repository.update_application(app_id, application, db)

    async def delete_application(
        self,
        app_id: str,
        db: AsyncSession
    ) -> None:
        """
        Delete application.
        
        Args:
            app_id: Application ID
            db: Database session
        
        Raises:
            ValueError: If application not found
        """
        existing = await self.repository.get_application(app_id, db)
        if not existing:
            raise ValueError(f"Application {app_id} not found")

        await self.repository.delete_application(app_id, db)

    async def list_applications(
        self,
        line_of_business: Optional[str] = None,
        data_center: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession
    ) -> List[Application]:
        """
        List applications with optional filtering.
        
        Args:
            line_of_business: Optional line of business filter
            data_center: Optional data center filter
            limit: Maximum number of results
            offset: Result offset
            db: Database session
        
        Returns:
            List of matching applications
        """
        return await self.repository.list_applications(
            line_of_business=line_of_business,
            data_center=data_center,
            limit=limit,
            offset=offset,
            db=db
        )
