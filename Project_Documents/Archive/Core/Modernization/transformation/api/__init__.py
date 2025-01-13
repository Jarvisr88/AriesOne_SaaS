"""
API package for the Core module.
"""
from fastapi import APIRouter

from .endpoints import auth, forms, navigator, tables

# Create API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(forms.router)
api_router.include_router(navigator.router)
api_router.include_router(tables.router)
