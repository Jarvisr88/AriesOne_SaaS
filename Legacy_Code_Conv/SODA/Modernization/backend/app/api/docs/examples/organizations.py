"""Organization API examples."""

from datetime import datetime, timezone
from uuid import UUID

ORGANIZATION_CREATE = {
    "name": "Acme Healthcare",
    "code": "ACME001",
    "type": "PROVIDER",
    "description": "Leading healthcare provider in the region",
    "settings": {
        "billing": {
            "auto_invoice": True,
            "payment_terms": 30
        },
        "notifications": {
            "email": ["billing@acme.com", "admin@acme.com"],
            "sms": ["+1234567890"]
        }
    },
    "parent_id": "123e4567-e89b-12d3-a456-426614174000"
}

ORGANIZATION_RESPONSE = {
    "id": "234e5678-e89b-12d3-a456-426614174000",
    "name": "Acme Healthcare",
    "code": "ACME001",
    "type": "PROVIDER",
    "description": "Leading healthcare provider in the region",
    "status": "ACTIVE",
    "settings": {
        "billing": {
            "auto_invoice": True,
            "payment_terms": 30
        },
        "notifications": {
            "email": ["billing@acme.com", "admin@acme.com"],
            "sms": ["+1234567890"]
        }
    },
    "parent_id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-12T18:44:05Z",
    "created_by_id": "345e6789-e89b-12d3-a456-426614174000",
    "updated_by_id": "345e6789-e89b-12d3-a456-426614174000"
}

ORGANIZATION_UPDATE = {
    "name": "Acme Healthcare Systems",
    "description": "Leading healthcare provider in the Western region",
    "settings": {
        "billing": {
            "auto_invoice": False,
            "payment_terms": 45
        }
    }
}

USER_ORGANIZATION_CREATE = {
    "user_id": "345e6789-e89b-12d3-a456-426614174000",
    "role": "ADMIN",
    "permissions": {
        "billing": ["view", "edit"],
        "users": ["view", "edit", "delete"],
        "forms": ["view", "edit", "submit", "approve"]
    }
}

USER_ORGANIZATION_RESPONSE = {
    "organization_id": "234e5678-e89b-12d3-a456-426614174000",
    "user_id": "345e6789-e89b-12d3-a456-426614174000",
    "role": "ADMIN",
    "permissions": {
        "billing": ["view", "edit"],
        "users": ["view", "edit", "delete"],
        "forms": ["view", "edit", "submit", "approve"]
    },
    "created_at": "2025-01-12T18:44:05Z",
    "updated_at": None
}

ORGANIZATION_WITH_USERS = {
    **ORGANIZATION_RESPONSE,
    "users": [USER_ORGANIZATION_RESPONSE]
}

examples = {
    "create_organization": {
        "summary": "Create new organization",
        "description": "Create a new organization with settings and hierarchy",
        "value": ORGANIZATION_CREATE
    },
    "organization_response": {
        "summary": "Organization details",
        "description": "Detailed organization information including settings and timestamps",
        "value": ORGANIZATION_RESPONSE
    },
    "update_organization": {
        "summary": "Update organization",
        "description": "Update organization details and settings",
        "value": ORGANIZATION_UPDATE
    },
    "add_user": {
        "summary": "Add user to organization",
        "description": "Add a user to an organization with role and permissions",
        "value": USER_ORGANIZATION_CREATE
    },
    "user_organization": {
        "summary": "User organization details",
        "description": "User's role and permissions in an organization",
        "value": USER_ORGANIZATION_RESPONSE
    },
    "organization_with_users": {
        "summary": "Organization with users",
        "description": "Organization details including all users and their roles",
        "value": ORGANIZATION_WITH_USERS
    }
}
