"""Security services module."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.database import get_db
from .models import User, Role, AccessToken, AuditLog, TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class SecurityService:
    """Service for handling security operations."""
    
    def __init__(self, db: Session):
        """Initialize security service."""
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Get password hash."""
        return pwd_context.hash(password)
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        # Store token in database
        token = AccessToken(
            user_id=data.get("sub"),
            token=encoded_jwt,
            expires_at=expire
        )
        self.db.add(token)
        self.db.commit()
        
        return encoded_jwt
    
    def get_current_user(
        self,
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """Get current user from token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
        
        user = self.get_user_by_email(email=token_data.email)
        if user is None:
            raise credentials_exception
        return user
    
    def get_current_active_user(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Get current active user."""
        if not current_user.is_active:
            raise HTTPException(
                status_code=400,
                detail="Inactive user"
            )
        return current_user
    
    def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        is_superuser: bool = False
    ) -> User:
        """Create new user."""
        hashed_password = self.get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ) -> Role:
        """Create new role."""
        role = Role(
            name=name,
            description=description,
            permissions=permissions
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def assign_role_to_user(self, user_id: int, role_id: int) -> None:
        """Assign role to user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            raise ValueError("User or role not found")
        
        user.roles.append(role)
        self.db.commit()
    
    def log_audit(
        self,
        user_id: int,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Create audit log entry."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def revoke_token(self, token: str) -> None:
        """Revoke access token."""
        db_token = self.db.query(AccessToken).filter(
            AccessToken.token == token
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            self.db.commit()
