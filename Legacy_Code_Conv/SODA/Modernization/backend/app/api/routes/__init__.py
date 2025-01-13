"""API routes."""

from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .organizations import router as organizations_router
from .dmerc import router as dmerc_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(organizations_router)
api_router.include_router(dmerc_router)
