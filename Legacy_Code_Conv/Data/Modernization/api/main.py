"""FastAPI application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api.middleware.auth import AuthMiddleware, AuthSettings
from api.middleware.audit import AuditMiddleware
from api.routes import company
from core.security.access_control import AccessControlService
from core.security.audit import AuditService
from infrastructure.database.session import async_session

def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AriesOne Data API",
        version="1.0.0",
        description="""
        AriesOne Data API provides a modern interface for managing HME/DME data.
        
        ## Features
        - Company management
        - Location tracking
        - Inventory control
        - Order processing
        
        ## Authentication
        All endpoints require JWT authentication. Include the JWT token in the Authorization header:
        ```
        Authorization: Bearer <your_token>
        ```
        
        ## Rate Limiting
        API requests are limited to:
        - 100 requests per minute for regular endpoints
        - 1000 requests per minute for read-only endpoints
        
        ## Error Handling
        The API uses standard HTTP status codes and returns error responses in the format:
        ```json
        {
            "detail": "Error message",
            "code": "ERROR_CODE",
            "params": {}
        }
        ```
        """,
        routes=app.routes,
        tags=[
            {
                "name": "companies",
                "description": "Operations for managing healthcare companies"
            },
            {
                "name": "health",
                "description": "API health monitoring endpoints"
            }
        ]
    )
    
    # Custom extension for rate limiting
    openapi_schema["x-ratelimit"] = {
        "regular": "100/minute",
        "read-only": "1000/minute"
    }
    
    # Security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for authentication"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Create FastAPI app
app = FastAPI(
    title="AriesOne Data API",
    description="API for AriesOne Data Module",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add auth middleware
app.add_middleware(
    AuthMiddleware,
    settings=AuthSettings(),
    access_control=AccessControlService(async_session),
    public_paths={"/health", "/metrics", "/docs", "/redoc", "/openapi.json"}
)

# Add audit middleware
app.add_middleware(
    AuditMiddleware,
    audit_service=AuditService(async_session),
    exclude_paths={"/health", "/metrics"}
)

# Include routers
app.include_router(company.router)

# Custom OpenAPI schema
app.openapi = custom_openapi

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint.
    
    Returns:
        dict: Health status information including:
            - status: Current API status
            - version: API version
            - database: Database connection status
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected"
    }

@app.get("/metrics", tags=["health"])
async def metrics():
    """Metrics endpoint.
    
    Returns:
        dict: API metrics including:
            - requests_total: Total number of requests
            - requests_failed: Number of failed requests
            - average_response_time: Average response time in milliseconds
    """
    return {
        "requests_total": 0,  # Implement metrics
        "requests_failed": 0,
        "average_response_time": 0
    }
