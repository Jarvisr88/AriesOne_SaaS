"""
Authentication and Authorization Module

This module handles all authentication and authorization for the Ability module.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..config import Settings
from ..models.user import User


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    scopes: list[str] = []


class SecurityService:
    """Security service for authentication and authorization."""

    def __init__(self, settings: Settings):
        """Initialize security service."""
        self.settings = settings
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(
            tokenUrl="token",
            scopes={
                "eligibility:read": "Read eligibility information",
                "eligibility:write": "Submit eligibility requests",
                "admin": "Administrative access"
            }
        )
        self.api_key_header = APIKeyHeader(name="X-API-Key")

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.algorithm
        )
        return encoded_jwt

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """Get current user from token."""
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm]
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        
        user = await User.get_by_username(token_data.username)
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Get current active user."""
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    async def validate_api_key(
        self,
        api_key: str = Security(api_key_header)
    ) -> bool:
        """Validate API key."""
        # In production, this should check against a secure store
        return api_key == self.settings.api_key

    def check_permissions(
        self,
        user: User,
        required_permissions: list[str]
    ) -> bool:
        """Check if user has required permissions."""
        return all(
            permission in user.permissions
            for permission in required_permissions
        )
