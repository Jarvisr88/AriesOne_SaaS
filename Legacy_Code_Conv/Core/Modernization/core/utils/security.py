"""
Core Security Utility Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides security utilities for the core module.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from cryptography.fernet import Fernet
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import get_settings
from .logging import CoreLogger

settings = get_settings()
logger = CoreLogger(__name__)

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str
    expires_at: datetime


class TokenData(BaseModel):
    """Token data model."""
    user_id: UUID
    scopes: list[str] = []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any],
                       expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
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


async def verify_token(token: str = Security(oauth2_scheme)) -> TokenData:
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        
        scopes = payload.get("scopes", [])
        return TokenData(user_id=UUID(user_id), scopes=scopes)
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )


def check_permission(required_scope: str, token_data: TokenData) -> bool:
    """Check if token has required scope."""
    return required_scope in token_data.scopes


class EncryptionService:
    """Service for handling data encryption/decryption."""
    
    def __init__(self):
        """Initialize encryption service."""
        try:
            # Generate or load encryption key
            self._key = Fernet.generate_key() if not hasattr(settings, 'ENCRYPTION_KEY') \
                else settings.ENCRYPTION_KEY.encode()
            self._fernet = Fernet(self._key)
            logger.info("Encryption service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption service: {str(e)}")
            raise
    
    def encrypt_value(self, value: str) -> str:
        """
        Encrypt a value using Fernet symmetric encryption.
        
        Args:
            value: String value to encrypt
            
        Returns:
            Encrypted value as base64 string
            
        Raises:
            ValueError: If value is empty or None
            Exception: If encryption fails
        """
        try:
            if not value:
                raise ValueError("Cannot encrypt empty value")
                
            encrypted = self._fernet.encrypt(value.encode())
            return encrypted.decode()
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """
        Decrypt a Fernet-encrypted value.
        
        Args:
            encrypted_value: Encrypted value as base64 string
            
        Returns:
            Decrypted string value
            
        Raises:
            ValueError: If encrypted_value is empty or None
            Exception: If decryption fails
        """
        try:
            if not encrypted_value:
                raise ValueError("Cannot decrypt empty value")
                
            decrypted = self._fernet.decrypt(encrypted_value.encode())
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def rotate_key(self) -> None:
        """
        Rotate encryption key.
        
        This should be called periodically for security purposes.
        All data encrypted with the old key must be re-encrypted
        with the new key before the old key is discarded.
        """
        try:
            new_key = Fernet.generate_key()
            self._key = new_key
            self._fernet = Fernet(new_key)
            logger.info("Encryption key rotated successfully")
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise
