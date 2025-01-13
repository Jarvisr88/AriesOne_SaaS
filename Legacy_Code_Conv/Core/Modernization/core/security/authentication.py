"""
Core Authentication Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides authentication functionality.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..utils.config import get_settings
from ..utils.security import get_password_hash, verify_password
from .models import AccessToken, RefreshToken, User

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthenticationService:
    """Service for handling authentication."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self._session = session
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        stmt = select(User).where(User.username == username, User.is_active == True)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
            
        return user
    
    async def create_access_token(self, user_id: UUID,
                                expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        expires = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        token_data = {
            "sub": str(user_id),
            "exp": expires,
            "type": "access"
        }
        
        token = jwt.encode(
            token_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        # Store token in database
        db_token = AccessToken(
            user_id=user_id,
            token=token,
            expires_at=expires
        )
        self._session.add(db_token)
        await self._session.commit()
        
        return token
    
    async def create_refresh_token(self, user_id: UUID,
                                 access_token_id: UUID) -> str:
        """Create refresh token."""
        expires = datetime.utcnow() + timedelta(days=30)
        
        token_data = {
            "sub": str(user_id),
            "exp": expires,
            "type": "refresh"
        }
        
        token = jwt.encode(
            token_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        # Store token in database
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            access_token_id=access_token_id,
            expires_at=expires
        )
        self._session.add(db_token)
        await self._session.commit()
        
        return token
    
    async def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id = UUID(payload["sub"])
            token_type = payload.get("type")
            
            if token_type not in ["access", "refresh"]:
                return None
                
            # Check if token is revoked
            stmt = select(AccessToken if token_type == "access" else RefreshToken).where(
                AccessToken.token == token if token_type == "access"
                else RefreshToken.token == token,
                AccessToken.is_revoked == False if token_type == "access"
                else RefreshToken.is_revoked == False
            )
            result = await self._session.execute(stmt)
            db_token = result.scalar_one_or_none()
            
            if not db_token or db_token.expires_at < datetime.utcnow():
                return None
            
            # Get user
            stmt = select(User).where(User.id == user_id, User.is_active == True)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none()
            
        except JWTError:
            return None
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke a token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            token_type = payload.get("type")
            
            if token_type not in ["access", "refresh"]:
                return False
            
            # Mark token as revoked
            stmt = select(AccessToken if token_type == "access" else RefreshToken).where(
                AccessToken.token == token if token_type == "access"
                else RefreshToken.token == token
            )
            result = await self._session.execute(stmt)
            db_token = result.scalar_one_or_none()
            
            if db_token:
                db_token.is_revoked = True
                await self._session.commit()
                return True
                
            return False
            
        except JWTError:
            return False


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Dependency for getting current authenticated user."""
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
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency for getting current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency for getting current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user
