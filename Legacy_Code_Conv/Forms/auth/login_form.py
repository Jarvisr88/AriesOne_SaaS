"""
Login form module using FastAPI and Pydantic for modern form handling.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from fastapi import Form, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import re
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from ...core.database import Database
from ...repositories.user_repository import UserRepository

# Security configuration
SECRET_KEY = "your-secret-key-stored-in-env"  # Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    company_id: Optional[int] = None

class LoginForm(BaseModel):
    """Login form model with validation."""
    username: str
    password: str
    remember_me: bool = False

    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username format."""
        if not re.match("^[a-zA-Z0-9_-]+$", v):
            raise ValueError('Username must be alphanumeric')
        return v

    @validator('password')
    def password_min_length(cls, v):
        """Validate password length."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
        remember_me: bool = Form(False)
    ):
        """Convert form data to model."""
        return cls(
            username=username,
            password=password,
            remember_me=remember_me
        )

class LoginManager:
    """Handle login authentication and token management."""
    
    def __init__(self, database: Database):
        self.database = database
        self.user_repository = UserRepository(database)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    async def authenticate_user(self, username: str, password: str):
        """Authenticate user credentials."""
        user = await self.user_repository.get_by_username(username)
        if not user:
            return False
        if not self.verify_password(password, user.password_hash):
            return False
        return user

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
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def login(self, form_data: LoginForm) -> Token:
        """Process login and return token."""
        user = await self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login
        await self.user_repository.update_last_login(user.id)

        # Create access token
        expires_delta = (
            timedelta(days=7) if form_data.remember_me
            else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        access_token = self.create_access_token(
            data={
                "sub": user.username,
                "company_id": user.company_id
            },
            expires_delta=expires_delta
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds())
        )

    async def get_current_user(self, token: str):
        """Get current user from token."""
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(
                username=username,
                company_id=payload.get("company_id")
            )
        except JWTError:
            raise credentials_exception
            
        user = await self.user_repository.get_by_username(token_data.username)
        if user is None:
            raise credentials_exception
            
        return user

    async def check_active_user(self, token: str):
        """Check if user is active."""
        user = await self.get_current_user(token)
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user
