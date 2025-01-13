"""
Authentication dependencies.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .models import User, Permission
from .service import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = None  # Add your DB dependency
) -> User:
    """Get current user.
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def check_permission(permission: Permission):
    """Create permission checker.
    
    Args:
        permission: Required permission
        
    Returns:
        Permission checker function
    """
    async def permission_checker(
        user: User = Depends(get_current_active_user)
    ) -> User:
        """Check user permission.
        
        Args:
            user: Current user
            
        Returns:
            User if authorized
            
        Raises:
            HTTPException: If not authorized
        """
        if not any(
            p == permission.value
            for p in RolePermissions.MAPPINGS[user.role]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user
        
    return permission_checker
