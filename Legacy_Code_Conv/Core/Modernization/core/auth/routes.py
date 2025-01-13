"""
Authentication Routes Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from datetime import datetime, timedelta
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..security import (AuthenticationService, SecurityAuditLog,
                       get_current_active_user, get_current_user)
from ..utils.config import get_settings
from ..utils.security import get_password_hash

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["authentication"])


class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token data model."""
    sub: UUID
    exp: datetime
    type: str


class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    """User response model."""
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
) -> UserResponse:
    """Register a new user."""
    # Check if user exists
    auth_service = AuthenticationService(session)
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = await auth_service.create_user(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )

    # Log registration
    audit_log = SecurityAuditLog(
        event_type="user_registration",
        user_id=user.id,
        ip_address="0.0.0.0",  # TODO: Get from request
        resource="user",
        action="create",
        status="success"
    )
    session.add(audit_log)
    await session.commit()

    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
) -> Token:
    """Login to get access token."""
    auth_service = AuthenticationService(session)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = await auth_service.create_access_token(user.id)
    refresh_token = await auth_service.create_refresh_token(
        user.id,
        UUID(access_token)  # TODO: Get actual access token ID
    )

    # Log login
    audit_log = SecurityAuditLog(
        event_type="user_login",
        user_id=user.id,
        ip_address="0.0.0.0",  # TODO: Get from request
        resource="token",
        action="create",
        status="success"
    )
    session.add(audit_log)
    await session.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    session: AsyncSession = Depends(get_session)
) -> Token:
    """Get new access token using refresh token."""
    auth_service = AuthenticationService(session)
    user = await auth_service.verify_token(refresh_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token = await auth_service.create_access_token(user.id)
    new_refresh_token = await auth_service.create_refresh_token(
        user.id,
        UUID(access_token)  # TODO: Get actual access token ID
    )

    # Revoke old refresh token
    await auth_service.revoke_token(refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="token"))],
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Logout user and revoke token."""
    auth_service = AuthenticationService(session)
    await auth_service.revoke_token(token)

    # Log logout
    audit_log = SecurityAuditLog(
        event_type="user_logout",
        user_id=current_user.id,
        ip_address="0.0.0.0",  # TODO: Get from request
        resource="token",
        action="revoke",
        status="success"
    )
    session.add(audit_log)
    await session.commit()

    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    old_password: str,
    new_password: str,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Change user password."""
    auth_service = AuthenticationService(session)
    
    # Verify old password
    if not auth_service.verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    await session.commit()

    # Log password change
    audit_log = SecurityAuditLog(
        event_type="password_change",
        user_id=current_user.id,
        ip_address="0.0.0.0",  # TODO: Get from request
        resource="user",
        action="update",
        status="success"
    )
    session.add(audit_log)
    await session.commit()

    return {"message": "Password successfully changed"}
