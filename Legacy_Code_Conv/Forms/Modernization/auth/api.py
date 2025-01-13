"""Authentication API endpoints.

This module provides FastAPI endpoints for authentication and user management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.session import get_session
from .models import User
from .service import AuthenticationService, get_current_user
from .security import Token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
) -> Token:
    """Login endpoint to get access token.
    
    Args:
        request: FastAPI request object
        form_data: OAuth2 form data
        session: Database session
        
    Returns:
        Token: Access token response
    """
    service = AuthenticationService(session)
    
    # Get client info for audit log
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return await service.authenticate_user(
        form_data.username,
        form_data.password,
        ip_address=client_host,
        user_agent=user_agent
    )


@router.post("/register", response_model=dict)
async def register(
    username: str,
    email: str,
    password: str,
    roles: Optional[list[str]] = None,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Register new user.
    
    Args:
        username: Username for new user
        email: Email for new user
        password: Password for new user
        roles: Optional list of role names
        session: Database session
        
    Returns:
        dict: Success message
    """
    service = AuthenticationService(session)
    await service.create_user(username, email, password, roles)
    return {"message": "User registered successfully"}


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        dict: User information
    """
    service = AuthenticationService(session)
    permissions = await service.get_user_permissions(current_user)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "roles": [role.name for role in current_user.roles],
        "permissions": permissions,
        "last_login": current_user.last_login
    }


@router.post("/logout", response_model=dict)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Logout current user.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        dict: Success message
    """
    # Log the logout
    service = AuthenticationService(session)
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    await service._log_successful_login(
        current_user.id,
        ip_address=client_host,
        user_agent=user_agent
    )
    
    return {"message": "Successfully logged out"}
