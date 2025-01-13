"""
Event API Endpoints Module

This module provides FastAPI endpoints for managing grid source events.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..models.events import (
    CreateSourceEventArgs,
    GridSource,
    SourceCreatedEvent,
    SourceEventContext,
    GridSourceType
)
from ..services.event_service import EventService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/sources", response_model=CreateSourceEventArgs[GridSource])
async def create_source(
    source_type: GridSourceType,
    schema: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> CreateSourceEventArgs[GridSource]:
    """
    Create a new grid source.
    
    Args:
        source_type: Type of grid source to create
        schema: Schema definition for the source
        current_user: The current authenticated user
        
    Returns:
        CreateSourceEventArgs instance with created source
    """
    try:
        # Create event context
        context = SourceEventContext(
            user_id=current_user.id,
            session_id=current_user.session_id
        )
        
        # Create source
        event_service = EventService[GridSource]()
        return await event_service.create_source(
            source_type=source_type,
            schema=schema,
            context=context
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create source: {str(e)}"
        )

@router.get("/sources/{source_id}", response_model=GridSource)
async def get_source(
    source_id: str,
    current_user: User = Depends(get_current_user)
) -> GridSource:
    """
    Get a grid source by ID.
    
    Args:
        source_id: ID of the source to retrieve
        current_user: The current authenticated user
        
    Returns:
        GridSource instance
        
    Raises:
        HTTPException: If source is not found
    """
    event_service = EventService[GridSource]()
    source = await event_service.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=404,
            detail=f"Source not found: {source_id}"
        )
    return source

@router.get("/sources/{source_id}/event", response_model=SourceCreatedEvent)
async def get_source_event(
    source_id: str,
    current_user: User = Depends(get_current_user)
) -> SourceCreatedEvent:
    """
    Get source creation event by ID.
    
    Args:
        source_id: ID of the source to get event for
        current_user: The current authenticated user
        
    Returns:
        SourceCreatedEvent instance
        
    Raises:
        HTTPException: If event is not found
    """
    event_service = EventService[GridSource]()
    event = await event_service.get_source_event(source_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Source event not found: {source_id}"
        )
    return event

@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a grid source.
    
    Args:
        source_id: ID of the source to delete
        current_user: The current authenticated user
    """
    event_service = EventService[GridSource]()
    await event_service.delete_source(source_id)
