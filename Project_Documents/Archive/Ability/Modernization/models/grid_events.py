"""
Grid Events Model Module

This module provides models for grid-related events and data structures.
"""
from typing import Optional, Dict, Any, Generic, TypeVar, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from enum import Enum
from datetime import datetime

T = TypeVar('T')

class GridEventType(str, Enum):
    """Enumeration of grid event types"""
    DATA_FETCH = "data_fetch"
    DATA_UPDATE = "data_update"
    SELECTION_CHANGE = "selection_change"
    SORT_CHANGE = "sort_change"
    FILTER_CHANGE = "filter_change"
    PAGE_CHANGE = "page_change"
    CUSTOM = "custom"

class GridSortDirection(str, Enum):
    """Enumeration of sort directions"""
    ASCENDING = "ascending"
    DESCENDING = "descending"

class GridSortInfo(BaseModel):
    """Model for grid sorting information"""
    field: str
    direction: GridSortDirection
    priority: int = 0

class GridFilterOperator(str, Enum):
    """Enumeration of filter operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"

class GridFilterInfo(BaseModel):
    """Model for grid filter information"""
    field: str
    operator: GridFilterOperator
    value: Any
    logic: Optional[str] = None  # "and" or "or"

class GridPagingInfo(BaseModel):
    """Model for grid paging information"""
    page: int = 1
    page_size: int = 50
    total_records: Optional[int] = None
    total_pages: Optional[int] = None

class GridSourceEventArgs(GenericModel, Generic[T]):
    """
    Event arguments for grid source events.
    Generic type T represents the data type.
    """
    event_type: GridEventType
    data: Optional[List[T]] = None
    sort_info: List[GridSortInfo] = Field(default_factory=list)
    filter_info: List[GridFilterInfo] = Field(default_factory=list)
    paging_info: GridPagingInfo = Field(default_factory=GridPagingInfo)
    cancelled: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GridSelectionEventArgs(BaseModel):
    """Event arguments for grid selection changes"""
    selected_rows: List[str] = Field(default_factory=list)
    selected_cells: List[Dict[str, Any]] = Field(default_factory=list)
    is_all_selected: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GridCustomEventArgs(BaseModel):
    """Event arguments for custom grid events"""
    event_name: str
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GridStateSnapshot(BaseModel):
    """Model for capturing grid state"""
    sort_info: List[GridSortInfo] = Field(default_factory=list)
    filter_info: List[GridFilterInfo] = Field(default_factory=list)
    paging_info: GridPagingInfo = Field(default_factory=GridPagingInfo)
    selected_rows: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
