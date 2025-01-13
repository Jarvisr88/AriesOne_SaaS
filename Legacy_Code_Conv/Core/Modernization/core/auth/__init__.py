"""
Authentication Package
Version: 1.0.0
Last Updated: 2025-01-10

This package provides authentication functionality for the core module.
"""

from .dependencies import (get_current_active_user, get_current_superuser,
                         get_current_user, get_optional_user)
from .middleware import AuthMiddleware
from .routes import router as auth_router

__all__ = [
    # Dependencies
    'get_current_user',
    'get_current_active_user',
    'get_current_superuser',
    'get_optional_user',
    
    # Middleware
    'AuthMiddleware',
    
    # Routes
    'auth_router'
]
