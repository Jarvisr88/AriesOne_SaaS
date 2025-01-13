"""
Data Access Layer Service Module

This module provides a comprehensive data access layer.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, Type, TypeVar, Generic
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, not_, desc, asc

T = TypeVar('T')

class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"

class FilterOperator(str, Enum):
    """Filter operator enumeration"""
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GE = "ge"
    LT = "lt"
    LE = "le"
    IN = "in"
    NOT_IN = "not_in"
    LIKE = "like"
    ILIKE = "ilike"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"

class FilterCondition(BaseModel):
    """Filter condition definition"""
    field: str
    operator: FilterOperator
    value: Any

class SortCondition(BaseModel):
    """Sort condition definition"""
    field: str
    order: SortOrder = SortOrder.ASC

class QueryOptions(BaseModel):
    """Query options"""
    filters: List[FilterCondition] = []
    sorts: List[SortCondition] = []
    limit: Optional[int] = None
    offset: Optional[int] = None
    includes: List[str] = []

class Repository(Generic[T]):
    """Generic repository base class"""
    
    def __init__(
        self,
        session: AsyncSession,
        model_type: Type[T]
    ):
        """Initialize repository"""
        self._session = session
        self._model_type = model_type

    async def get_by_id(
        self,
        id: Any,
        includes: Optional[List[str]] = None
    ) -> Optional[T]:
        """Get entity by ID"""
        query = select(self._model_type)
        
        if includes:
            for include in includes:
                query = query.options(joinedload(include))
        
        query = query.filter(self._model_type.id == id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        options: Optional[QueryOptions] = None
    ) -> List[T]:
        """Get all entities matching criteria"""
        query = select(self._model_type)
        
        if options:
            query = self._apply_query_options(query, options)
        
        result = await self._session.execute(query)
        return result.scalars().all()

    async def create(
        self,
        entity: T
    ) -> T:
        """Create new entity"""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(
        self,
        entity: T
    ) -> T:
        """Update existing entity"""
        await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(
        self,
        entity: T
    ):
        """Delete entity"""
        await self._session.delete(entity)
        await self._session.flush()

    async def delete_by_id(
        self,
        id: Any
    ):
        """Delete entity by ID"""
        entity = await self.get_by_id(id)
        if entity:
            await self.delete(entity)

    async def exists(
        self,
        id: Any
    ) -> bool:
        """Check if entity exists"""
        query = select(self._model_type.id).filter(self._model_type.id == id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None

    async def count(
        self,
        options: Optional[QueryOptions] = None
    ) -> int:
        """Count entities matching criteria"""
        query = select(self._model_type)
        
        if options:
            query = self._apply_query_options(query, options)
        
        result = await self._session.execute(query)
        return len(result.scalars().all())

    def _apply_query_options(
        self,
        query: Any,
        options: QueryOptions
    ) -> Any:
        """Apply query options to query"""
        # Apply includes
        if options.includes:
            for include in options.includes:
                query = query.options(joinedload(include))
        
        # Apply filters
        if options.filters:
            filter_conditions = []
            for filter_condition in options.filters:
                if filter_condition.operator == FilterOperator.EQ:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field) == filter_condition.value
                    )
                elif filter_condition.operator == FilterOperator.NE:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field) != filter_condition.value
                    )
                elif filter_condition.operator == FilterOperator.GT:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field) > filter_condition.value
                    )
                elif filter_condition.operator == FilterOperator.GE:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field) >= filter_condition.value
                    )
                elif filter_condition.operator == FilterOperator.LT:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field) < filter_condition.value
                    )
                elif filter_condition.operator == FilterOperator.LE:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field) <= filter_condition.value
                    )
                elif filter_condition.operator == FilterOperator.IN:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field).in_(filter_condition.value)
                    )
                elif filter_condition.operator == FilterOperator.NOT_IN:
                    filter_conditions.append(
                        ~getattr(self._model_type, filter_condition.field).in_(filter_condition.value)
                    )
                elif filter_condition.operator == FilterOperator.LIKE:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field).like(filter_condition.value)
                    )
                elif filter_condition.operator == FilterOperator.ILIKE:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field).ilike(filter_condition.value)
                    )
                elif filter_condition.operator == FilterOperator.BETWEEN:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field).between(
                            filter_condition.value[0],
                            filter_condition.value[1]
                        )
                    )
                elif filter_condition.operator == FilterOperator.IS_NULL:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field).is_(None)
                    )
                elif filter_condition.operator == FilterOperator.IS_NOT_NULL:
                    filter_conditions.append(
                        getattr(self._model_type, filter_condition.field).isnot(None)
                    )
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        # Apply sorts
        if options.sorts:
            for sort_condition in options.sorts:
                if sort_condition.order == SortOrder.ASC:
                    query = query.order_by(asc(getattr(self._model_type, sort_condition.field)))
                else:
                    query = query.order_by(desc(getattr(self._model_type, sort_condition.field)))
        
        # Apply pagination
        if options.offset is not None:
            query = query.offset(options.offset)
        if options.limit is not None:
            query = query.limit(options.limit)
        
        return query
