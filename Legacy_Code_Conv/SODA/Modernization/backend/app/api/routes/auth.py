"""Authentication routes."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_user_service, get_current_active_user
from ..schemas.auth import (
    Token,
    LoginRequest,
    PasswordResetRequest,
    PasswordUpdateRequest
)
from ...services.user_service import UserService
from ...domain.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token)
async def login(
    request: LoginRequest,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> Token:
    """Login user and return access token."""
    user = await user_service.authenticate_user(
        request.email,
        request.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # TODO: Implement proper JWT token generation
    # For now, just return user ID as token
    return Token(access_token=str(user.id))

@router.post("/password/reset", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(
    request: PasswordResetRequest,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:
    """Request password reset."""
    await user_service.reset_password(request.email)

@router.post("/password/update")
async def update_password(
    request: PasswordUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:
    """Update user password."""
    success = await user_service.update_password(
        current_user.id,
        request.current_password,
        request.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

@router.post("/verify/{token}")
async def verify_email(
    token: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:
    """Verify user email."""
    success = await user_service.verify_email(current_user.id, token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
