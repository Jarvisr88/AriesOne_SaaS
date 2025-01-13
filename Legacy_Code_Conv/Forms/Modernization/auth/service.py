"""Authentication service module.

This module provides authentication and authorization services.
"""
from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.db.session import get_session
from .models import User, Role, Permission, AuditLog
from .security import (
    Token,
    verify_password,
    get_password_hash,
    create_token_response,
    verify_token
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthenticationService:
    """Authentication service for user management and authentication."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service with database session.
        
        Args:
            session: Async database session
        """
        self.session = session
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Token:
        """Authenticate user and return access token.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            ip_address: Optional IP address for audit log
            user_agent: Optional user agent for audit log
            
        Returns:
            Token: Access token response
            
        Raises:
            HTTPException: If authentication fails
        """
        user = await self.get_user_by_username(username)
        
        if not user or not verify_password(password, user.hashed_password):
            await self._log_failed_login(
                username, ip_address, user_agent
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.session.commit()
        
        # Get user permissions
        scopes = await self.get_user_permissions(user)
        
        # Create token
        token = create_token_response(username, scopes)
        
        # Log successful login
        await self._log_successful_login(
            user.id, ip_address, user_agent
        )
        
        return token
    
    async def get_user_by_username(
        self,
        username: str
    ) -> Optional[User]:
        """Get user by username.
        
        Args:
            username: Username to lookup
            
        Returns:
            Optional[User]: User if found, None otherwise
        """
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: list[str] = None
    ) -> User:
        """Create new user.
        
        Args:
            username: Username for new user
            email: Email for new user
            password: Password for new user
            roles: Optional list of role names
            
        Returns:
            User: Created user
            
        Raises:
            HTTPException: If user already exists
        """
        # Check if user exists
        if await self.get_user_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password)
        )
        
        # Add roles if specified
        if roles:
            role_objects = await self._get_roles_by_names(roles)
            user.roles.extend(role_objects)
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def get_user_permissions(self, user: User) -> list[str]:
        """Get all permissions for user.
        
        Args:
            user: User to get permissions for
            
        Returns:
            list[str]: List of permission names
        """
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        return list(permissions)
    
    async def _get_roles_by_names(
        self,
        role_names: list[str]
    ) -> list[Role]:
        """Get roles by names.
        
        Args:
            role_names: List of role names
            
        Returns:
            list[Role]: List of found roles
            
        Raises:
            HTTPException: If any role not found
        """
        result = await self.session.execute(
            select(Role).where(Role.name.in_(role_names))
        )
        roles = result.scalars().all()
        
        if len(roles) != len(role_names):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more roles not found"
            )
        
        return roles
    
    async def _log_successful_login(
        self,
        user_id: int,
        ip_address: Optional[str],
        user_agent: Optional[str]
    ) -> None:
        """Log successful login attempt.
        
        Args:
            user_id: ID of user who logged in
            ip_address: Optional IP address
            user_agent: Optional user agent
        """
        log = AuditLog(
            user_id=user_id,
            action="login_success",
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(log)
        await self.session.commit()
    
    async def _log_failed_login(
        self,
        username: str,
        ip_address: Optional[str],
        user_agent: Optional[str]
    ) -> None:
        """Log failed login attempt.
        
        Args:
            username: Username that failed
            ip_address: Optional IP address
            user_agent: Optional user agent
        """
        log = AuditLog(
            user_id=None,
            action="login_failed",
            details=f"Failed login attempt for username: {username}",
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(log)
        await self.session.commit()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Get current authenticated user.
    
    Args:
        token: JWT token from request
        session: Database session
        
    Returns:
        User: Authenticated user
        
    Raises:
        HTTPException: If token invalid or user not found
    """
    try:
        token_data = verify_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    service = AuthenticationService(session)
    user = await service.get_user_by_username(token_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user
