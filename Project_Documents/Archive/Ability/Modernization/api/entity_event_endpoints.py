"""
Entity Event API Endpoints Module

This module provides FastAPI endpoints for entity events.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from ..models.entity_events import (
    EntityEvent,
    EntityCreatedEvent,
    CreateSourceEvent,
    EventType,
    EventStatus,
    GridSourceType
)
from ..services.entity_event_service import EntityEventService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/events/entity", response_model=EntityCreatedEvent)
async def create_entity_event(
    entity_type: str,
    entity_id: Union[int, str, UUID],
    payload: Dict[str, Any],
    source: str,
    correlation_id: Optional[str] = None,
    causation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> EntityCreatedEvent:
    """
    Create an entity event.
    
    Args:
        entity_type: Type of entity
        entity_id: Entity ID
        payload: Event payload
        source: Event source
        correlation_id: Optional correlation ID
        causation_id: Optional causation ID
        metadata: Optional event metadata
        current_user: The current authenticated user
        
    Returns:
        Entity created event
    """
    service = EntityEventService()
    return await service.create_entity_event(
        entity_type,
        entity_id,
        payload,
        source,
        correlation_id,
        causation_id,
        metadata
    )

@router.post("/events/source", response_model=CreateSourceEvent)
async def create_source_event(
    name: str,
    source_type: GridSourceType,
    connection_string: Optional[str] = None,
    query: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    source: str = "grid_service",
    correlation_id: Optional[str] = None,
    causation_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> CreateSourceEvent:
    """
    Create a grid source event.
    
    Args:
        name: Grid source name
        source_type: Type of grid source
        connection_string: Optional connection string
        query: Optional query
        parameters: Optional parameters
        metadata: Optional metadata
        source: Event source
        correlation_id: Optional correlation ID
        causation_id: Optional causation ID
        current_user: The current authenticated user
        
    Returns:
        Create source event
    """
    service = EntityEventService()
    return await service.create_source_event(
        name,
        source_type,
        connection_string,
        query,
        parameters,
        metadata,
        source,
        correlation_id,
        causation_id
    )

@router.get("/events/{event_id}", response_model=EntityEvent)
async def get_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user)
) -> EntityEvent:
    """
    Get an event by ID.
    
    Args:
        event_id: Event ID
        current_user: The current authenticated user
        
    Returns:
        Entity event
        
    Raises:
        HTTPException: If event not found
    """
    service = EntityEventService()
    event = await service.get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail=f"Event not found: {event_id}"
        )
    return event

@router.get("/events/type/{event_type}", response_model=List[EntityEvent])
async def get_events_by_type(
    event_type: EventType,
    current_user: User = Depends(get_current_user)
) -> List[EntityEvent]:
    """
    Get events by type.
    
    Args:
        event_type: Event type
        current_user: The current authenticated user
        
    Returns:
        List of entity events
    """
    service = EntityEventService()
    return await service.get_events_by_type(event_type)

@router.get("/events/entity/{entity_type}/{entity_id}", response_model=List[EntityEvent])
async def get_events_by_entity(
    entity_type: str,
    entity_id: Union[int, str, UUID],
    current_user: User = Depends(get_current_user)
) -> List[EntityEvent]:
    """
    Get events by entity.
    
    Args:
        entity_type: Entity type
        entity_id: Entity ID
        current_user: The current authenticated user
        
    Returns:
        List of entity events
    """
    service = EntityEventService()
    return await service.get_events_by_entity(entity_type, entity_id)
