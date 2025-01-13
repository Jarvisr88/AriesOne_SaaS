"""
Navigator Models Module

This module provides models for the navigation system.
"""
from typing import Optional, Dict, Any, List, Set
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class GridSortDirection(str, Enum):
    """Enumeration of grid sort directions"""
    ASCENDING = "ascending"
    DESCENDING = "descending"
    NONE = "none"

class GridFilterType(str, Enum):
    """Enumeration of grid filter types"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    CUSTOM = "custom"

class GridColumnDefinition(BaseModel):
    """Model for grid column definition"""
    field: str
    title: str
    width: Optional[int] = None
    sortable: bool = True
    filterable: bool = True
    visible: bool = True
    filter_type: GridFilterType = GridFilterType.TEXT
    format: Optional[str] = None
    template: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GridAppearance(BaseModel):
    """Model for grid appearance settings"""
    columns: List[GridColumnDefinition] = Field(default_factory=list)
    allow_sorting: bool = True
    allow_filtering: bool = True
    allow_column_reorder: bool = True
    allow_column_resize: bool = True
    row_height: Optional[int] = None
    header_height: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GridState(BaseModel):
    """Model for grid state"""
    filter_text: Optional[str] = None
    sort_field: Optional[str] = None
    sort_direction: GridSortDirection = GridSortDirection.NONE
    selected_rows: List[str] = Field(default_factory=list)
    visible_columns: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NavigatorOptions(BaseModel):
    """Model for navigator options"""
    caption: str = "Search"
    switchable: bool = True
    table_names: Set[str] = Field(default_factory=set)
    appearance: GridAppearance = Field(default_factory=GridAppearance)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CreateSourceEvent(BaseModel):
    """Model for create source event"""
    source_id: str
    table_names: Set[str]
    filter_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FillSourceEvent(BaseModel):
    """Model for fill source event"""
    source_id: str
    filter_text: Optional[str] = None
    sort_field: Optional[str] = None
    sort_direction: GridSortDirection = GridSortDirection.NONE
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NavigatorRowClickEvent(BaseModel):
    """Model for navigator row click event"""
    row_id: str
    row_data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NavigatorState(BaseModel):
    """Model for navigator state"""
    grid_state: GridState = Field(default_factory=GridState)
    options: NavigatorOptions
    is_loading: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
