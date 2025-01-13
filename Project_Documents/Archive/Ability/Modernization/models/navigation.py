"""
Navigation Models Module

This module provides models for navigation functionality.
"""
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID
from pydantic import BaseModel, Field

class NavigatorState(str, Enum):
    """Navigator state enumeration"""
    IDLE = "idle"
    LOADING = "loading"
    FILTERING = "filtering"
    ERROR = "error"

class GridAppearance(BaseModel):
    """Grid appearance configuration"""
    columns: List[str] = Field(default_factory=list, description="Visible columns")
    column_order: Dict[str, int] = Field(default_factory=dict, description="Column display order")
    column_widths: Dict[str, int] = Field(default_factory=dict, description="Column widths")
    sort_columns: List[str] = Field(default_factory=list, description="Sort columns")
    sort_directions: Dict[str, bool] = Field(default_factory=dict, description="Sort directions (True for ascending)")
    row_height: Optional[int] = Field(None, description="Row height in pixels")
    theme: Optional[str] = Field(None, description="Grid theme name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional appearance metadata")

class NavigatorOptions(BaseModel):
    """Navigator options model"""
    table_names: Set[str] = Field(default_factory=set, description="Allowed table names")
    appearance: GridAppearance = Field(default_factory=GridAppearance, description="Grid appearance")
    enable_filtering: bool = Field(default=True, description="Enable filtering")
    enable_sorting: bool = Field(default=True, description="Enable sorting")
    enable_column_resize: bool = Field(default=True, description="Enable column resize")
    enable_column_reorder: bool = Field(default=True, description="Enable column reorder")
    enable_row_selection: bool = Field(default=True, description="Enable row selection")
    page_size: Optional[int] = Field(None, description="Page size for paged navigation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional options metadata")

class NavigatorFilter(BaseModel):
    """Navigator filter model"""
    text: Optional[str] = Field(None, description="Filter text")
    columns: Optional[List[str]] = Field(None, description="Columns to filter")
    case_sensitive: bool = Field(default=False, description="Case sensitive filtering")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional filter metadata")

class NavigatorSort(BaseModel):
    """Navigator sort model"""
    column: str = Field(..., description="Sort column")
    ascending: bool = Field(default=True, description="Sort direction")

class NavigatorMetadata(BaseModel):
    """Navigator metadata model"""
    navigator_id: UUID = Field(..., description="Navigator ID")
    state: NavigatorState = Field(default=NavigatorState.IDLE, description="Navigator state")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    filter: Optional[NavigatorFilter] = Field(None, description="Current filter")
    sorts: List[NavigatorSort] = Field(default_factory=list, description="Current sorts")
    options: NavigatorOptions = Field(..., description="Navigator options")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class NavigatorData(BaseModel):
    """Navigator data model"""
    metadata: NavigatorMetadata = Field(..., description="Navigator metadata")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Grid data")
    total_rows: int = Field(default=0, description="Total number of rows")
    filtered_rows: int = Field(default=0, description="Number of filtered rows")
    page: Optional[int] = Field(None, description="Current page number")
    page_count: Optional[int] = Field(None, description="Total number of pages")

class NavigatorEvent(BaseModel):
    """Navigator event model"""
    event_type: str = Field(..., description="Event type")
    navigator_id: UUID = Field(..., description="Navigator ID")
    data: Optional[Dict[str, Any]] = Field(None, description="Event data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class RowClickEvent(BaseModel):
    """Row click event model"""
    navigator_id: UUID = Field(..., description="Navigator ID")
    row_index: int = Field(..., description="Row index")
    row_data: Dict[str, Any] = Field(..., description="Row data")
    column: Optional[str] = Field(None, description="Clicked column")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
