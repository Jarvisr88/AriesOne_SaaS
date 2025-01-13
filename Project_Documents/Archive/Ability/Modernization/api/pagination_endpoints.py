"""
Pagination API Endpoints Module

This module provides FastAPI endpoints for the pagination system.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, Generic, TypeVar
from ..models.pagination import (
    PaginatedNavigatorOptions,
    PaginatedNavigatorState,
    PaginationFilter,
    SortOrder
)
from ..services.pagination_service import PaginationService
from ..services.auth_service import get_current_user, User

T = TypeVar('T')
router = APIRouter()

@router.post("/paginated-navigators", response_model=str)
async def create_paginated_navigator(
    options: PaginatedNavigatorOptions,
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Create a new paginated navigator.
    
    Args:
        options: Navigator options
        current_user: The current authenticated user
        
    Returns:
        Navigator ID
    """
    service = PaginationService()
    return await service.create_navigator(options)

@router.get("/paginated-navigators/{navigator_id}", response_model=PaginatedNavigatorState)
async def get_paginated_navigator_state(
    navigator_id: str,
    current_user: User = Depends(get_current_user)
) -> PaginatedNavigatorState:
    """
    Get paginated navigator state.
    
    Args:
        navigator_id: ID of the navigator
        current_user: The current authenticated user
        
    Returns:
        Navigator state
    """
    service = PaginationService()
    return await service.get_navigator_state(navigator_id)

@router.put("/paginated-navigators/{navigator_id}/filter")
async def set_paginated_filter(
    navigator_id: str,
    filter_text: Optional[str] = None,
    sort_field: Optional[str] = None,
    sort_order: Optional[SortOrder] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Set filter and sort parameters.
    
    Args:
        navigator_id: ID of the navigator
        filter_text: Filter text
        sort_field: Sort field
        sort_order: Sort order
        current_user: The current authenticated user
    """
    service = PaginationService()
    await service.set_filter(
        navigator_id,
        filter_text,
        sort_field,
        sort_order
    )

@router.post("/paginated-navigators/{navigator_id}/load-more")
async def load_more_data(
    navigator_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Load more data.
    
    Args:
        navigator_id: ID of the navigator
        current_user: The current authenticated user
    """
    service = PaginationService()
    await service.load_more(navigator_id)
