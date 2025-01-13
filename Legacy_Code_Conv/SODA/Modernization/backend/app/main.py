"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import api_router
from .api.docs.api_docs import get_openapi_schema
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Override default OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi_schema()
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}
