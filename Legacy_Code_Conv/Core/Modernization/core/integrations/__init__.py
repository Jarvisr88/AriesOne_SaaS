"""
Core Integrations Package
Version: 1.0.0
Last Updated: 2025-01-10

This package provides integration components for the core module.
"""

from .api import router as api_router
from .database import DatabaseIntegration, get_db_integration
from .event_bus import Event, EventBusIntegration, get_event_bus

__all__ = [
    'api_router',
    'DatabaseIntegration',
    'get_db_integration',
    'Event',
    'EventBusIntegration',
    'get_event_bus'
]
