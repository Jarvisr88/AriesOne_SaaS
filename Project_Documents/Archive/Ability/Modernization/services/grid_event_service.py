"""
Grid Event Service Module

This module provides services for handling grid events and state management.
"""
from typing import Optional, Dict, Any, Generic, TypeVar, List, Callable
from ..models.grid_events import (
    GridSourceEventArgs,
    GridEventType,
    GridSortInfo,
    GridFilterInfo,
    GridPagingInfo,
    GridSelectionEventArgs,
    GridCustomEventArgs,
    GridStateSnapshot
)
from .base_service import BaseService
from fastapi import HTTPException
import uuid
from datetime import datetime

T = TypeVar('T')

class GridEventService(BaseService, Generic[T]):
    """Service for handling grid events"""
    
    def __init__(self):
        """Initialize grid event service"""
        self._event_handlers: Dict[str, Dict[GridEventType, List[Callable]]] = {}
        self._grid_states: Dict[str, GridStateSnapshot] = {}
    
    async def create_grid_source(
        self,
        initial_state: Optional[GridStateSnapshot] = None
    ) -> str:
        """
        Create a new grid source.
        
        Args:
            initial_state: Optional initial grid state
            
        Returns:
            Grid source ID
        """
        grid_id = str(uuid.uuid4())
        if initial_state:
            self._grid_states[grid_id] = initial_state
        else:
            self._grid_states[grid_id] = GridStateSnapshot()
        return grid_id
    
    async def handle_event(
        self,
        grid_id: str,
        event: GridSourceEventArgs[T]
    ) -> GridSourceEventArgs[T]:
        """
        Handle a grid event.
        
        Args:
            grid_id: ID of the grid
            event: Event to handle
            
        Returns:
            Processed event arguments
            
        Raises:
            HTTPException: If grid is not found
        """
        try:
            # Get current state
            state = await self._get_grid_state(grid_id)
            
            # Update state based on event
            if event.event_type == GridEventType.SORT_CHANGE:
                state.sort_info = event.sort_info
            elif event.event_type == GridEventType.FILTER_CHANGE:
                state.filter_info = event.filter_info
            elif event.event_type == GridEventType.PAGE_CHANGE:
                state.paging_info = event.paging_info
            
            # Save updated state
            self._grid_states[grid_id] = state
            
            # Trigger event handlers
            if grid_id in self._event_handlers:
                handlers = self._event_handlers[grid_id].get(event.event_type, [])
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        event.error = str(e)
                        event.cancelled = True
                        break
            
            return event
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to handle grid event: {str(e)}"
            )
    
    async def add_event_handler(
        self,
        grid_id: str,
        event_type: GridEventType,
        handler: Callable[[GridSourceEventArgs[T]], None]
    ):
        """
        Add an event handler for a grid.
        
        Args:
            grid_id: ID of the grid
            event_type: Type of event to handle
            handler: Event handler function
        """
        if grid_id not in self._event_handlers:
            self._event_handlers[grid_id] = {}
        
        if event_type not in self._event_handlers[grid_id]:
            self._event_handlers[grid_id][event_type] = []
        
        self._event_handlers[grid_id][event_type].append(handler)
    
    async def remove_event_handler(
        self,
        grid_id: str,
        event_type: GridEventType,
        handler: Callable[[GridSourceEventArgs[T]], None]
    ):
        """
        Remove an event handler from a grid.
        
        Args:
            grid_id: ID of the grid
            event_type: Type of event
            handler: Event handler function to remove
        """
        if (
            grid_id in self._event_handlers and
            event_type in self._event_handlers[grid_id]
        ):
            handlers = self._event_handlers[grid_id][event_type]
            if handler in handlers:
                handlers.remove(handler)
    
    async def get_grid_state(
        self,
        grid_id: str
    ) -> GridStateSnapshot:
        """
        Get the current state of a grid.
        
        Args:
            grid_id: ID of the grid
            
        Returns:
            Current grid state
            
        Raises:
            HTTPException: If grid is not found
        """
        return await self._get_grid_state(grid_id)
    
    async def update_grid_state(
        self,
        grid_id: str,
        state: GridStateSnapshot
    ):
        """
        Update the state of a grid.
        
        Args:
            grid_id: ID of the grid
            state: New grid state
            
        Raises:
            HTTPException: If grid is not found
        """
        if grid_id not in self._grid_states:
            raise HTTPException(
                status_code=404,
                detail=f"Grid not found: {grid_id}"
            )
        self._grid_states[grid_id] = state
    
    async def _get_grid_state(
        self,
        grid_id: str
    ) -> GridStateSnapshot:
        """
        Get grid state by ID.
        
        Args:
            grid_id: ID of the grid
            
        Returns:
            Grid state
            
        Raises:
            HTTPException: If grid is not found
        """
        state = self._grid_states.get(grid_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Grid not found: {grid_id}"
            )
        return state
