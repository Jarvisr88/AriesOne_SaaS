"""
Navigation Base Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides base classes for navigation management.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, validator

from ..utils.logging import CoreLogger

logger = CoreLogger(__name__)


class NavigationItem(BaseModel):
    """Base model for navigation items."""
    id: str = Field(..., description="Item ID")
    title: str = Field(..., description="Display title")
    path: str = Field(..., description="Navigation path")
    icon: Optional[str] = Field(None, description="Icon identifier")
    parent_id: Optional[str] = Field(None, description="Parent item ID")
    order: int = Field(default=0, description="Display order")
    requires_auth: bool = Field(default=True, description="Requires authentication")
    permissions: Set[str] = Field(
        default_factory=set,
        description="Required permissions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        """Set updated_at to current time."""
        return datetime.utcnow()


class NavigationMenu(BaseModel):
    """Base model for navigation menus."""
    id: str = Field(..., description="Menu ID")
    name: str = Field(..., description="Menu name")
    description: Optional[str] = Field(None, description="Menu description")
    items: List[NavigationItem] = Field(
        default_factory=list,
        description="Navigation items"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        """Set updated_at to current time."""
        return datetime.utcnow()


class NavigationContextBase(ABC):
    """Base class for navigation context."""
    
    @abstractmethod
    async def get_user_permissions(self) -> Set[str]:
        """Get current user's permissions."""
        pass
    
    @abstractmethod
    async def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        pass
    
    @abstractmethod
    async def get_user_preferences(self) -> Dict[str, Any]:
        """Get user's navigation preferences."""
        pass


class NavigationBuilderBase(ABC):
    """Base class for navigation builders."""
    
    @abstractmethod
    async def build_menu(self, menu: NavigationMenu,
                        context: NavigationContextBase) -> NavigationMenu:
        """Build navigation menu based on context."""
        try:
            # Get user permissions and authentication status
            permissions = await context.get_user_permissions()
            is_authenticated = await context.is_authenticated()
            
            # Filter items based on permissions and auth
            filtered_items = []
            for item in menu.items:
                if item.requires_auth and not is_authenticated:
                    continue
                if item.permissions and not permissions.intersection(item.permissions):
                    continue
                filtered_items.append(item)
            
            # Sort items by order
            filtered_items.sort(key=lambda x: x.order)
            
            # Create new menu with filtered items
            return NavigationMenu(
                id=menu.id,
                name=menu.name,
                description=menu.description,
                items=filtered_items,
                metadata=menu.metadata
            )
        except Exception as e:
            logger.error(f"Failed to build menu: {str(e)}")
            raise
    
    @abstractmethod
    async def build_breadcrumbs(self, current_path: str,
                               menu: NavigationMenu) -> List[NavigationItem]:
        """Build breadcrumbs for current path."""
        pass


class NavigationRepositoryBase(ABC):
    """Base class for navigation repositories."""
    
    @abstractmethod
    async def get_menu(self, menu_id: str) -> Optional[NavigationMenu]:
        """Get navigation menu by ID."""
        pass
    
    @abstractmethod
    async def save_menu(self, menu: NavigationMenu) -> NavigationMenu:
        """Save navigation menu."""
        pass
    
    @abstractmethod
    async def delete_menu(self, menu_id: str) -> bool:
        """Delete navigation menu."""
        pass
    
    @abstractmethod
    async def list_menus(self) -> List[NavigationMenu]:
        """List all navigation menus."""
        pass
    
    @abstractmethod
    async def get_item(self, item_id: str) -> Optional[NavigationItem]:
        """Get navigation item by ID."""
        pass
    
    @abstractmethod
    async def save_item(self, item: NavigationItem) -> NavigationItem:
        """Save navigation item."""
        pass
    
    @abstractmethod
    async def delete_item(self, item_id: str) -> bool:
        """Delete navigation item."""
        pass


class NavigationServiceBase(ABC):
    """Base class for navigation services."""
    
    def __init__(self, repository: NavigationRepositoryBase,
                 builder: NavigationBuilderBase):
        """Initialize navigation service."""
        self.repository = repository
        self.builder = builder
    
    @abstractmethod
    async def get_user_menu(self, menu_id: str,
                           context: NavigationContextBase) -> Optional[NavigationMenu]:
        """Get user-specific navigation menu."""
        try:
            # Get base menu
            menu = await self.repository.get_menu(menu_id)
            if not menu:
                return None
            
            # Build menu for user
            return await self.builder.build_menu(menu, context)
        except Exception as e:
            logger.error(f"Failed to get user menu: {str(e)}")
            raise
    
    @abstractmethod
    async def get_breadcrumbs(self, current_path: str,
                             menu_id: str) -> List[NavigationItem]:
        """Get breadcrumbs for current path."""
        try:
            # Get menu
            menu = await self.repository.get_menu(menu_id)
            if not menu:
                return []
            
            # Build breadcrumbs
            return await self.builder.build_breadcrumbs(current_path, menu)
        except Exception as e:
            logger.error(f"Failed to get breadcrumbs: {str(e)}")
            raise
