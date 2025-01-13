"""
Navigator Service Module

This module provides services for the navigation system.
"""
from typing import Optional, Dict, Any, List, Set, Callable
from ..models.navigator import (
    NavigatorState,
    NavigatorOptions,
    GridState,
    CreateSourceEvent,
    FillSourceEvent,
    NavigatorRowClickEvent,
    GridSortDirection
)
from .base_service import BaseService
from fastapi import HTTPException
import uuid
from datetime import datetime

class NavigatorService(BaseService):
    """Service for handling navigation"""
    
    def __init__(self):
        """Initialize navigator service"""
        self._navigators: Dict[str, NavigatorState] = {}
        self._create_source_handlers: Dict[str, List[Callable[[CreateSourceEvent], None]]] = {}
        self._fill_source_handlers: Dict[str, List[Callable[[FillSourceEvent], None]]] = {}
        self._row_click_handlers: Dict[str, List[Callable[[NavigatorRowClickEvent], None]]] = {}
    
    async def create_navigator(
        self,
        options: NavigatorOptions
    ) -> str:
        """
        Create a new navigator.
        
        Args:
            options: Navigator options
            
        Returns:
            Navigator ID
        """
        navigator_id = str(uuid.uuid4())
        self._navigators[navigator_id] = NavigatorState(
            options=options
        )
        return navigator_id
    
    async def get_navigator_state(
        self,
        navigator_id: str
    ) -> NavigatorState:
        """
        Get navigator state.
        
        Args:
            navigator_id: ID of the navigator
            
        Returns:
            Navigator state
            
        Raises:
            HTTPException: If navigator is not found
        """
        state = self._navigators.get(navigator_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Navigator not found: {navigator_id}"
            )
        return state
    
    async def update_grid_state(
        self,
        navigator_id: str,
        grid_state: GridState
    ):
        """
        Update grid state.
        
        Args:
            navigator_id: ID of the navigator
            grid_state: New grid state
            
        Raises:
            HTTPException: If navigator is not found
        """
        state = await self.get_navigator_state(navigator_id)
        state.grid_state = grid_state
        state.timestamp = datetime.utcnow()
    
    async def set_filter(
        self,
        navigator_id: str,
        filter_text: Optional[str]
    ):
        """
        Set filter text.
        
        Args:
            navigator_id: ID of the navigator
            filter_text: Filter text
            
        Raises:
            HTTPException: If navigator is not found
        """
        state = await self.get_navigator_state(navigator_id)
        state.grid_state.filter_text = filter_text
        state.timestamp = datetime.utcnow()
        
        # Trigger fill source event
        await self._trigger_fill_source(navigator_id)
    
    async def set_sort(
        self,
        navigator_id: str,
        field: Optional[str],
        direction: GridSortDirection
    ):
        """
        Set sort field and direction.
        
        Args:
            navigator_id: ID of the navigator
            field: Sort field
            direction: Sort direction
            
        Raises:
            HTTPException: If navigator is not found
        """
        state = await self.get_navigator_state(navigator_id)
        state.grid_state.sort_field = field
        state.grid_state.sort_direction = direction
        state.timestamp = datetime.utcnow()
        
        # Trigger fill source event
        await self._trigger_fill_source(navigator_id)
    
    async def handle_row_click(
        self,
        navigator_id: str,
        row_id: str,
        row_data: Dict[str, Any]
    ):
        """
        Handle row click event.
        
        Args:
            navigator_id: ID of the navigator
            row_id: ID of the clicked row
            row_data: Row data
            
        Raises:
            HTTPException: If navigator is not found
        """
        state = await self.get_navigator_state(navigator_id)
        
        # Create event
        event = NavigatorRowClickEvent(
            row_id=row_id,
            row_data=row_data
        )
        
        # Trigger handlers
        if navigator_id in self._row_click_handlers:
            for handler in self._row_click_handlers[navigator_id]:
                try:
                    await handler(event)
                except Exception as e:
                    state.error = str(e)
    
    async def add_create_source_handler(
        self,
        navigator_id: str,
        handler: Callable[[CreateSourceEvent], None]
    ):
        """
        Add create source event handler.
        
        Args:
            navigator_id: ID of the navigator
            handler: Event handler function
        """
        if navigator_id not in self._create_source_handlers:
            self._create_source_handlers[navigator_id] = []
        self._create_source_handlers[navigator_id].append(handler)
    
    async def add_fill_source_handler(
        self,
        navigator_id: str,
        handler: Callable[[FillSourceEvent], None]
    ):
        """
        Add fill source event handler.
        
        Args:
            navigator_id: ID of the navigator
            handler: Event handler function
        """
        if navigator_id not in self._fill_source_handlers:
            self._fill_source_handlers[navigator_id] = []
        self._fill_source_handlers[navigator_id].append(handler)
    
    async def add_row_click_handler(
        self,
        navigator_id: str,
        handler: Callable[[NavigatorRowClickEvent], None]
    ):
        """
        Add row click event handler.
        
        Args:
            navigator_id: ID of the navigator
            handler: Event handler function
        """
        if navigator_id not in self._row_click_handlers:
            self._row_click_handlers[navigator_id] = []
        self._row_click_handlers[navigator_id].append(handler)
    
    async def _trigger_fill_source(
        self,
        navigator_id: str
    ):
        """
        Trigger fill source event.
        
        Args:
            navigator_id: ID of the navigator
        """
        state = self._navigators[navigator_id]
        state.is_loading = True
        
        try:
            # Create event
            event = FillSourceEvent(
                source_id=navigator_id,
                filter_text=state.grid_state.filter_text,
                sort_field=state.grid_state.sort_field,
                sort_direction=state.grid_state.sort_direction
            )
            
            # Trigger handlers
            if navigator_id in self._fill_source_handlers:
                for handler in self._fill_source_handlers[navigator_id]:
                    try:
                        await handler(event)
                    except Exception as e:
                        state.error = str(e)
                        break
        finally:
            state.is_loading = False
