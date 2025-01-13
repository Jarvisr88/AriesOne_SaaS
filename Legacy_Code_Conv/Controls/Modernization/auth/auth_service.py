from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Security configuration
SECRET_KEY = "your-secret-key-stored-in-env"  # Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    permissions: list[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    permissions: list[str] = []

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    def __init__(self):
        self.pwd_context = pwd_context

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = self.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def get_user(self, username: str) -> Optional[UserInDB]:
        # Implement user retrieval from database
        # This is a placeholder - replace with actual database query
        pass

# Initialize global auth service
auth_service = AuthService()
