"""Security utilities module."""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.auth import RefreshToken

def create_access_token(
    data: Dict[str, Any],
    secret_key: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    return jwt.encode(to_encode, secret_key, algorithm="HS256")

def create_refresh_token() -> str:
    """Create refresh token."""
    return os.urandom(32).hex()

def verify_refresh_token(db: Session, token: str) -> RefreshToken:
    """Verify refresh token and return token object."""
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == token)
        .filter(RefreshToken.revoked == False)
        .filter(RefreshToken.expires_at > datetime.utcnow())
        .first()
    )
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return db_token

def verify_access_token(token: str, secret_key: str) -> Dict[str, Any]:
    """Verify JWT access token and return payload."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token"
        )

def has_permission(user_roles: list, required_permission: str) -> bool:
    """Check if user has required permission."""
    # Admin role has all permissions
    if "admin" in user_roles:
        return True
    
    # Check specific permissions
    for role in user_roles:
        if role == required_permission:
            return True
    
    return False
