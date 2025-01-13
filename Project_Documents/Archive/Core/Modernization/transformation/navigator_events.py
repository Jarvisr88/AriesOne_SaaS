"""
Navigator Events Models
Author: Cascade AI
Date: 2025-01-08
"""

from typing import Optional, List, Dict, Any, TypeVar, Generic, Protocol, runtime_checkable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from abc import ABC, abstractmethod

T = TypeVar('T')

class NavigatorEventContext(BaseModel):
    """Navigator event context."""
    user_id: str
    session_id: str
    navigator_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NavigatorEventResult(BaseModel):
    """Navigator event result."""
    success: bool
    message: Optional[str]
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    duration_ms: Optional[float]

class NavigatorSourceType(str, Enum):
    """Navigator source types."""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    MEMORY = "memory"
    CUSTOM = "custom"

class NavigatorSourceConfig(BaseModel):
    """Navigator source configuration."""
    type: NavigatorSourceType
    connection: Optional[str]
    query: Optional[str]
    params: Dict[str, Any] = Field(default_factory=dict)
    cache_key: Optional[str]
    cache_ttl: Optional[int]
    batch_size: Optional[int]
    timeout: Optional[int]
    retry_count: Optional[int]
    custom_config: Optional[Dict[str, Any]]

class NavigatorSourceResult(BaseModel, Generic[T]):
    """Navigator source result."""
    items: List[T]
    total: int
    page: int
    page_size: int
    has_more: bool
    cursor: Optional[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NavigatorRowData(BaseModel):
    """Navigator row data."""
    id: str
    index: int
    data: Dict[str, Any]
    selected: bool = False
    expanded: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class NavigatorAppearanceTheme(str, Enum):
    """Navigator appearance themes."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    CUSTOM = "custom"

class NavigatorAppearanceConfig(BaseModel):
    """Navigator appearance configuration."""
    theme: NavigatorAppearanceTheme = NavigatorAppearanceTheme.SYSTEM
    font_family: Optional[str]
    font_size: Optional[int]
    row_height: Optional[int]
    header_height: Optional[int]
    border_radius: Optional[int]
    custom_styles: Optional[Dict[str, Any]]
    animations: bool = True
    compact: bool = False

@runtime_checkable
class NavigatorEventHandler(Protocol[T]):
    """Navigator event handler protocol."""
    
    async def create_source(
        self,
        context: NavigatorEventContext,
        config: NavigatorSourceConfig
    ) -> NavigatorSourceResult[T]:
        """Create data source."""
        ...
    
    async def fill_source(
        self,
        context: NavigatorEventContext,
        config: NavigatorSourceConfig,
        page: int,
        page_size: int,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None
    ) -> NavigatorSourceResult[T]:
        """Fill data source."""
        ...
    
    async def handle_row_click(
        self,
        context: NavigatorEventContext,
        row: NavigatorRowData
    ) -> NavigatorEventResult:
        """Handle row click event."""
        ...
    
    async def initialize_appearance(
        self,
        context: NavigatorEventContext,
        config: NavigatorAppearanceConfig
    ) -> NavigatorEventResult:
        """Initialize appearance."""
        ...
    
    @property
    def caption(self) -> str:
        """Get caption."""
        return "Search"
    
    @property
    def switchable(self) -> bool:
        """Get switchable state."""
        return True
    
    @property
    def table_names(self) -> List[str]:
        """Get table names."""
        return []

class BaseNavigatorEventHandler(ABC, Generic[T]):
    """Base navigator event handler."""
    
    def __init__(self):
        """Initialize handler."""
        self._caption = "Search"
        self._switchable = True
        self._table_names: List[str] = []
    
    @abstractmethod
    async def create_source(
        self,
        context: NavigatorEventContext,
        config: NavigatorSourceConfig
    ) -> NavigatorSourceResult[T]:
        """Create data source."""
        raise NotImplementedError
    
    @abstractmethod
    async def fill_source(
        self,
        context: NavigatorEventContext,
        config: NavigatorSourceConfig,
        page: int,
        page_size: int,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None
    ) -> NavigatorSourceResult[T]:
        """Fill data source."""
        raise NotImplementedError
    
    @abstractmethod
    async def handle_row_click(
        self,
        context: NavigatorEventContext,
        row: NavigatorRowData
    ) -> NavigatorEventResult:
        """Handle row click event."""
        raise NotImplementedError
    
    @abstractmethod
    async def initialize_appearance(
        self,
        context: NavigatorEventContext,
        config: NavigatorAppearanceConfig
    ) -> NavigatorEventResult:
        """Initialize appearance."""
        raise NotImplementedError
    
    @property
    def caption(self) -> str:
        """Get caption."""
        return self._caption
    
    @caption.setter
    def caption(self, value: str):
        """Set caption."""
        self._caption = value
    
    @property
    def switchable(self) -> bool:
        """Get switchable state."""
        return self._switchable
    
    @switchable.setter
    def switchable(self, value: bool):
        """Set switchable state."""
        self._switchable = value
    
    @property
    def table_names(self) -> List[str]:
        """Get table names."""
        return self._table_names
    
    @table_names.setter
    def table_names(self, value: List[str]):
        """Set table names."""
        self._table_names = value
