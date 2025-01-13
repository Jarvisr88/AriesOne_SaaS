"""
API Package

This package provides FastAPI endpoints for the Common module.
"""
from fastapi import APIRouter

from .common_endpoints import router as common_router
from .file_endpoints import router as file_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(common_router)
router.include_router(file_router)

__all__ = ["router"]
