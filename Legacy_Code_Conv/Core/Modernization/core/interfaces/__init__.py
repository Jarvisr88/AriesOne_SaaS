"""
Core Interfaces Package
Version: 1.0.0
Last Updated: 2025-01-10

This package contains all core interface definitions for the system.
"""

from .IEntity import IEntity
from .IRepository import IRepository
from .IEventHandler import IEventHandler
from .INavigationService import INavigationService, NavigationState

__all__ = [
    'IEntity',
    'IRepository',
    'IEventHandler',
    'INavigationService',
    'NavigationState'
]
