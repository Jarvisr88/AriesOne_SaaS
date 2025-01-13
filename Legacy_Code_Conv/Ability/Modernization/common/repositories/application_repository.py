"""
Application Repository Module

This module provides data access for application management.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.common_models import Application
from ..models.database.common_models import ApplicationDB

class ApplicationRepository:
    """Repository for application data access."""

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
        """
        # Convert to DB model
        application_db = ApplicationDB(
            app_id=application.app_id,
            name=application.name,
            facility_state=application.facility_state,
            line_of_business=application.line_of_business,
            data_center=application.data_center,
            pptn_region=application.pptn_region
        )

        # Add to session
        db.add(application_db)
        await db.commit()
        await db.refresh(application_db)

        # Convert back to Pydantic model
        return Application.model_validate(application_db)

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
        stmt = select(ApplicationDB).where(ApplicationDB.app_id == app_id)
        result = await db.execute(stmt)
        application_db = result.scalar_one_or_none()

        if not application_db:
            return None

        return Application.model_validate(application_db)

    async def update_application(
        self,
        app_id: str,
        application: Application,
        db: AsyncSession
    ) -> Application:
        """
        Update application.
        
        Args:
            app_id: Application ID
            application: Updated application
            db: Database session
        
        Returns:
            Updated application
        
        Raises:
            ValueError: If application not found
        """
        stmt = select(ApplicationDB).where(ApplicationDB.app_id == app_id)
        result = await db.execute(stmt)
        application_db = result.scalar_one_or_none()

        if not application_db:
            raise ValueError(f"Application {app_id} not found")

        # Update fields
        application_db.name = application.name
        application_db.facility_state = application.facility_state
        application_db.line_of_business = application.line_of_business
        application_db.data_center = application.data_center
        application_db.pptn_region = application.pptn_region

        await db.commit()
        await db.refresh(application_db)

        return Application.model_validate(application_db)

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
        stmt = select(ApplicationDB).where(ApplicationDB.app_id == app_id)
        result = await db.execute(stmt)
        application_db = result.scalar_one_or_none()

        if not application_db:
            raise ValueError(f"Application {app_id} not found")

        await db.delete(application_db)
        await db.commit()

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
        query = select(ApplicationDB)

        if line_of_business:
            query = query.where(ApplicationDB.line_of_business == line_of_business)
        if data_center:
            query = query.where(ApplicationDB.data_center == data_center)

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        applications_db = result.scalars().all()

        return [Application.model_validate(app) for app in applications_db]
