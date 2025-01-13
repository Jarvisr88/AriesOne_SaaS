"""
Entity Management Service Module

This module provides services for entity creation and management.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Set, Type, Union
from uuid import UUID, uuid4
from fastapi import HTTPException
from pydantic import BaseModel, Field

class EntityCreatedEvent(BaseModel):
    """Event data for entity creation"""
    entity_id: Union[str, int, UUID]
    entity_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CreateSourceEvent(BaseModel):
    """Event data for source creation"""
    source_id: UUID
    source_type: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EntityCreatedEventListener(Protocol):
    """Protocol for entity creation event listeners"""
    
    async def on_entity_created(self, event: EntityCreatedEvent) -> None:
        """
        Handle entity created event.
        
        Args:
            event: Entity created event data
        """
        ...

class EntityManagementService:
    """Service for entity management"""
    
    def __init__(self):
        """Initialize entity management service"""
        self._entity_listeners: Dict[str, List[EntityCreatedEventListener]] = {}
        self._source_handlers: Dict[str, List[callable]] = {}
    
    async def create_entity(
        self,
        entity_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> EntityCreatedEvent:
        """
        Create a new entity and notify listeners.
        
        Args:
            entity_type: Type of entity
            data: Entity data
            metadata: Optional metadata
            
        Returns:
            Entity created event
        """
        # Generate entity ID
        entity_id = uuid4()
        
        # Create event
        event = EntityCreatedEvent(
            entity_id=entity_id,
            entity_type=entity_type,
            data=data,
            metadata=metadata or {}
        )
        
        # Notify listeners
        await self._notify_entity_listeners(entity_type, event)
        
        return event
    
    async def create_source(
        self,
        source_type: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> CreateSourceEvent:
        """
        Create a new source and notify handlers.
        
        Args:
            source_type: Type of source
            parameters: Source parameters
            metadata: Optional metadata
            
        Returns:
            Create source event
        """
        # Generate source ID
        source_id = uuid4()
        
        # Create event
        event = CreateSourceEvent(
            source_id=source_id,
            source_type=source_type,
            parameters=parameters,
            metadata=metadata or {}
        )
        
        # Notify handlers
        await self._notify_source_handlers(source_type, event)
        
        return event
    
    async def register_entity_listener(
        self,
        entity_type: str,
        listener: EntityCreatedEventListener
    ):
        """
        Register an entity creation listener.
        
        Args:
            entity_type: Type of entity to listen for
            listener: Event listener
        """
        if entity_type not in self._entity_listeners:
            self._entity_listeners[entity_type] = []
        self._entity_listeners[entity_type].append(listener)
    
    async def unregister_entity_listener(
        self,
        entity_type: str,
        listener: EntityCreatedEventListener
    ):
        """
        Unregister an entity creation listener.
        
        Args:
            entity_type: Type of entity
            listener: Event listener
        """
        if entity_type in self._entity_listeners:
            if listener in self._entity_listeners[entity_type]:
                self._entity_listeners[entity_type].remove(listener)
    
    async def register_source_handler(
        self,
        source_type: str,
        handler: callable
    ):
        """
        Register a source creation handler.
        
        Args:
            source_type: Type of source to handle
            handler: Event handler
        """
        if source_type not in self._source_handlers:
            self._source_handlers[source_type] = []
        self._source_handlers[source_type].append(handler)
    
    async def unregister_source_handler(
        self,
        source_type: str,
        handler: callable
    ):
        """
        Unregister a source creation handler.
        
        Args:
            source_type: Type of source
            handler: Event handler
        """
        if source_type in self._source_handlers:
            if handler in self._source_handlers[source_type]:
                self._source_handlers[source_type].remove(handler)
    
    async def _notify_entity_listeners(
        self,
        entity_type: str,
        event: EntityCreatedEvent
    ):
        """
        Notify entity creation listeners.
        
        Args:
            entity_type: Type of entity
            event: Entity created event
        """
        if entity_type in self._entity_listeners:
            for listener in self._entity_listeners[entity_type]:
                try:
                    await listener.on_entity_created(event)
                except Exception as e:
                    # Log error but continue notifying other listeners
                    print(f"Error in entity creation listener: {e}")
                    continue
    
    async def _notify_source_handlers(
        self,
        source_type: str,
        event: CreateSourceEvent
    ):
        """
        Notify source creation handlers.
        
        Args:
            source_type: Type of source
            event: Create source event
        """
        if source_type in self._source_handlers:
            for handler in self._source_handlers[source_type]:
                try:
                    await handler(event)
                except Exception as e:
                    # Log error but continue notifying other handlers
                    print(f"Error in source creation handler: {e}")
                    continue
