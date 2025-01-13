"""
Core Navigation Service Base Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides the base implementation for navigation services in the system.
"""
from abc import ABC
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from uuid import UUID

from ..interfaces import INavigationService, NavigationState


class NavigationServiceBase(INavigationService, ABC):
    """Base class for navigation services providing common functionality."""
    
    def __init__(self):
        """Initialize navigation service."""
        self._routes: Dict[str, Callable] = {}
        self._history: List[NavigationState] = []
        self._current_state: Optional[NavigationState] = None
        self._max_history: int = 100
    
    async def navigate_to(self, route: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Navigate to a specific route."""
        if not await self.can_navigate(route):
            return False
        
        handler = self._routes.get(route)
        if not handler:
            return False
        
        previous_route = self._current_state.current_route if self._current_state else None
        
        self._current_state = NavigationState(
            current_route=route,
            params=params or {},
            previous_route=previous_route,
            history=self._get_route_history(),
            user_id=await self._get_current_user_id(),
            timestamp=datetime.utcnow().timestamp()
        )
        
        self._add_to_history(self._current_state)
        await self._persist_state(self._current_state)
        
        try:
            await handler(params or {})
            return True
        except Exception as e:
            await self._handle_navigation_error(e, route, params)
            return False
    
    async def go_back(self) -> bool:
        """Navigate to the previous route."""
        if not self._history or len(self._history) < 2:
            return False
        
        previous_state = self._history[-2]
        return await self.navigate_to(previous_state.current_route, previous_state.params)
    
    async def get_current_state(self) -> NavigationState:
        """Get the current navigation state."""
        return self._current_state
    
    async def save_state(self) -> bool:
        """Save the current navigation state."""
        if not self._current_state:
            return False
        return await self._persist_state(self._current_state)
    
    async def restore_state(self, state: NavigationState) -> bool:
        """Restore a saved navigation state."""
        return await self.navigate_to(state.current_route, state.params)
    
    async def clear_history(self) -> None:
        """Clear navigation history."""
        self._history.clear()
        await self._clear_persisted_history()
    
    async def can_navigate(self, route: str) -> bool:
        """Check if navigation to a route is allowed."""
        if route not in self._routes:
            return False
        return await self._check_route_permissions(route)
    
    async def register_route(self, route: str, handler: Callable) -> None:
        """Register a new route handler."""
        self._routes[route] = handler
    
    async def get_route_params(self, route: str) -> Dict[str, Any]:
        """Get parameters for a specific route."""
        if route not in self._routes:
            return {}
        return await self._get_route_metadata(route)
    
    def _add_to_history(self, state: NavigationState) -> None:
        """Add state to navigation history."""
        self._history.append(state)
        if len(self._history) > self._max_history:
            self._history.pop(0)
    
    def _get_route_history(self) -> List[str]:
        """Get the route history."""
        return [state.current_route for state in self._history]
    
    async def _get_current_user_id(self) -> UUID:
        """Get the current user ID."""
        # Implement in subclasses
        raise NotImplementedError
    
    async def _persist_state(self, state: NavigationState) -> bool:
        """Persist navigation state."""
        # Implement in subclasses
        raise NotImplementedError
    
    async def _clear_persisted_history(self) -> None:
        """Clear persisted navigation history."""
        # Implement in subclasses
        raise NotImplementedError
    
    async def _check_route_permissions(self, route: str) -> bool:
        """Check if current user has permission for route."""
        # Implement in subclasses
        raise NotImplementedError
    
    async def _get_route_metadata(self, route: str) -> Dict[str, Any]:
        """Get metadata for a route."""
        # Implement in subclasses
        raise NotImplementedError
    
    async def _handle_navigation_error(self, error: Exception, route: str,
                                     params: Optional[Dict[str, Any]]) -> None:
        """Handle navigation errors."""
        # Implement in subclasses
        raise NotImplementedError
