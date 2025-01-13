"""
Entity Event Service Module

This module provides services for handling entity events.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union, Callable
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException
from ..models.entity_events import (
    EntityEvent,
    EntityCreatedEvent,
    CreateSourceEvent,
    EventType,
    EventStatus,
    EventMetadata,
    GridSource,
    GridSourceConfig,
    GridSourceType
)
from .base_service import BaseService

T = TypeVar('T')
EventHandler = Callable[[EntityEvent[T]], None]

class EntityEventService(BaseService, Generic[T]):
    """Service for handling entity events"""
    
    def __init__(self):
        """Initialize entity event service"""
        self._handlers: Dict[EventType, List[EventHandler]] = {
            event_type: []
            for event_type in EventType
        }
        self._events: Dict[UUID, EntityEvent[T]] = {}
    
    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler
    ):
        """
        Subscribe to entity events.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Event handler function
        """
        self._handlers[event_type].append(handler)
    
    def unsubscribe(
        self,
        event_type: EventType,
        handler: EventHandler
    ):
        """
        Unsubscribe from entity events.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Event handler function to remove
        """
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
    
    async def publish_event(
        self,
        event: EntityEvent[T]
    ):
        """
        Publish an entity event.
        
        Args:
            event: Entity event to publish
        """
        # Store event
        self._events[event.metadata.event_id] = event
        
        # Update status
        event.metadata.status = EventStatus.PROCESSING
        
        try:
            # Call handlers
            for handler in self._handlers[event.metadata.event_type]:
                handler(event)
            
            # Update status
            event.metadata.status = EventStatus.COMPLETED
            
        except Exception as e:
            # Update status
            event.metadata.status = EventStatus.FAILED
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process event: {str(e)}"
            )
    
    async def create_entity_event(
        self,
        entity_type: str,
        entity_id: Union[int, str, UUID],
        payload: T,
        source: str,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EntityCreatedEvent[T]:
        """
        Create an entity created event.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            payload: Event payload
            source: Event source
            correlation_id: Optional correlation ID
            causation_id: Optional causation ID
            metadata: Optional event metadata
            
        Returns:
            Entity created event
        """
        event = EntityCreatedEvent(
            metadata=EventMetadata(
                event_id=uuid4(),
                event_type=EventType.CREATED,
                source=source,
                correlation_id=correlation_id,
                causation_id=causation_id,
                metadata=metadata or {}
            ),
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload
        )
        
        await self.publish_event(event)
        return event
    
    async def create_source_event(
        self,
        name: str,
        source_type: GridSourceType,
        connection_string: Optional[str] = None,
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "grid_service",
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None
    ) -> CreateSourceEvent:
        """
        Create a grid source creation event.
        
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
            
        Returns:
            Create source event
        """
        grid_source = GridSource(
            id=uuid4(),
            name=name,
            config=GridSourceConfig(
                source_type=source_type,
                connection_string=connection_string,
                query=query,
                parameters=parameters or {},
                metadata=metadata or {}
            )
        )
        
        event = CreateSourceEvent(
            metadata=EventMetadata(
                event_id=uuid4(),
                event_type=EventType.SOURCE_CREATED,
                source=source,
                correlation_id=correlation_id,
                causation_id=causation_id,
                metadata={}
            ),
            entity_type="grid_source",
            entity_id=grid_source.id,
            payload=grid_source
        )
        
        await self.publish_event(event)
        return event
    
    async def get_event(
        self,
        event_id: UUID
    ) -> Optional[EntityEvent[T]]:
        """
        Get an event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Entity event if found, None otherwise
        """
        return self._events.get(event_id)
    
    async def get_events_by_type(
        self,
        event_type: EventType
    ) -> List[EntityEvent[T]]:
        """
        Get events by type.
        
        Args:
            event_type: Event type
            
        Returns:
            List of entity events
        """
        return [
            event
            for event in self._events.values()
            if event.metadata.event_type == event_type
        ]
    
    async def get_events_by_entity(
        self,
        entity_type: str,
        entity_id: Union[int, str, UUID]
    ) -> List[EntityEvent[T]]:
        """
        Get events by entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            
        Returns:
            List of entity events
        """
        return [
            event
            for event in self._events.values()
            if event.entity_type == entity_type and event.entity_id == entity_id
        ]
