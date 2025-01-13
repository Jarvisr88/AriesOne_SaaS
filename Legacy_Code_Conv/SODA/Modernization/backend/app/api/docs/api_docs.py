"""API documentation configuration."""

from typing import Dict, Any

from .examples import auth, users, organizations, dmerc

tags_metadata = [
    {
        "name": "auth",
        "description": "Authentication operations including login, password management, and email verification."
    },
    {
        "name": "users",
        "description": "User management operations including creation, updates, and role management."
    },
    {
        "name": "organizations",
        "description": "Organization management including hierarchy, settings, and user membership."
    },
    {
        "name": "dmerc",
        "description": "DMERC form operations including creation, updates, attachments, and workflow management."
    }
]

responses = {
    400: {
        "description": "Bad Request - The request was invalid or cannot be served",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid request parameters"
                }
            }
        }
    },
    401: {
        "description": "Unauthorized - Authentication is required or has failed",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Not authenticated"
                }
            }
        }
    },
    403: {
        "description": "Forbidden - The request is not allowed",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Not authorized to perform this action"
                }
            }
        }
    },
    404: {
        "description": "Not Found - The requested resource was not found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Resource not found"
                }
            }
        }
    },
    422: {
        "description": "Unprocessable Entity - The request was well-formed but invalid",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["body", "email"],
                            "msg": "field required",
                            "type": "value_error.missing"
                        }
                    ]
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error - Something went wrong on the server",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Internal server error"
                }
            }
        }
    }
}

def get_openapi_schema() -> Dict[str, Any]:
    """Get OpenAPI schema configuration."""
    return {
        "openapi": "3.0.2",
        "info": {
            "title": "AriesOne SaaS API",
            "description": """
            AriesOne SaaS API provides endpoints for managing users, organizations, and DMERC forms.
            
            ## Authentication
            All endpoints except login and password reset require authentication using a JWT token.
            Include the token in the Authorization header: `Authorization: Bearer <token>`
            
            ## Rate Limiting
            API requests are rate limited to protect our services. Limits are:
            - 100 requests per minute for authenticated users
            - 10 requests per minute for unauthenticated users
            
            ## Pagination
            List endpoints support pagination using `offset` and `limit` parameters.
            Default values are offset=0 and limit=100.
            
            ## Errors
            The API uses standard HTTP response codes:
            - 2xx: Success
            - 4xx: Client errors
            - 5xx: Server errors
            
            Error responses include a detail message explaining the error.
            """,
            "version": "1.0.0",
            "contact": {
                "name": "AriesOne Support",
                "email": "support@ariesone.com",
                "url": "https://ariesone.com/support"
            },
            "license": {
                "name": "Proprietary",
                "url": "https://ariesone.com/license"
            }
        },
        "tags": tags_metadata,
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "responses": responses
        },
        "security": [{"bearerAuth": []}],
        "examples": {
            "auth": auth.examples,
            "users": users.examples,
            "organizations": organizations.examples,
            "dmerc": dmerc.examples
        }
    }
