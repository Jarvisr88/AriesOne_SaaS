"""
Dependencies for FastAPI endpoints.
"""
from typing import Optional, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.service import AuthService
from ..auth.models import UserInDB
from ..database import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> UserInDB:
    """Get current user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    auth_service = AuthService(session)
    user = await auth_service.verify_token(token)
    if not user:
        raise credentials_exception
    
    return UserInDB.from_orm(user)

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def check_permission(required_permission: str) -> Callable:
    """Check if user has required permission."""
    async def permission_checker(
        current_user: UserInDB = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session)
    ) -> None:
        auth_service = AuthService(session)
        has_permission = await auth_service.check_permission(
            current_user,
            required_permission
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {required_permission} required"
            )
    
    return permission_checker
