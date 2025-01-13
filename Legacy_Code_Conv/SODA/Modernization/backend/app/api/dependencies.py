"""API dependencies for FastAPI."""

from typing import Optional, Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..core.database.database import DatabaseService
from ..core.cache import CacheService
from ..core.metrics import MetricsService
from ..services.user_service import UserService
from ..services.organization_service import OrganizationService
from ..services.dmerc_service import DMERCService
from ..repositories.user_repository import UserRepository
from ..repositories.organization_repository import OrganizationRepository
from ..repositories.dmerc_repository import DMERCRepository
from ..domain.models.user import User, UserRole, UserStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Service instances
db = DatabaseService()
cache = CacheService()
metrics = MetricsService()

# Repository instances
user_repository = UserRepository(db, cache, metrics)
organization_repository = OrganizationRepository(db, cache, metrics)
dmerc_repository = DMERCRepository(db, cache, metrics)

# Service instances
user_service = UserService(user_repository, metrics)
organization_service = OrganizationService(organization_repository, metrics)
dmerc_service = DMERCService(dmerc_repository, metrics)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Get current authenticated user."""
    try:
        # TODO: Implement proper JWT token validation
        # For now, assume token is user_id
        user = await user_service.get_by_id(UUID(token))
        if not user or user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user."""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Get current admin user."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def get_user_service() -> UserService:
    """Get user service instance."""
    return user_service

def get_organization_service() -> OrganizationService:
    """Get organization service instance."""
    return organization_service

def get_dmerc_service() -> DMERCService:
    """Get DMERC service instance."""
    return dmerc_service
