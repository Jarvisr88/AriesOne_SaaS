"""
Core API Integration Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides API integration functionality.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..security import (AuthenticationService, AuthorizationService,
                       get_current_active_user, require_permission)
from ..utils.logging import CoreLogger
from .database import DatabaseIntegration
from .event_bus import Event, get_event_bus

logger = CoreLogger(__name__)
router = APIRouter(prefix="/api/v1/core", tags=["core"])


@router.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        # Check database health
        session = request.app.state.db_session
        db_integration = DatabaseIntegration(session)
        db_health = await db_integration.health_check()
        
        # Check event bus health
        event_bus = await get_event_bus()
        event_health = await event_bus.health_check()
        
        return {
            "status": "healthy" if all(h["status"] == "healthy" for h in
                                    [db_health, event_health]) else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": db_health,
                "event_bus": event_health
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/metrics")
@require_permission("metrics", "read")
async def get_metrics(
    request: Request,
    current_user = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get system metrics."""
    try:
        # Get database metrics
        session = request.app.state.db_session
        db_integration = DatabaseIntegration(session)
        db_metrics = await db_integration.get_metrics()
        
        # Add other metrics here
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_metrics
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/events")
@require_permission("events", "publish")
async def publish_event(
    event_type: str,
    payload: Dict[str, Any],
    routing_key: str,
    current_user = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Publish event to event bus."""
    try:
        event = Event(event_type, payload)
        event_bus = await get_event_bus()
        await event_bus.publish(event, routing_key)
        
        return {
            "status": "success",
            "event_id": str(event.id),
            "timestamp": event.timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to publish event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/schema/{table_name}")
@require_permission("schema", "read")
async def get_table_schema(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get database table schema."""
    try:
        db_integration = DatabaseIntegration(session)
        schema = await db_integration.get_table_schema(table_name)
        
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table {table_name} not found"
            )
        
        return schema
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get schema: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/backup/{table_name}")
@require_permission("backup", "create")
async def backup_table(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Create table backup."""
    try:
        db_integration = DatabaseIntegration(session)
        success = await db_integration.backup_table(table_name)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to backup table {table_name}"
            )
        
        return {
            "status": "success",
            "message": f"Table {table_name} backed up successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to backup table: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
