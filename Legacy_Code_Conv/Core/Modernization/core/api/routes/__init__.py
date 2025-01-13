"""
API Routes Package
Version: 1.0.0
Last Updated: 2025-01-10

This package provides API routes for the core module.
"""

from .inventory import router as inventory_router
from .order import router as order_router
from .tenant import router as tenant_router

__all__ = [
    'inventory_router',
    'order_router',
    'tenant_router'
]
