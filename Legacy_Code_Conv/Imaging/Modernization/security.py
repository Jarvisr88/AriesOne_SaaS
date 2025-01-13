"""
Security module for the imaging service.

Handles authentication, authorization, and security policies.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import JWTError
import logging
from .config import settings


class SecurityManager:
    """Manages security operations."""
    
    def __init__(self):
        """Initialize security manager."""
        self.logger = logging.getLogger(__name__)
        self.security = HTTPBearer()

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token.
        
        Args:
            data: Token payload
            expires_delta: Optional expiration override
            
        Returns:
            JWT token string
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
            "iat": datetime.utcnow()
        })
        
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def decode_token(
        self,
        token: str
    ) -> Dict[str, Any]:
        """Decode and validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token type"
                )
                
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ) -> Dict[str, Any]:
        """Get current user from token.
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            User details from token
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            payload = self.decode_token(credentials.credentials)
            
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token subject"
                )
                
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )

    def verify_company_access(
        self,
        token_data: Dict[str, Any],
        company_id: int
    ) -> bool:
        """Verify user has access to company.
        
        Args:
            token_data: Decoded token data
            company_id: Company to check access for
            
        Returns:
            True if access is allowed
            
        Raises:
            HTTPException: If access is denied
        """
        # Super admin can access all companies
        if token_data.get("is_superadmin"):
            return True
            
        # Check if user belongs to company
        user_company = token_data.get("company_id")
        if not user_company or user_company != company_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied for this company"
            )
            
        return True

    def generate_secure_filename(
        self,
        original_filename: str,
        company_id: int
    ) -> str:
        """Generate secure filename for storage.
        
        Args:
            original_filename: Original file name
            company_id: Company identifier
            
        Returns:
            Secure filename
        """
        import uuid
        import os
        
        # Get file extension
        _, ext = os.path.splitext(original_filename)
        if not ext:
            ext = '.jpg'  # Default to jpg
        
        # Generate UUID
        filename = f"{uuid.uuid4()}{ext.lower()}"
        
        # Add company prefix
        return f"{company_id}/{filename}"

    def validate_file_type(
        self,
        content_type: str,
        filename: str
    ) -> bool:
        """Validate file type is allowed.
        
        Args:
            content_type: File content type
            filename: Original filename
            
        Returns:
            True if file type is allowed
            
        Raises:
            HTTPException: If file type is not allowed
        """
        # Check content type
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
            
        # Check extension
        ext = filename.split('.')[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File extension .{ext} not allowed"
            )
            
        return True
