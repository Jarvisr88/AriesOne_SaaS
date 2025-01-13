"""
Navigator API Endpoints Module

This module provides FastAPI endpoints for the navigation system.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from ..models.navigator import (
    NavigatorState,
    NavigatorOptions,
    GridState,
    GridSortDirection,
    NavigatorRowClickEvent
)
from ..services.navigator_service import NavigatorService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/navigators", response_model=str)
async def create_navigator(
    options: NavigatorOptions,
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Create a new navigator.
    
    Args:
        options: Navigator options
        current_user: The current authenticated user
        
    Returns:
        Navigator ID
    """
    service = NavigatorService()
    return await service.create_navigator(options)

@router.get("/navigators/{navigator_id}", response_model=NavigatorState)
async def get_navigator_state(
    navigator_id: str,
    current_user: User = Depends(get_current_user)
) -> NavigatorState:
    """
    Get navigator state.
    
    Args:
        navigator_id: ID of the navigator
        current_user: The current authenticated user
        
    Returns:
        Navigator state
    """
    service = NavigatorService()
    return await service.get_navigator_state(navigator_id)

@router.put("/navigators/{navigator_id}/grid-state")
async def update_grid_state(
    navigator_id: str,
    grid_state: GridState,
    current_user: User = Depends(get_current_user)
):
    """
    Update grid state.
    
    Args:
        navigator_id: ID of the navigator
        grid_state: New grid state
        current_user: The current authenticated user
    """
    service = NavigatorService()
    await service.update_grid_state(navigator_id, grid_state)

@router.put("/navigators/{navigator_id}/filter")
async def set_filter(
    navigator_id: str,
    filter_text: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Set filter text.
    
    Args:
        navigator_id: ID of the navigator
        filter_text: Filter text
        current_user: The current authenticated user
    """
    service = NavigatorService()
    await service.set_filter(navigator_id, filter_text)

@router.put("/navigators/{navigator_id}/sort")
async def set_sort(
    navigator_id: str,
    field: Optional[str] = None,
    direction: GridSortDirection = GridSortDirection.NONE,
    current_user: User = Depends(get_current_user)
):
    """
    Set sort field and direction.
    
    Args:
        navigator_id: ID of the navigator
        field: Sort field
        direction: Sort direction
        current_user: The current authenticated user
    """
    service = NavigatorService()
    await service.set_sort(navigator_id, field, direction)

@router.post("/navigators/{navigator_id}/row-click")
async def handle_row_click(
    navigator_id: str,
    row_id: str,
    row_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Handle row click event.
    
    Args:
        navigator_id: ID of the navigator
        row_id: ID of the clicked row
        row_data: Row data
        current_user: The current authenticated user
    """
    service = NavigatorService()
    await service.handle_row_click(navigator_id, row_id, row_data)
