"""
Navigation Service Module

This module provides services for navigation functionality.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union, cast
from uuid import UUID, uuid4
from fastapi import HTTPException
from ..models.navigation import (
    NavigatorData,
    NavigatorEvent,
    NavigatorFilter,
    NavigatorMetadata,
    NavigatorOptions,
    NavigatorSort,
    NavigatorState,
    RowClickEvent
)
from .base_service import BaseService

class NavigationService(BaseService):
    """Service for navigation"""
    
    def __init__(self):
        """Initialize navigation service"""
        self._navigators: Dict[UUID, NavigatorData] = {}
        self._event_handlers: Dict[str, List[callable]] = {}
    
    async def create_navigator(
        self,
        table_names: Optional[Set[str]] = None,
        options: Optional[NavigatorOptions] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NavigatorData:
        """
        Create a new navigator.
        
        Args:
            table_names: Optional set of allowed table names
            options: Optional navigator options
            metadata: Optional metadata
            
        Returns:
            Navigator data
        """
        navigator_id = uuid4()
        
        # Create options if not provided
        if not options:
            options = NavigatorOptions(
                table_names=table_names or set()
            )
        elif table_names:
            options.table_names = table_names
        
        # Create metadata
        nav_metadata = NavigatorMetadata(
            navigator_id=navigator_id,
            options=options,
            metadata=metadata or {}
        )
        
        # Create navigator data
        navigator = NavigatorData(
            metadata=nav_metadata
        )
        
        self._navigators[navigator_id] = navigator
        await self._publish_event("navigator_created", navigator_id)
        
        return navigator
    
    async def get_navigator(
        self,
        navigator_id: UUID
    ) -> Optional[NavigatorData]:
        """
        Get navigator by ID.
        
        Args:
            navigator_id: Navigator ID
            
        Returns:
            Navigator data if found, None otherwise
        """
        return self._navigators.get(navigator_id)
    
    async def update_filter(
        self,
        navigator_id: UUID,
        filter_text: Optional[str] = None,
        columns: Optional[List[str]] = None,
        case_sensitive: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NavigatorData:
        """
        Update navigator filter.
        
        Args:
            navigator_id: Navigator ID
            filter_text: Optional filter text
            columns: Optional columns to filter
            case_sensitive: Case sensitive filtering
            metadata: Optional filter metadata
            
        Returns:
            Updated navigator data
            
        Raises:
            HTTPException: If navigator not found
        """
        navigator = await self.get_navigator(navigator_id)
        if not navigator:
            raise HTTPException(
                status_code=404,
                detail=f"Navigator not found: {navigator_id}"
            )
        
        # Create filter
        nav_filter = NavigatorFilter(
            text=filter_text,
            columns=columns,
            case_sensitive=case_sensitive,
            metadata=metadata or {}
        )
        
        # Update navigator
        navigator.metadata.filter = nav_filter
        navigator.metadata.state = NavigatorState.FILTERING
        navigator.metadata.updated_at = datetime.utcnow()
        
        await self._publish_event("navigator_filtered", navigator_id)
        
        return navigator
    
    async def update_sort(
        self,
        navigator_id: UUID,
        sorts: List[NavigatorSort]
    ) -> NavigatorData:
        """
        Update navigator sort.
        
        Args:
            navigator_id: Navigator ID
            sorts: Sort configurations
            
        Returns:
            Updated navigator data
            
        Raises:
            HTTPException: If navigator not found
        """
        navigator = await self.get_navigator(navigator_id)
        if not navigator:
            raise HTTPException(
                status_code=404,
                detail=f"Navigator not found: {navigator_id}"
            )
        
        # Update navigator
        navigator.metadata.sorts = sorts
        navigator.metadata.updated_at = datetime.utcnow()
        
        await self._publish_event("navigator_sorted", navigator_id)
        
        return navigator
    
    async def load_data(
        self,
        navigator_id: UUID,
        data: List[Dict[str, Any]],
        total_rows: int,
        filtered_rows: Optional[int] = None,
        page: Optional[int] = None,
        page_count: Optional[int] = None
    ) -> NavigatorData:
        """
        Load data into navigator.
        
        Args:
            navigator_id: Navigator ID
            data: Grid data
            total_rows: Total number of rows
            filtered_rows: Optional number of filtered rows
            page: Optional current page number
            page_count: Optional total number of pages
            
        Returns:
            Updated navigator data
            
        Raises:
            HTTPException: If navigator not found
        """
        navigator = await self.get_navigator(navigator_id)
        if not navigator:
            raise HTTPException(
                status_code=404,
                detail=f"Navigator not found: {navigator_id}"
            )
        
        # Update navigator
        navigator.data = data
        navigator.total_rows = total_rows
        navigator.filtered_rows = filtered_rows or total_rows
        navigator.page = page
        navigator.page_count = page_count
        navigator.metadata.state = NavigatorState.IDLE
        navigator.metadata.updated_at = datetime.utcnow()
        
        await self._publish_event("navigator_loaded", navigator_id)
        
        return navigator
    
    async def handle_row_click(
        self,
        navigator_id: UUID,
        row_index: int,
        row_data: Dict[str, Any],
        column: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Handle row click event.
        
        Args:
            navigator_id: Navigator ID
            row_index: Row index
            row_data: Row data
            column: Optional clicked column
            metadata: Optional event metadata
            
        Raises:
            HTTPException: If navigator not found
        """
        navigator = await self.get_navigator(navigator_id)
        if not navigator:
            raise HTTPException(
                status_code=404,
                detail=f"Navigator not found: {navigator_id}"
            )
        
        # Create event
        event = RowClickEvent(
            navigator_id=navigator_id,
            row_index=row_index,
            row_data=row_data,
            column=column,
            metadata=metadata or {}
        )
        
        await self._publish_event("row_clicked", navigator_id, {"event": event.dict()})
    
    async def delete_navigator(
        self,
        navigator_id: UUID
    ):
        """
        Delete navigator.
        
        Args:
            navigator_id: Navigator ID
            
        Raises:
            HTTPException: If navigator not found
        """
        navigator = await self.get_navigator(navigator_id)
        if not navigator:
            raise HTTPException(
                status_code=404,
                detail=f"Navigator not found: {navigator_id}"
            )
        
        await self._publish_event("navigator_deleted", navigator_id)
        
        del self._navigators[navigator_id]
    
    async def subscribe(
        self,
        event_type: str,
        handler: callable
    ):
        """
        Subscribe to navigator events.
        
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
        Unsubscribe from navigator events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type in self._event_handlers and handler in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(handler)
    
    async def _publish_event(
        self,
        event_type: str,
        navigator_id: UUID,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Publish navigator event.
        
        Args:
            event_type: Type of event
            navigator_id: Navigator ID
            data: Optional event data
        """
        event = NavigatorEvent(
            event_type=event_type,
            navigator_id=navigator_id,
            data=data
        )
        
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                await handler(event)
