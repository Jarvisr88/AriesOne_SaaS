"""
Main application module with FastAPI configuration and documentation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .config import settings
from .utils.error_handlers import setup_error_handlers
from .api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=settings.OPENAPI_URL,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Set up error handlers
setup_error_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

def custom_openapi():
    """Customize OpenAPI documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="""
        AriesOne SaaS API Documentation
        
        This API provides endpoints for managing:
        * Entity Management
        * Table Management
        * Form Management
        * Navigation
        * Source Management
        * UI Attributes
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
