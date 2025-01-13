"""
Navigation API Endpoints Module

This module provides FastAPI endpoints for navigation.
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
from ..services.navigation_service import NavigationService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/navigators", response_model=NavigatorData)
async def create_navigator(
    table_names: Optional[Set[str]] = None,
    options: Optional[NavigatorOptions] = None,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Create a new navigator.
    
    Args:
        table_names: Optional set of allowed table names
        options: Optional navigator options
        metadata: Optional metadata
        current_user: The current authenticated user
        
    Returns:
        Created navigator data
    """
    service = NavigationService()
    return await service.create_navigator(
        table_names,
        options,
        metadata
    )

@router.get("/navigators/{navigator_id}", response_model=NavigatorData)
async def get_navigator(
    navigator_id: UUID,
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Get navigator by ID.
    
    Args:
        navigator_id: Navigator ID
        current_user: The current authenticated user
        
    Returns:
        Navigator data
        
    Raises:
        HTTPException: If navigator not found
    """
    service = NavigationService()
    navigator = await service.get_navigator(navigator_id)
    if not navigator:
        raise HTTPException(
            status_code=404,
            detail=f"Navigator not found: {navigator_id}"
        )
    return navigator

@router.put("/navigators/{navigator_id}/filter", response_model=NavigatorData)
async def update_filter(
    navigator_id: UUID,
    filter_text: Optional[str] = None,
    columns: Optional[List[str]] = None,
    case_sensitive: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Update navigator filter.
    
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
    service = NavigationService()
    return await service.update_filter(
        navigator_id,
        filter_text,
        columns,
        case_sensitive,
        metadata
    )

@router.put("/navigators/{navigator_id}/sort", response_model=NavigatorData)
async def update_sort(
    navigator_id: UUID,
    sorts: List[NavigatorSort],
    current_user: User = Depends(get_current_user)
) -> NavigatorData:
    """
    Update navigator sort.
    
    Args:
        navigator_id: Navigator ID
        sorts: Sort configurations
        current_user: The current authenticated user
        
    Returns:
        Updated navigator data
    """
    service = NavigationService()
    return await service.update_sort(navigator_id, sorts)

@router.put("/navigators/{navigator_id}/data", response_model=NavigatorData)
async def load_data(
    navigator_id: UUID,
    data: List[Dict[str, Any]],
    total_rows: int,
    filtered_rows: Optional[int] = None,
    page: Optional[int] = None,
    page_count: Optional[int] = None,
    current_user: User = Depends(get_current_user)
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
        current_user: The current authenticated user
        
    Returns:
        Updated navigator data
    """
    service = NavigationService()
    return await service.load_data(
        navigator_id,
        data,
        total_rows,
        filtered_rows,
        page,
        page_count
    )

@router.post("/navigators/{navigator_id}/row-click")
async def handle_row_click(
    navigator_id: UUID,
    row_index: int,
    row_data: Dict[str, Any],
    column: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Handle row click event.
    
    Args:
        navigator_id: Navigator ID
        row_index: Row index
        row_data: Row data
        column: Optional clicked column
        metadata: Optional event metadata
        current_user: The current authenticated user
    """
    service = NavigationService()
    await service.handle_row_click(
        navigator_id,
        row_index,
        row_data,
        column,
        metadata
    )

@router.delete("/navigators/{navigator_id}")
async def delete_navigator(
    navigator_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Delete navigator.
    
    Args:
        navigator_id: Navigator ID
        current_user: The current authenticated user
    """
    service = NavigationService()
    await service.delete_navigator(navigator_id)
