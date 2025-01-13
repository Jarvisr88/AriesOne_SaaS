"""API package.

This package contains API schemas and endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from .endpoints import router as api_router


settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Forms API",
    description="API for form management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API router
app.include_router(api_router, prefix="/api/v1")
