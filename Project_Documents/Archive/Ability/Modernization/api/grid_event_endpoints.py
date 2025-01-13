"""
Grid Event API Endpoints Module

This module provides FastAPI endpoints for grid event handling.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from ..models.grid_events import (
    GridSourceEventArgs,
    GridEventType,
    GridStateSnapshot,
    GridSelectionEventArgs,
    GridCustomEventArgs
)
from ..services.grid_event_service import GridEventService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/grids", response_model=str)
async def create_grid(
    initial_state: GridStateSnapshot = None,
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Create a new grid source.
    
    Args:
        initial_state: Optional initial grid state
        current_user: The current authenticated user
        
    Returns:
        Grid ID
    """
    service = GridEventService[Dict[str, Any]]()
    return await service.create_grid_source(initial_state)

@router.post("/grids/{grid_id}/events", response_model=GridSourceEventArgs[Dict[str, Any]])
async def handle_grid_event(
    grid_id: str,
    event: GridSourceEventArgs[Dict[str, Any]],
    current_user: User = Depends(get_current_user)
) -> GridSourceEventArgs[Dict[str, Any]]:
    """
    Handle a grid event.
    
    Args:
        grid_id: ID of the grid
        event: Event to handle
        current_user: The current authenticated user
        
    Returns:
        Processed event arguments
    """
    service = GridEventService[Dict[str, Any]]()
    return await service.handle_event(grid_id, event)

@router.get("/grids/{grid_id}/state", response_model=GridStateSnapshot)
async def get_grid_state(
    grid_id: str,
    current_user: User = Depends(get_current_user)
) -> GridStateSnapshot:
    """
    Get the current state of a grid.
    
    Args:
        grid_id: ID of the grid
        current_user: The current authenticated user
        
    Returns:
        Current grid state
    """
    service = GridEventService[Dict[str, Any]]()
    return await service.get_grid_state(grid_id)

@router.put("/grids/{grid_id}/state")
async def update_grid_state(
    grid_id: str,
    state: GridStateSnapshot,
    current_user: User = Depends(get_current_user)
):
    """
    Update the state of a grid.
    
    Args:
        grid_id: ID of the grid
        state: New grid state
        current_user: The current authenticated user
    """
    service = GridEventService[Dict[str, Any]]()
    await service.update_grid_state(grid_id, state)

@router.post("/grids/{grid_id}/selection")
async def handle_selection_event(
    grid_id: str,
    event: GridSelectionEventArgs,
    current_user: User = Depends(get_current_user)
):
    """
    Handle a grid selection event.
    
    Args:
        grid_id: ID of the grid
        event: Selection event data
        current_user: The current authenticated user
    """
    service = GridEventService[Dict[str, Any]]()
    grid_event = GridSourceEventArgs[Dict[str, Any]](
        event_type=GridEventType.SELECTION_CHANGE,
        metadata={
            "selection": event.dict()
        }
    )
    await service.handle_event(grid_id, grid_event)

@router.post("/grids/{grid_id}/custom")
async def handle_custom_event(
    grid_id: str,
    event: GridCustomEventArgs,
    current_user: User = Depends(get_current_user)
):
    """
    Handle a custom grid event.
    
    Args:
        grid_id: ID of the grid
        event: Custom event data
        current_user: The current authenticated user
    """
    service = GridEventService[Dict[str, Any]]()
    grid_event = GridSourceEventArgs[Dict[str, Any]](
        event_type=GridEventType.CUSTOM,
        metadata={
            "custom_event": event.dict()
        }
    )
    await service.handle_event(grid_id, grid_event)
