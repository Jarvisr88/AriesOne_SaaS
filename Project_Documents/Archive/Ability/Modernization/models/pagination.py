"""
Pagination Models Module

This module provides models for the pagination system.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

T = TypeVar('T')

class SortOrder(str, Enum):
    """Enumeration of sort orders"""
    ASC = "asc"
    DESC = "desc"

class PaginationFilter(BaseModel):
    """Model for pagination filter"""
    filter_text: Optional[str] = None
    start: int = 0
    count: int = 100
    sort_field: Optional[str] = None
    sort_order: Optional[SortOrder] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('start')
    def validate_start(cls, v):
        """Validate start index"""
        if v < 0:
            raise ValueError("start cannot be negative")
        return v
    
    @validator('count')
    def validate_count(cls, v):
        """Validate count"""
        if v < 0:
            raise ValueError("count cannot be negative")
        return v

class PageInfo(BaseModel):
    """Model for page information"""
    total_count: int
    page_size: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaginatedData(BaseModel, Generic[T]):
    """Model for paginated data"""
    items: List[T]
    page_info: PageInfo
    filter: PaginationFilter
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedNavigatorOptions(BaseModel):
    """Model for paginated navigator options"""
    caption: str = "Search"
    switchable: bool = True
    page_size: int = 100
    enable_infinite_scroll: bool = True
    enable_manual_pagination: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('page_size')
    def validate_page_size(cls, v):
        """Validate page size"""
        if v <= 0:
            raise ValueError("page_size must be positive")
        return v

class PaginatedNavigatorState(BaseModel):
    """Model for paginated navigator state"""
    filter: PaginationFilter = Field(default_factory=PaginationFilter)
    options: PaginatedNavigatorOptions
    is_loading: bool = False
    is_loading_more: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedSourceEvent(BaseModel):
    """Model for paginated source event"""
    source_id: str
    filter: PaginationFilter
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
