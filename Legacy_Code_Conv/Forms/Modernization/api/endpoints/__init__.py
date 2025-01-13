"""API endpoints package.

This package contains all API endpoint modules.
"""
from fastapi import APIRouter

from .forms import router as forms_router
from .companies import router as companies_router


# Create main router
router = APIRouter()

# Include all routers
router.include_router(forms_router)
router.include_router(companies_router)
