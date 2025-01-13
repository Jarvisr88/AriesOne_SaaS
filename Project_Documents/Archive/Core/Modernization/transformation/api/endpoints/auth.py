"""
Authentication endpoints for the Core module.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth.service import AuthService
from ...auth.models import UserCreate, UserUpdate, UserInDB
from ...database import get_session
from ...dependencies import get_current_user, get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserInDB)
async def register(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_session)
) -> UserInDB:
    """Register a new user."""
    auth_service = AuthService(session)
    user = await auth_service.create_user(user_create)
    return UserInDB.from_orm(user)

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Login to get access token."""
    auth_service = AuthService(session)
    user = await auth_service.authenticate_user(
        form_data.username,
        form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await auth_service.create_access_token(
        user,
        device_info=form_data.client_id
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserInDB)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """Get current user information."""
    return current_user

@router.put("/me", response_model=UserInDB)
async def update_user_me(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session)
) -> UserInDB:
    """Update current user information."""
    auth_service = AuthService(session)
    updated_user = await auth_service.update_user(
        current_user.id,
        user_update
    )
    return UserInDB.from_orm(updated_user)

@router.post("/logout")
async def logout(
    current_user: UserInDB = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Logout and revoke current token."""
    auth_service = AuthService(session)
    await auth_service.revoke_token(current_user.id)
    return {"message": "Successfully logged out"}
