"""
Paged Navigation Models Module

This module provides models for paged navigation functionality.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID
from pydantic import BaseModel, Field
from .navigation import NavigatorOptions, NavigatorFilter, NavigatorSort

class PagedNavigatorOptions(NavigatorOptions):
    """Extended navigator options with paging support"""
    page_size: int = Field(default=100, ge=1, le=1000)
    enable_paging: bool = True
    cache_pages: bool = True
    max_cached_pages: int = Field(default=10, ge=1, le=100)

class PagedFilter(NavigatorFilter):
    """Extended filter with paging support"""
    page_number: Optional[int] = Field(default=1, ge=1)
    items_per_page: Optional[int] = Field(default=100, ge=1, le=1000)
    total_items: Optional[int] = None
    total_pages: Optional[int] = None

class PagedFillSourceEventArgs(BaseModel):
    """Event arguments for paged source fill events"""
    page_number: int = Field(ge=1)
    items_per_page: int = Field(ge=1, le=1000)
    total_items: Optional[int] = None
    total_pages: Optional[int] = None
    filter: Optional[PagedFilter] = None
    sorts: Optional[List[NavigatorSort]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PagedNavigatorMetadata(BaseModel):
    """Metadata for paged navigation"""
    current_page: int = Field(default=1, ge=1)
    items_per_page: int = Field(default=100, ge=1, le=1000)
    total_items: Optional[int] = None
    total_pages: Optional[int] = None
    cached_pages: Set[int] = Field(default_factory=set)
    filter: Optional[PagedFilter] = None
    sorts: Optional[List[NavigatorSort]] = None
    options: PagedNavigatorOptions
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PagedNavigatorData(BaseModel):
    """Data model for paged navigation"""
    metadata: PagedNavigatorMetadata
    data: Dict[int, List[Dict[str, Any]]] = Field(default_factory=dict)  # page_number -> page_data
    
    class Config:
        arbitrary_types_allowed = True
