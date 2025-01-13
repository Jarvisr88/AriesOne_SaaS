"""
Source Management Service Module

This module provides services for managing data sources and fill events.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4
from fastapi import HTTPException
from pydantic import BaseModel

class FillSourceEventArgs(BaseModel):
    """Event arguments for source fill events"""
    source_id: UUID
    source_type: str
    data: Any
    metadata: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()

class SourceManagementService:
    """Service for managing data sources"""
    
    def __init__(self):
        """Initialize source management service"""
        self._sources: Dict[UUID, Dict[str, Any]] = {}
        self._event_handlers: Dict[str, List[callable]] = {}
    
    async def create_source(
        self,
        source_type: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Create a new data source.
        
        Args:
            source_type: Type of source
            data: Source data
            metadata: Optional metadata
            
        Returns:
            Source ID
        """
        source_id = uuid4()
        
        # Store source
        self._sources[source_id] = {
            'type': source_type,
            'data': data,
            'metadata': metadata or {},
            'created_at': datetime.utcnow()
        }
        
        # Create event
        event = FillSourceEventArgs(
            source_id=source_id,
            source_type=source_type,
            data=data,
            metadata=metadata or {}
        )
        
        # Notify handlers
        await self._notify_handlers('source_created', event)
        
        return source_id
    
    async def update_source(
        self,
        source_id: UUID,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Update a data source.
        
        Args:
            source_id: Source ID
            data: New source data
            metadata: Optional metadata
            
        Raises:
            HTTPException: If source not found
        """
        source = self._sources.get(source_id)
        if not source:
            raise HTTPException(
                status_code=404,
                detail=f"Source not found: {source_id}"
            )
        
        # Update source
        source['data'] = data
        if metadata:
            source['metadata'].update(metadata)
        
        # Create event
        event = FillSourceEventArgs(
            source_id=source_id,
            source_type=source['type'],
            data=data,
            metadata=source['metadata']
        )
        
        # Notify handlers
        await self._notify_handlers('source_updated', event)
    
    async def delete_source(
        self,
        source_id: UUID
    ):
        """
        Delete a data source.
        
        Args:
            source_id: Source ID
            
        Raises:
            HTTPException: If source not found
        """
        source = self._sources.get(source_id)
        if not source:
            raise HTTPException(
                status_code=404,
                detail=f"Source not found: {source_id}"
            )
        
        # Create event
        event = FillSourceEventArgs(
            source_id=source_id,
            source_type=source['type'],
            data=None,
            metadata=source['metadata']
        )
        
        # Delete source
        del self._sources[source_id]
        
        # Notify handlers
        await self._notify_handlers('source_deleted', event)
    
    async def get_source(
        self,
        source_id: UUID
    ) -> Dict[str, Any]:
        """
        Get a data source.
        
        Args:
            source_id: Source ID
            
        Returns:
            Source data and metadata
            
        Raises:
            HTTPException: If source not found
        """
        source = self._sources.get(source_id)
        if not source:
            raise HTTPException(
                status_code=404,
                detail=f"Source not found: {source_id}"
            )
        return source
    
    async def subscribe(
        self,
        event_type: str,
        handler: callable
    ):
        """
        Subscribe to source events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    async def unsubscribe(
        self,
        event_type: str,
        handler: callable
    ):
        """
        Unsubscribe from source events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type in self._event_handlers and handler in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(handler)
    
    async def _notify_handlers(
        self,
        event_type: str,
        event: FillSourceEventArgs
    ):
        """
        Notify event handlers.
        
        Args:
            event_type: Type of event
            event: Event arguments
        """
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    # Log error but continue notifying other handlers
                    print(f"Error in source event handler: {e}")
                    continue
