"""
Authentication service for the Core module.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy import and_

from ..services.base_service import BaseService
from .models import (
    User, Role, Permission, Token,
    UserCreate, UserUpdate, RoleCreate, PermissionCreate
)

# Security configuration
SECRET_KEY = "your-secret-key"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService(BaseService):
    """Service for handling authentication and authorization."""

    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user and return user object if valid."""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(
        self,
        user_create: UserCreate
    ) -> User:
        """Create a new user."""
        # Check if username or email already exists
        if await self.get_user_by_username(user_create.username):
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
        
        if await self.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Create user
        hashed_password = self.get_password_hash(user_create.password)
        user_dict = user_create.dict()
        user_dict.pop("password")
        user_dict["hashed_password"] = hashed_password

        user = User(**user_dict)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def create_access_token(
        self,
        user: User,
        device_info: Optional[str] = None
    ) -> str:
        """Create access token for user."""
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_at = datetime.utcnow() + expires_delta

        # Create token data
        token_data = {
            "sub": user.username,
            "exp": expires_at,
            "roles": [role.name for role in user.roles],
            "permissions": await self.get_user_permissions(user.id)
        }

        # Create JWT token
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        # Store token in database
        db_token = Token(
            user_id=user.id,
            token=token,
            token_type="bearer",
            expires_at=expires_at,
            device_info=device_info
        )
        self.db.add(db_token)
        await self.db.commit()

        return token

    async def verify_token(self, token: str) -> Optional[User]:
        """Verify token and return user if valid."""
        try:
            # Verify JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if not username:
                return None

            # Check if token is revoked
            db_token = await self.get_token(token)
            if not db_token or db_token.is_revoked:
                return None

            # Get user
            user = await self.get_user_by_username(username)
            if not user or not user.is_active:
                return None

            return user

        except JWTError:
            return None

    async def create_role(
        self,
        role_create: RoleCreate
    ) -> Role:
        """Create a new role."""
        # Check if role already exists
        if await self.get_role_by_name(role_create.name):
            raise HTTPException(
                status_code=400,
                detail=f"Role '{role_create.name}' already exists"
            )

        # Create role
        role = Role(**role_create.dict(exclude={"permissions"}))
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)

        # Add permissions
        if role_create.permissions:
            await self.update_role_permissions(role.id, role_create.permissions)

        return role

    async def create_permission(
        self,
        permission_create: PermissionCreate
    ) -> Permission:
        """Create a new permission."""
        # Check if permission already exists
        if await self.get_permission_by_name(permission_create.name):
            raise HTTPException(
                status_code=400,
                detail=f"Permission '{permission_create.name}' already exists"
            )

        permission = Permission(**permission_create.dict())
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)

        return permission

    async def get_user_permissions(
        self,
        user_id: int
    ) -> List[str]:
        """Get all permissions for a user."""
        user = await self.get(User, user_id)
        if not user:
            return []

        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.name)

        return list(permissions)

    async def check_permission(
        self,
        user: User,
        required_permission: str
    ) -> bool:
        """Check if user has required permission."""
        if user.is_superuser:
            return True

        user_permissions = await self.get_user_permissions(user.id)
        return required_permission in user_permissions

    # Helper methods

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Get password hash."""
        return pwd_context.hash(password)

    async def get_user_by_username(
        self,
        username: str
    ) -> Optional[User]:
        """Get user by username."""
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        email: str
    ) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_role_by_name(
        self,
        name: str
    ) -> Optional[Role]:
        """Get role by name."""
        query = select(Role).where(Role.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_permission_by_name(
        self,
        name: str
    ) -> Optional[Permission]:
        """Get permission by name."""
        query = select(Permission).where(Permission.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_token(
        self,
        token: str
    ) -> Optional[Token]:
        """Get token from database."""
        query = select(Token).where(
            and_(
                Token.token == token,
                Token.expires_at > datetime.utcnow()
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_role_permissions(
        self,
        role_id: int,
        permission_names: List[str]
    ) -> None:
        """Update role permissions."""
        role = await self.get(Role, role_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail=f"Role {role_id} not found"
            )

        # Get permission objects
        permissions = []
        for name in permission_names:
            permission = await self.get_permission_by_name(name)
            if not permission:
                raise HTTPException(
                    status_code=400,
                    detail=f"Permission '{name}' not found"
                )
            permissions.append(permission)

        # Update role permissions
        role.permissions = permissions
        await self.db.commit()
