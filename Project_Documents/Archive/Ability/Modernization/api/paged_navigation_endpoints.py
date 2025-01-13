"""
Paged Navigation API Endpoints Module

This module provides FastAPI endpoints for paged navigation.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID
from ..models.navigation import (
    NavigatorData,
    NavigatorEvent,
    NavigatorFilter,
    NavigatorOptions,
    NavigatorSort,
    RowClickEvent
)
from ..services.paged_navigation_service import PagedNavigationService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/paged-navigators", response_model=NavigatorData)
async def create_paged_navigator(
    table_names: Optional[Set[str]] = None,
    options: Optional[NavigatorOptions] = None,
    metadata: Optional[Dict[str, Any]] = None,
    page_size: int = PagedNavigationService.DEFAULT_PAGE_SIZE,
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Create a new paged navigator.
    
    Args:
        table_names: Optional set of allowed table names
        options: Optional navigator options
        metadata: Optional metadata
        page_size: Page size (default: 100)
        current_user: The current authenticated user
        
    Returns:
        Created navigator data
    """
    service = PagedNavigationService()
    return await service.create_navigator(
        table_names,
        options,
        metadata,
        page_size
    )

@router.get("/paged-navigators/{navigator_id}", response_model=NavigatorData)
async def get_paged_navigator(
    navigator_id: UUID,
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Get paged navigator by ID.
    
    Args:
        navigator_id: Navigator ID
        current_user: The current authenticated user
        
    Returns:
        Navigator data
        
    Raises:
        HTTPException: If navigator not found
    """
    service = PagedNavigationService()
    navigator = await service.get_navigator(navigator_id)
    if not navigator:
        raise HTTPException(
            status_code=404,
            detail=f"Navigator not found: {navigator_id}"
        )
    return navigator

@router.put("/paged-navigators/{navigator_id}/page", response_model=NavigatorData)
async def load_page(
    navigator_id: UUID,
    page: int,
    data: List[Dict[str, Any]],
    total_rows: int,
    filtered_rows: Optional[int] = None,
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Load a page of data into navigator.
    
    Args:
        navigator_id: Navigator ID
        page: Page number (1-based)
        data: Page data
        total_rows: Total number of rows
        filtered_rows: Optional number of filtered rows
        current_user: The current authenticated user
        
    Returns:
        Updated navigator data
    """
    service = PagedNavigationService()
    return await service.load_page(
        navigator_id,
        page,
        data,
        total_rows,
        filtered_rows
    )

@router.put("/paged-navigators/{navigator_id}/filter", response_model=NavigatorData)
async def update_paged_filter(
    navigator_id: UUID,
    filter_text: Optional[str] = None,
    columns: Optional[List[str]] = None,
    case_sensitive: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Update paged navigator filter.
    
    Args:
        navigator_id: Navigator ID
        filter_text: Optional filter text
        columns: Optional columns to filter
        case_sensitive: Case sensitive filtering
        metadata: Optional filter metadata
        current_user: The current authenticated user
        
    Returns:
        Updated navigator data
    """
    service = PagedNavigationService()
    return await service.update_filter(
        navigator_id,
        filter_text,
        columns,
        case_sensitive,
        metadata
    )

@router.put("/paged-navigators/{navigator_id}/sort", response_model=NavigatorData)
async def update_paged_sort(
    navigator_id: UUID,
    sorts: List[NavigatorSort],
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Update paged navigator sort.
    
    Args:
        navigator_id: Navigator ID
        sorts: Sort configurations
        current_user: The current authenticated user
        
    Returns:
        Updated navigator data
    """
    service = PagedNavigationService()
    return await service.update_sort(navigator_id, sorts)

@router.post("/paged-navigators/{navigator_id}/clear", response_model=NavigatorData)
async def clear_paged_data(
    navigator_id: UUID,
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Clear paged navigator data.
    
    Args:
        navigator_id: Navigator ID
        current_user: The current authenticated user
        
    Returns:
        Updated navigator data
    """
    service = PagedNavigationService()
    return await service.clear_data(navigator_id)

@router.post("/paged-navigators/{navigator_id}/row-click")
async def handle_paged_row_click(
    navigator_id: UUID,
    row_index: int,
    row_data: Dict[str, Any],
    column: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Handle paged navigator row click event.
    
    Args:
        navigator_id: Navigator ID
        row_index: Row index
        row_data: Row data
        column: Optional clicked column
        metadata: Optional event metadata
        current_user: The current authenticated user
    """
    service = PagedNavigationService()
    await service.handle_row_click(
        navigator_id,
        row_index,
        row_data,
        column,
        metadata
    )

@router.delete("/paged-navigators/{navigator_id}")
async def delete_paged_navigator(
    navigator_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Delete paged navigator.
    
    Args:
        navigator_id: Navigator ID
        current_user: The current authenticated user
    """
    service = PagedNavigationService()
    await service.delete_navigator(navigator_id)
