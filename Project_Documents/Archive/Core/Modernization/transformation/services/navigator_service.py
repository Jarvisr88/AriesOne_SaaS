"""
Navigator service for the Core module.
Handles data navigation, filtering, and grid operations.
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy import and_, or_, text
from sqlalchemy.sql import Select

from .base_service import BaseService
from ..models.navigator import (
    GridDefinition, GridState, GridFilter,
    GridDefinitionSchema, GridStateSchema, GridFilterSchema,
    FilterCondition, SortOrder
)

class NavigatorService(BaseService):
    """Service for handling navigation and grid operations."""

    async def create_grid_definition(
        self,
        schema: GridDefinitionSchema
    ) -> GridDefinition:
        """Create a new grid definition."""
        # Validate grid name uniqueness
        existing = await self._get_grid_by_name(schema.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Grid with name '{schema.name}' already exists"
            )
        
        return await self.create(GridDefinition, schema)

    async def get_grid_definition(
        self,
        grid_id: int
    ) -> Optional[GridDefinition]:
        """Get grid definition by ID."""
        grid = await self.get(GridDefinition, grid_id)
        if not grid:
            raise HTTPException(
                status_code=404,
                detail=f"Grid definition {grid_id} not found"
            )
        return grid

    async def save_grid_state(
        self,
        schema: GridStateSchema
    ) -> GridState:
        """Save grid state."""
        # Check if state exists
        existing_state = await self._get_grid_state(
            schema.grid_definition_id,
            schema.user_id
        )
        
        if existing_state:
            return await self.update(GridState, existing_state.id, schema)
        else:
            return await self.create(GridState, schema)

    async def get_data(
        self,
        grid_id: int,
        page: int = 1,
        page_size: int = 50,
        sort_order: Optional[List[SortOrder]] = None,
        filters: Optional[List[FilterCondition]] = None,
        search_text: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated and filtered data for a grid."""
        # Get grid definition
        grid_def = await self.get_grid_definition(grid_id)
        if not grid_def:
            raise HTTPException(
                status_code=404,
                detail=f"Grid definition {grid_id} not found"
            )

        try:
            # Build base query
            query = await self._build_base_query(grid_def)
            
            # Apply filters
            if filters:
                query = await self._apply_filters(query, filters)
            
            # Apply search
            if search_text:
                query = await self._apply_search(query, grid_def, search_text)
            
            # Apply sorting
            if sort_order:
                query = await self._apply_sorting(query, sort_order)
            
            # Get total count
            count_query = query.with_only_columns([text('COUNT(*)')])
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            query = query.offset((page - 1) * page_size).limit(page_size)
            
            # Execute query
            result = await self.db.execute(query)
            data = [dict(row) for row in result.mappings()]
            
            return data, total

        except Exception as e:
            await self._log_error(str(e), "grid_query_error", f"grid_{grid_id}")
            raise HTTPException(
                status_code=400,
                detail=f"Error querying grid data: {str(e)}"
            )

    async def save_filter(
        self,
        schema: GridFilterSchema
    ) -> GridFilter:
        """Save a grid filter."""
        return await self.create(GridFilter, schema)

    async def get_saved_filters(
        self,
        grid_id: int,
        user_id: str
    ) -> List[GridFilter]:
        """Get saved filters for a grid."""
        query = select(GridFilter).where(
            and_(
                GridFilter.grid_definition_id == grid_id,
                or_(
                    GridFilter.created_by == user_id,
                    GridFilter.is_global == True
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _get_grid_by_name(
        self,
        name: str
    ) -> Optional[GridDefinition]:
        """Get grid definition by name."""
        query = select(GridDefinition).where(GridDefinition.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_grid_state(
        self,
        grid_id: int,
        user_id: str
    ) -> Optional[GridState]:
        """Get grid state for a user."""
        query = select(GridState).where(
            and_(
                GridState.grid_definition_id == grid_id,
                GridState.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _build_base_query(
        self,
        grid_def: GridDefinition
    ) -> Select:
        """Build base query for grid data."""
        # This is a placeholder - actual implementation would depend on
        # how we store and retrieve grid data
        return select([text('*')]).select_from(text(grid_def.name))

    async def _apply_filters(
        self,
        query: Select,
        filters: List[FilterCondition]
    ) -> Select:
        """Apply filters to query."""
        for filter_condition in filters:
            field = filter_condition.field
            operator = filter_condition.operator
            value = filter_condition.value
            
            if operator == 'eq':
                query = query.where(text(f"{field} = :value"))
            elif operator == 'neq':
                query = query.where(text(f"{field} != :value"))
            elif operator == 'gt':
                query = query.where(text(f"{field} > :value"))
            elif operator == 'gte':
                query = query.where(text(f"{field} >= :value"))
            elif operator == 'lt':
                query = query.where(text(f"{field} < :value"))
            elif operator == 'lte':
                query = query.where(text(f"{field} <= :value"))
            elif operator == 'contains':
                query = query.where(text(f"{field} LIKE :value"))
                value = f"%{value}%"
            elif operator == 'startswith':
                query = query.where(text(f"{field} LIKE :value"))
                value = f"{value}%"
            elif operator == 'endswith':
                query = query.where(text(f"{field} LIKE :value"))
                value = f"%{value}"
            
            query = query.params(value=value)
        
        return query

    async def _apply_search(
        self,
        query: Select,
        grid_def: GridDefinition,
        search_text: str
    ) -> Select:
        """Apply search to query."""
        search_conditions = []
        for column in grid_def.columns:
            if column.get('searchable', True):
                field = column['field']
                search_conditions.append(
                    text(f"{field} LIKE :search_text")
                )
        
        if search_conditions:
            query = query.where(
                or_(*search_conditions)
            ).params(search_text=f"%{search_text}%")
        
        return query

    async def _apply_sorting(
        self,
        query: Select,
        sort_order: List[SortOrder]
    ) -> Select:
        """Apply sorting to query."""
        for sort in sort_order:
            direction = 'ASC' if sort.direction == 'asc' else 'DESC'
            query = query.order_by(text(f"{sort.field} {direction}"))
        
        return query
