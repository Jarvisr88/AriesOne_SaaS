"""Authentication security module.

This module handles password hashing, JWT token management, and security utilities.
"""
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from core.config import get_settings


settings = get_settings()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class Token(BaseModel):
    """Token model for JWT authentication."""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token data model for JWT claims."""
    username: str
    scopes: list[str] = []
    exp: datetime


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        TokenData: Decoded token data
        
    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        scopes: list[str] = payload.get("scopes", [])
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))
        
        if username is None:
            raise JWTError("Username not found in token")
        
        return TokenData(
            username=username,
            scopes=scopes,
            exp=exp
        )
    except JWTError as e:
        raise JWTError(f"Could not validate token: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password using Argon2.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_token_response(
    username: str,
    scopes: list[str],
    expires_delta: Optional[timedelta] = None
) -> Token:
    """Create token response with access token.
    
    Args:
        username: Username to encode in token
        scopes: Permission scopes to encode
        expires_delta: Optional expiration time
        
    Returns:
        Token: Token response with access token
    """
    if expires_delta:
        expire = expires_delta
    else:
        expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token = create_access_token(
        data={
            "sub": username,
            "scopes": scopes
        },
        expires_delta=expire
    )
    
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=int(expire.total_seconds())
    )
