"""
Navigator endpoints for the Core module.
"""
from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...services.navigator_service import NavigatorService
from ...models.navigator import (
    GridDefinition, GridState, GridFilter,
    GridDefinitionSchema, GridStateSchema, GridFilterSchema,
    FilterCondition, SortOrder
)
from ...database import get_session
from ...dependencies import get_current_active_user, check_permission
from ...auth.models import UserInDB

router = APIRouter(prefix="/navigator", tags=["navigator"])

@router.post("/grids", response_model=GridDefinition)
async def create_grid(
    grid_schema: GridDefinitionSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("navigator:create"))
) -> GridDefinition:
    """Create a new grid definition."""
    nav_service = NavigatorService(session)
    return await nav_service.create_grid_definition(grid_schema)

@router.get("/grids/{grid_id}", response_model=GridDefinition)
async def get_grid(
    grid_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("navigator:read"))
) -> GridDefinition:
    """Get grid definition by ID."""
    nav_service = NavigatorService(session)
    grid = await nav_service.get_grid_definition(grid_id)
    if not grid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid {grid_id} not found"
        )
    return grid

@router.post("/grids/state", response_model=GridState)
async def save_grid_state(
    state_schema: GridStateSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("navigator:update"))
) -> GridState:
    """Save grid state."""
    nav_service = NavigatorService(session)
    return await nav_service.save_grid_state(state_schema)

@router.get("/grids/{grid_id}/data")
async def get_grid_data(
    grid_id: int,
    page: int = 1,
    page_size: int = 50,
    sort_order: Optional[List[SortOrder]] = None,
    filters: Optional[List[FilterCondition]] = None,
    search_text: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("navigator:read"))
) -> dict:
    """Get paginated and filtered data for a grid."""
    nav_service = NavigatorService(session)
    data, total = await nav_service.get_data(
        grid_id,
        page,
        page_size,
        sort_order,
        filters,
        search_text
    )
    
    return {
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("/grids/filters", response_model=GridFilter)
async def save_filter(
    filter_schema: GridFilterSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("navigator:update"))
) -> GridFilter:
    """Save a grid filter."""
    nav_service = NavigatorService(session)
    return await nav_service.save_filter(filter_schema)

@router.get("/grids/{grid_id}/filters", response_model=List[GridFilter])
async def get_saved_filters(
    grid_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("navigator:read"))
) -> List[GridFilter]:
    """Get saved filters for a grid."""
    nav_service = NavigatorService(session)
    return await nav_service.get_saved_filters(grid_id, current_user.id)
