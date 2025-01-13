"""
Core Security Package
Version: 1.0.0
Last Updated: 2025-01-10

This package provides security infrastructure for the core module.
"""

from .authentication import (AuthenticationService, get_current_user,
                           get_current_active_user, get_current_superuser)
from .authorization import AuthorizationService, require_permission
from .models import (User, Role, Permission, SecurityAuditLog,
                    AccessToken, RefreshToken)

__all__ = [
    # Authentication
    'AuthenticationService',
    'get_current_user',
    'get_current_active_user',
    'get_current_superuser',
    
    # Authorization
    'AuthorizationService',
    'require_permission',
    
    # Models
    'User',
    'Role',
    'Permission',
    'SecurityAuditLog',
    'AccessToken',
    'RefreshToken'
]
