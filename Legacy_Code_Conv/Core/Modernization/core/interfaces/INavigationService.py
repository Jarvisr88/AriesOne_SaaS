"""
Core Navigation Service Interface Module
Version: 1.0.0
Last Updated: 2025-01-10

This module defines the base interface for navigation services in the system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class NavigationState(BaseModel):
    """Navigation state model."""
    current_route: str
    params: Dict[str, Any]
    previous_route: Optional[str]
    history: List[str]
    user_id: UUID
    timestamp: float


class INavigationService(ABC):
    """Base interface for navigation services."""
    
    @abstractmethod
    async def navigate_to(self, route: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Navigate to a specific route."""
        pass
    
    @abstractmethod
    async def go_back(self) -> bool:
        """Navigate to the previous route."""
        pass
    
    @abstractmethod
    async def get_current_state(self) -> NavigationState:
        """Get the current navigation state."""
        pass
    
    @abstractmethod
    async def save_state(self) -> bool:
        """Save the current navigation state."""
        pass
    
    @abstractmethod
    async def restore_state(self, state: NavigationState) -> bool:
        """Restore a saved navigation state."""
        pass
    
    @abstractmethod
    async def clear_history(self) -> None:
        """Clear navigation history."""
        pass
    
    @abstractmethod
    async def can_navigate(self, route: str) -> bool:
        """Check if navigation to a route is allowed."""
        pass
    
    @abstractmethod
    async def register_route(self, route: str, handler: Any) -> None:
        """Register a new route handler."""
        pass
    
    @abstractmethod
    async def get_route_params(self, route: str) -> Dict[str, Any]:
        """Get parameters for a specific route."""
        pass
