"""
Authentication Dependencies Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..security import AuthenticationService, User
from ..utils.config import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session)
) -> User:
    """Get current authenticated user."""
    auth_service = AuthenticationService(session)
    user = await auth_service.verify_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user


async def get_optional_user(
    request: Request,
    token: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not token:
        return None

    auth_service = AuthenticationService(session)
    return await auth_service.verify_token(token)
