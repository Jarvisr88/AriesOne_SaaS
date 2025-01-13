"""
Pagination Service Module

This module provides services for the pagination system.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar, Callable
from ..models.pagination import (
    PaginationFilter,
    PageInfo,
    PaginatedData,
    PaginatedNavigatorOptions,
    PaginatedNavigatorState,
    PaginatedSourceEvent,
    SortOrder
)
from .base_service import BaseService
from fastapi import HTTPException
import uuid
from datetime import datetime
import math

T = TypeVar('T')

class PaginationService(BaseService, Generic[T]):
    """Service for handling pagination"""
    
    def __init__(self):
        """Initialize pagination service"""
        self._navigators: Dict[str, PaginatedNavigatorState] = {}
        self._source_handlers: Dict[str, List[Callable[[PaginatedSourceEvent], PaginatedData[T]]]] = {}
    
    async def create_navigator(
        self,
        options: PaginatedNavigatorOptions
    ) -> str:
        """
        Create a new paginated navigator.
        
        Args:
            options: Navigator options
            
        Returns:
            Navigator ID
        """
        navigator_id = str(uuid.uuid4())
        self._navigators[navigator_id] = PaginatedNavigatorState(
            options=options
        )
        return navigator_id
    
    async def get_navigator_state(
        self,
        navigator_id: str
    ) -> PaginatedNavigatorState:
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
    
    async def set_filter(
        self,
        navigator_id: str,
        filter_text: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[SortOrder] = None
    ):
        """
        Set filter and sort parameters.
        
        Args:
            navigator_id: ID of the navigator
            filter_text: Filter text
            sort_field: Sort field
            sort_order: Sort order
            
        Raises:
            HTTPException: If navigator is not found
        """
        state = await self.get_navigator_state(navigator_id)
        
        # Reset pagination when filter changes
        state.filter = PaginationFilter(
            filter_text=filter_text,
            sort_field=sort_field,
            sort_order=sort_order,
            count=state.options.page_size
        )
        state.timestamp = datetime.utcnow()
        
        # Load first page
        await self._load_data(navigator_id)
    
    async def load_more(
        self,
        navigator_id: str
    ):
        """
        Load more data.
        
        Args:
            navigator_id: ID of the navigator
            
        Raises:
            HTTPException: If navigator is not found
        """
        state = await self.get_navigator_state(navigator_id)
        
        if not state.is_loading and not state.is_loading_more:
            state.is_loading_more = True
            state.filter.start += state.filter.count
            state.timestamp = datetime.utcnow()
            
            try:
                await self._load_data(navigator_id)
            finally:
                state.is_loading_more = False
    
    async def add_source_handler(
        self,
        navigator_id: str,
        handler: Callable[[PaginatedSourceEvent], PaginatedData[T]]
    ):
        """
        Add source event handler.
        
        Args:
            navigator_id: ID of the navigator
            handler: Event handler function
        """
        if navigator_id not in self._source_handlers:
            self._source_handlers[navigator_id] = []
        self._source_handlers[navigator_id].append(handler)
    
    async def _load_data(
        self,
        navigator_id: str
    ):
        """
        Load data using source handlers.
        
        Args:
            navigator_id: ID of the navigator
        """
        state = self._navigators[navigator_id]
        state.is_loading = True
        state.error = None
        
        try:
            # Create event
            event = PaginatedSourceEvent(
                source_id=navigator_id,
                filter=state.filter
            )
            
            # Trigger handlers
            if navigator_id in self._source_handlers:
                for handler in self._source_handlers[navigator_id]:
                    try:
                        data = await handler(event)
                        # Update state with loaded data
                        state.filter = data.filter
                        state.metadata.update(data.metadata)
                    except Exception as e:
                        state.error = str(e)
                        break
        finally:
            state.is_loading = False
    
    def create_page_info(
        self,
        total_count: int,
        page_size: int,
        current_page: int
    ) -> PageInfo:
        """
        Create page information.
        
        Args:
            total_count: Total number of items
            page_size: Items per page
            current_page: Current page number
            
        Returns:
            Page information
        """
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 0
        
        return PageInfo(
            total_count=total_count,
            page_size=page_size,
            current_page=current_page,
            total_pages=total_pages,
            has_next=current_page < total_pages,
            has_previous=current_page > 1
        )
