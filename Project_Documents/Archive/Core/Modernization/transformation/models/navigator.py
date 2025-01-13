"""
Navigator models for the Core module.
Handles data navigation, filtering, and grid state management.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator

from .base import BaseDBModel, BaseSchema

class GridDefinition(BaseDBModel):
    """Database model for grid definitions."""
    __tablename__ = "core_grid_definitions"

    name = Column(String(100), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    columns = Column(JSON, nullable=False)
    default_sort = Column(JSON, nullable=True)
    default_filters = Column(JSON, nullable=True)
    permissions = Column(JSON, nullable=False)
    page_size = Column(Integer, nullable=False, default=50)
    allow_selection = Column(Boolean, nullable=False, default=True)
    allow_filtering = Column(Boolean, nullable=False, default=True)
    allow_sorting = Column(Boolean, nullable=False, default=True)

class GridState(BaseDBModel):
    """Database model for grid states."""
    __tablename__ = "core_grid_states"

    grid_definition_id = Column(Integer, ForeignKey("core_grid_definitions.id"), nullable=False)
    user_id = Column(String(50), nullable=False)
    current_page = Column(Integer, nullable=False, default=1)
    page_size = Column(Integer, nullable=False)
    sort_order = Column(JSON, nullable=True)
    filters = Column(JSON, nullable=True)
    selected_rows = Column(JSON, nullable=True)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GridFilter(BaseDBModel):
    """Database model for saved grid filters."""
    __tablename__ = "core_grid_filters"

    grid_definition_id = Column(Integer, ForeignKey("core_grid_definitions.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    filter_definition = Column(JSON, nullable=False)
    is_global = Column(Boolean, nullable=False, default=False)
    created_by = Column(String(50), nullable=False)

# Pydantic Schemas

class ColumnDefinition(BaseModel):
    """Schema for grid column definition."""
    field: str
    header: str
    type: str
    width: Optional[int] = None
    sortable: bool = True
    filterable: bool = True
    visible: bool = True
    format: Optional[str] = None
    template: Optional[str] = None
    style: Optional[Dict[str, str]] = None

    @validator('type')
    def validate_type(cls, v):
        valid_types = {'text', 'number', 'date', 'boolean', 'custom'}
        if v not in valid_types:
            raise ValueError(f'Invalid column type. Must be one of {valid_types}')
        return v

class SortOrder(BaseModel):
    """Schema for sort order."""
    field: str
    direction: str

    @validator('direction')
    def validate_direction(cls, v):
        if v not in {'asc', 'desc'}:
            raise ValueError('Direction must be either "asc" or "desc"')
        return v

class FilterCondition(BaseModel):
    """Schema for filter condition."""
    field: str
    operator: str
    value: Any
    logic: Optional[str] = 'and'

    @validator('operator')
    def validate_operator(cls, v):
        valid_operators = {'eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'contains', 'startswith', 'endswith'}
        if v not in valid_operators:
            raise ValueError(f'Invalid operator. Must be one of {valid_operators}')
        return v

    @validator('logic')
    def validate_logic(cls, v):
        if v not in {'and', 'or'}:
            raise ValueError('Logic must be either "and" or "or"')
        return v

class GridDefinitionSchema(BaseSchema):
    """Schema for grid definition."""
    name: str
    title: str
    description: Optional[str] = None
    columns: List[ColumnDefinition]
    default_sort: Optional[List[SortOrder]] = None
    default_filters: Optional[List[FilterCondition]] = None
    permissions: Dict[str, List[str]]
    page_size: int = Field(50, ge=1, le=1000)
    allow_selection: bool = True
    allow_filtering: bool = True
    allow_sorting: bool = True

class GridStateSchema(BaseSchema):
    """Schema for grid state."""
    grid_definition_id: int
    user_id: str
    current_page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=1000)
    sort_order: Optional[List[SortOrder]] = None
    filters: Optional[List[FilterCondition]] = None
    selected_rows: Optional[List[int]] = None
    last_modified: Optional[datetime] = None

class GridFilterSchema(BaseSchema):
    """Schema for saved grid filter."""
    grid_definition_id: int
    name: str
    description: Optional[str] = None
    filter_definition: List[FilterCondition]
    is_global: bool = False
    created_by: str
