"""User API examples."""

from datetime import datetime, timezone
from uuid import UUID

USER_CREATE = {
    "email": "john.doe@example.com",
    "username": "johndoe",
    "password": "securePassword123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "USER",
    "status": "PENDING"
}

USER_RESPONSE = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "john.doe@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "role": "USER",
    "status": "ACTIVE",
    "is_verified": True,
    "email_verified_at": "2025-01-12T18:44:05Z",
    "last_login": "2025-01-12T18:30:00Z",
    "preferences": {
        "theme": "dark",
        "notifications": {
            "email": True,
            "push": False
        }
    },
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-12T18:44:05Z"
}

USER_UPDATE = {
    "first_name": "Jonathan",
    "last_name": "Doe",
    "preferences": {
        "theme": "light",
        "notifications": {
            "email": True,
            "push": True
        }
    }
}

USER_ADMIN_UPDATE = {
    "role": "ADMIN",
    "status": "ACTIVE"
}

USER_PREFERENCES_UPDATE = {
    "preferences": {
        "theme": "dark",
        "notifications": {
            "email": True,
            "push": True
        },
        "dashboard": {
            "layout": "compact",
            "widgets": ["stats", "recent_forms", "tasks"]
        }
    }
}

examples = {
    "create_user": {
        "summary": "Create new user",
        "description": "Create a new user account with basic information",
        "value": USER_CREATE
    },
    "user_response": {
        "summary": "User details",
        "description": "Detailed user information including preferences and timestamps",
        "value": USER_RESPONSE
    },
    "update_user": {
        "summary": "Update user details",
        "description": "Update user's personal information and preferences",
        "value": USER_UPDATE
    },
    "admin_update": {
        "summary": "Admin update user",
        "description": "Update user's role and status (admin only)",
        "value": USER_ADMIN_UPDATE
    },
    "preferences_update": {
        "summary": "Update preferences",
        "description": "Update user's application preferences",
        "value": USER_PREFERENCES_UPDATE
    }
}
