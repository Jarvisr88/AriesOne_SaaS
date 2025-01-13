"""
Common API Endpoints Module

This module provides FastAPI endpoints for common operations.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.common_models import (
    Application,
    Credential,
    Error,
    ErrorDetail
)
from ..services.application_service import ApplicationService
from ..services.error_service import ErrorService
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/common", tags=["common"])

# Application endpoints
@router.post("/applications", response_model=Application)
async def create_application(
    application: Application,
    current_user = Depends(get_current_user),
    app_service: ApplicationService = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Application:
    """Create a new application configuration."""
    try:
        return await app_service.create_application(application, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/applications/{app_id}", response_model=Application)
async def get_application(
    app_id: str,
    current_user = Depends(get_current_user),
    app_service: ApplicationService = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Application:
    """Get application configuration by ID."""
    app = await app_service.get_application(app_id, db)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.put("/applications/{app_id}", response_model=Application)
async def update_application(
    app_id: str,
    application: Application,
    current_user = Depends(get_current_user),
    app_service: ApplicationService = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Application:
    """Update application configuration."""
    try:
        return await app_service.update_application(app_id, application, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Error endpoints
@router.post("/errors", response_model=Error)
async def log_error(
    error: Error,
    current_user = Depends(get_current_user),
    error_service: ErrorService = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Error:
    """Log a new error."""
    return await error_service.log_error(error, db)

@router.get("/errors", response_model=List[Error])
async def get_errors(
    app_id: Optional[str] = None,
    severity: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    current_user = Depends(get_current_user),
    error_service: ErrorService = Depends(),
    db: AsyncSession = Depends(get_db)
) -> List[Error]:
    """Get error logs with optional filtering."""
    return await error_service.get_errors(
        app_id=app_id,
        severity=severity,
        source=source,
        limit=limit,
        offset=offset,
        db=db
    )

@router.get("/errors/{error_id}", response_model=Error)
async def get_error(
    error_id: UUID,
    current_user = Depends(get_current_user),
    error_service: ErrorService = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Error:
    """Get error details by ID."""
    error = await error_service.get_error(error_id, db)
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    return error
