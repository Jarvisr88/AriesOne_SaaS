"""
Paged Navigation Service Module

This module provides services for paged navigation functionality.
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
from .navigation_service import NavigationService

class PagedNavigationService(NavigationService):
    """Service for paged navigation"""
    
    DEFAULT_PAGE_SIZE = 100
    
    async def create_navigator(
        self,
        table_names: Optional[Set[str]] = None,
        options: Optional[NavigatorOptions] = None,
        metadata: Optional[Dict[str, Any]] = None,
        page_size: int = DEFAULT_PAGE_SIZE
    ) -> NavigatorData:
        """
        Create a new paged navigator.
        
        Args:
            table_names: Optional set of allowed table names
            options: Optional navigator options
            metadata: Optional metadata
            page_size: Page size (default: 100)
            
        Returns:
            Navigator data
        """
        # Create options if not provided
        if not options:
            options = NavigatorOptions(
                table_names=table_names or set(),
                page_size=page_size
            )
        else:
            options.page_size = page_size
            if table_names:
                options.table_names = table_names
        
        return await super().create_navigator(
            table_names=table_names,
            options=options,
            metadata=metadata
        )
    
    async def load_page(
        self,
        navigator_id: UUID,
        page: int,
        data: List[Dict[str, Any]],
        total_rows: int,
        filtered_rows: Optional[int] = None
    ) -> NavigatorData:
        """
        Load a page of data into navigator.
        
        Args:
            navigator_id: Navigator ID
            page: Page number (1-based)
            data: Page data
            total_rows: Total number of rows
            filtered_rows: Optional number of filtered rows
            
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
        
        # Calculate page count
        page_size = navigator.metadata.options.page_size or self.DEFAULT_PAGE_SIZE
        total_filtered = filtered_rows or total_rows
        page_count = (total_filtered + page_size - 1) // page_size
        
        # Update navigator
        navigator.data.extend(data)  # Append new page data
        navigator.total_rows = total_rows
        navigator.filtered_rows = filtered_rows or total_rows
        navigator.page = page
        navigator.page_count = page_count
        navigator.metadata.state = NavigatorState.IDLE
        navigator.metadata.updated_at = datetime.utcnow()
        
        await self._publish_event(
            "navigator_page_loaded",
            navigator_id,
            {
                "page": page,
                "page_count": page_count,
                "total_rows": total_rows,
                "filtered_rows": filtered_rows
            }
        )
        
        return navigator
    
    async def clear_data(
        self,
        navigator_id: UUID
    ) -> NavigatorData:
        """
        Clear navigator data.
        
        Args:
            navigator_id: Navigator ID
            
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
        
        # Clear data
        navigator.data = []
        navigator.total_rows = 0
        navigator.filtered_rows = 0
        navigator.page = None
        navigator.page_count = None
        navigator.metadata.state = NavigatorState.IDLE
        navigator.metadata.updated_at = datetime.utcnow()
        
        await self._publish_event("navigator_cleared", navigator_id)
        
        return navigator
    
    async def update_filter(
        self,
        navigator_id: UUID,
        filter_text: Optional[str] = None,
        columns: Optional[List[str]] = None,
        case_sensitive: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NavigatorData:
        """
        Update navigator filter and clear existing data.
        
        Args:
            navigator_id: Navigator ID
            filter_text: Optional filter text
            columns: Optional columns to filter
            case_sensitive: Case sensitive filtering
            metadata: Optional filter metadata
            
        Returns:
            Updated navigator data
        """
        # Update filter
        navigator = await super().update_filter(
            navigator_id,
            filter_text,
            columns,
            case_sensitive,
            metadata
        )
        
        # Clear existing data
        return await self.clear_data(navigator_id)
    
    async def update_sort(
        self,
        navigator_id: UUID,
        sorts: List[NavigatorSort]
    ) -> NavigatorData:
        """
        Update navigator sort and clear existing data.
        
        Args:
            navigator_id: Navigator ID
            sorts: Sort configurations
            
        Returns:
            Updated navigator data
        """
        # Update sort
        navigator = await super().update_sort(navigator_id, sorts)
        
        # Clear existing data
        return await self.clear_data(navigator_id)
