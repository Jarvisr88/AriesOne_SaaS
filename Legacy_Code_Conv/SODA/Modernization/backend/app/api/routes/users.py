"""User routes."""

from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import (
    get_user_service,
    get_current_active_user,
    get_admin_user
)
from ..schemas.user import (
    UserCreate,
    UserUpdate,
    UserAdminUpdate,
    UserResponse,
    UserPreferencesUpdate
)
from ...services.user_service import UserService
from ...domain.models.user import User, UserRole, UserStatus

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """Create new user."""
    return await user_service.create_user(user.model_dump())

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Get current user."""
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """Update current user."""
    return await user_service.update(
        current_user.id,
        update.model_dump(exclude_unset=True)
    )

@router.patch("/me/preferences", response_model=UserResponse)
async def update_preferences(
    preferences: UserPreferencesUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """Update user preferences."""
    return await user_service.update_preferences(
        current_user.id,
        preferences.preferences
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """Get user by ID."""
    # Regular users can only view themselves
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    return await user_service.get_by_id(user_id)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    update: UserAdminUpdate,
    current_user: Annotated[User, Depends(get_admin_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """Update user (admin only)."""
    if "role" in update.model_dump(exclude_unset=True):
        return await user_service.update_role(
            user_id,
            update.role,
            current_user.id
        )
    elif "status" in update.model_dump(exclude_unset=True):
        return await user_service.update_status(
            user_id,
            update.status,
            current_user.id
        )
    else:
        return await user_service.update(
            user_id,
            update.model_dump(exclude_unset=True)
        )

@router.get("", response_model=List[UserResponse])
async def search_users(
    search: str = "",
    offset: int = 0,
    limit: int = 100,
    current_user: Annotated[User, Depends(get_admin_user)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> List[User]:
    """Search users (admin only)."""
    return await user_service.search_users(
        search,
        offset=offset,
        limit=limit
    )
