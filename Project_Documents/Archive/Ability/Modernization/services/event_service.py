"""
Event Service Module

This module provides services for handling grid source events.
"""
from typing import Optional, Dict, Any, TypeVar, Generic
from ..models.events import (
    CreateSourceEventArgs,
    GridSource,
    SourceCreatedEvent,
    SourceEventContext,
    GridSourceType
)
from .base_service import BaseService
from fastapi import HTTPException
import time
import uuid

T = TypeVar('T')

class EventService(BaseService, Generic[T]):
    """Service for handling grid source events"""
    
    def __init__(self):
        """Initialize event service"""
        self._sources: Dict[str, GridSource] = {}
        self._events: Dict[str, SourceCreatedEvent] = {}
    
    async def create_source(
        self,
        source_type: GridSourceType,
        schema: Dict[str, Any],
        context: SourceEventContext
    ) -> CreateSourceEventArgs[T]:
        """
        Create a new grid source.
        
        Args:
            source_type: Type of grid source to create
            schema: Schema definition for the source
            context: Event context information
            
        Returns:
            CreateSourceEventArgs instance with created source
            
        Raises:
            HTTPException: If source creation fails
        """
        try:
            # Create source
            source_id = str(uuid.uuid4())
            source = GridSource(
                type=source_type,
                name=f"source_{source_id}",
                schema=schema
            )
            
            # Store source
            self._sources[source_id] = source
            
            # Create event
            event = SourceCreatedEvent(
                source_id=source_id,
                source_type=source_type,
                timestamp=time.time(),
                metadata=context.metadata
            )
            self._events[source_id] = event
            
            # Return event args
            return CreateSourceEventArgs[T](
                source=source,
                metadata={
                    "source_id": source_id,
                    "context": context.dict()
                }
            )
        except Exception as e:
            return CreateSourceEventArgs[T](
                cancelled=True,
                error=str(e)
            )
    
    async def get_source(self, source_id: str) -> Optional[GridSource]:
        """
        Get a grid source by ID.
        
        Args:
            source_id: ID of the source to retrieve
            
        Returns:
            GridSource if found, None otherwise
        """
        return self._sources.get(source_id)
    
    async def get_source_event(self, source_id: str) -> Optional[SourceCreatedEvent]:
        """
        Get source creation event by ID.
        
        Args:
            source_id: ID of the source to get event for
            
        Returns:
            SourceCreatedEvent if found, None otherwise
        """
        return self._events.get(source_id)
    
    async def delete_source(self, source_id: str):
        """
        Delete a grid source.
        
        Args:
            source_id: ID of the source to delete
        """
        self._sources.pop(source_id, None)
        self._events.pop(source_id, None)
