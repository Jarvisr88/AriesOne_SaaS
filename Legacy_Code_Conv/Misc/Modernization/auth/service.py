"""
Authentication service implementation.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import (
    User,
    UserInDB,
    TokenData,
    Role,
    RolePermissions
)


# Security configuration
SECRET_KEY = "your-secret-key"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:
    """Service for authentication and authorization."""

    def __init__(self, db: Session):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Verify password.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        return pwd_context.verify(
            plain_password,
            hashed_password
        )

    def get_password_hash(
        self,
        password: str
    ) -> str:
        """Hash password.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    async def get_user(
        self,
        username: str
    ) -> Optional[UserInDB]:
        """Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        # TODO: Implement database query
        pass

    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User if authenticated
            
        Raises:
            HTTPException: If authentication fails
        """
        user = await self.get_user(username)
        if not user:
            return None
            
        if not self.verify_password(
            password,
            user.hashed_password
        ):
            return None
            
        return User(**user.dict())

    def create_access_token(
        self,
        username: str,
        role: Role,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token.
        
        Args:
            username: Username
            role: User role
            expires_delta: Token expiration
            
        Returns:
            JWT token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
        # Get permissions for role
        permissions = RolePermissions.MAPPINGS[role]
        
        # Create token data
        token_data = {
            "sub": username,
            "role": role,
            "permissions": permissions,
            "exp": expire
        }
        
        # Create JWT token
        encoded_jwt = jwt.encode(
            token_data,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        
        return encoded_jwt

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """Get current user from token.
        
        Args:
            token: JWT token
            
        Returns:
            Current user
            
        Raises:
            HTTPException: If token is invalid
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )
            
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
                
            token_data = TokenData(**payload)
            
        except JWTError:
            raise credentials_exception
            
        # Get user
        user = await self.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
            
        return user

    def check_permission(
        self,
        user: User,
        permission: str
    ) -> bool:
        """Check if user has permission.
        
        Args:
            user: User to check
            permission: Required permission
            
        Returns:
            True if user has permission
        """
        return permission in RolePermissions.MAPPINGS[user.role]
