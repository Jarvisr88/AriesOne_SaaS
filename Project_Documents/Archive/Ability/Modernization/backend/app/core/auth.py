from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_session
from app.models.user import User as UserModel
from app.schemas.token import Token, TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_authorization_code = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.OAUTH2_AUTHORIZATION_URL,
    tokenUrl=settings.OAUTH2_TOKEN_URL,
)

class User(BaseModel):
    id: str
    email: str
    is_active: bool
    is_superuser: bool
    full_name: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
) -> User:
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
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    user = await db.get(UserModel, token_data.user_id)
    if user is None:
        raise credentials_exception
    return User.from_orm(user)

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user

class OAuth2Handler:
    def __init__(self):
        self.oauth2_clients: Dict[str, Dict[str, Any]] = {}

    def register_client(
        self,
        client_id: str,
        client_secret: str,
        redirect_uris: list[str],
        scopes: list[str]
    ) -> None:
        """Register a new OAuth2 client"""
        self.oauth2_clients[client_id] = {
            "client_secret": client_secret,
            "redirect_uris": redirect_uris,
            "scopes": scopes,
        }

    def verify_client(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: str
    ) -> bool:
        """Verify OAuth2 client credentials and scope"""
        client = self.oauth2_clients.get(client_id)
        if not client:
            return False

        if client["client_secret"] != client_secret:
            return False

        if redirect_uri not in client["redirect_uris"]:
            return False

        requested_scopes = scope.split()
        if not all(s in client["scopes"] for s in requested_scopes):
            return False

        return True

    async def create_authorization_code(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        user: User
    ) -> str:
        """Create an authorization code"""
        code_data = {
            "sub": user.id,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
        }
        return create_access_token(code_data, timedelta(minutes=10))

    async def exchange_code_for_token(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> Token:
        """Exchange authorization code for access token"""
        try:
            payload = jwt.decode(
                code,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            if (
                payload["client_id"] != client_id or
                payload["redirect_uri"] != redirect_uri
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid client or redirect URI"
                )

            access_token = create_access_token(
                data={"sub": payload["sub"]},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

            refresh_token = create_access_token(
                data={"sub": payload["sub"]},
                expires_delta=timedelta(days=30)
            )

            return Token(
                access_token=access_token,
                token_type="bearer",
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                scope=payload["scope"]
            )
        except JWTError:
            raise HTTPException(
                status_code=400,
                detail="Invalid authorization code"
            )

oauth2_handler = OAuth2Handler()
