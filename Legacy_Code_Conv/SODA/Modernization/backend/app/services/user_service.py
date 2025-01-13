"""User service for business logic operations."""

from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from passlib.context import CryptContext

from ..core.metrics import MetricsService
from ..repositories.user_repository import UserRepository
from ..domain.models.user import User, UserStatus, UserRole
from .base_service import BaseService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService(BaseService[User]):
    """Service for user operations."""

    def __init__(
        self,
        repository: UserRepository,
        metrics: Optional[MetricsService] = None
    ):
        """Initialize user service."""
        super().__init__(repository, metrics)
        self.repository: UserRepository = repository

    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate user data."""
        required_fields = ["email", "username"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        # Validate email format
        if not "@" in data["email"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        # Validate username length
        if len(data["username"]) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long"
            )

    async def create_user(
        self,
        data: Dict[str, Any],
        *,
        verify_email: bool = True
    ) -> User:
        """Create new user."""
        self.validate_data(data)

        # Check if email or username already exists
        existing_email = await self.repository.find_by_email(data["email"])
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        existing_username = await self.repository.find_by_username(data["username"])
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Hash password if provided
        if "password" in data:
            data["password_hash"] = pwd_context.hash(data["password"])
            del data["password"]

        # Set default values
        data.setdefault("role", UserRole.USER)
        data.setdefault("status", UserStatus.PENDING if verify_email else UserStatus.ACTIVE)

        return await self.create(data)

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.repository.find_by_email(email)
        if not user or not user.password_hash:
            return None

        if not pwd_context.verify(password, user.password_hash):
            if self.metrics:
                self.metrics.increment("user.auth.failed")
            return None

        # Update last login
        await self.repository.update_last_login(user.id)
        if self.metrics:
            self.metrics.increment("user.auth.success")

        return user

    async def verify_email(
        self,
        user_id: UUID,
        token: str
    ) -> bool:
        """Verify user's email."""
        user = await self.get_by_id(user_id)
        if not user or user.is_verified:
            return False

        # TODO: Implement token verification logic
        # For now, just mark as verified
        await self.repository.verify_email(user_id)
        if self.metrics:
            self.metrics.increment("user.email.verified")

        return True

    async def update_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """Update user's password."""
        user = await self.get_by_id(user_id)
        if not user or not user.password_hash:
            return False

        # Verify current password
        if not pwd_context.verify(current_password, user.password_hash):
            if self.metrics:
                self.metrics.increment("user.password.update.failed")
            return False

        # Update password
        await self.update(
            user_id,
            {"password_hash": pwd_context.hash(new_password)}
        )
        if self.metrics:
            self.metrics.increment("user.password.updated")

        return True

    async def reset_password(
        self,
        email: str
    ) -> bool:
        """Initiate password reset process."""
        user = await self.repository.find_by_email(email)
        if not user:
            return False

        # TODO: Implement password reset token generation and email sending
        # For now, just log the request
        self.logger.info(f"Password reset requested for user: {user.id}")
        if self.metrics:
            self.metrics.increment("user.password.reset.requested")

        return True

    async def update_role(
        self,
        user_id: UUID,
        role: UserRole,
        updated_by_id: UUID
    ) -> User:
        """Update user's role."""
        # Verify that the updating user has admin privileges
        updating_user = await self.get_by_id(updated_by_id)
        if updating_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update user roles"
            )

        updated = await self.repository.update_role(user_id, role)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if self.metrics:
            self.metrics.increment(f"user.role.updated.{role.value}")

        return updated

    async def update_status(
        self,
        user_id: UUID,
        status: UserStatus,
        updated_by_id: UUID
    ) -> User:
        """Update user's status."""
        # Verify that the updating user has admin privileges
        updating_user = await self.get_by_id(updated_by_id)
        if updating_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update user status"
            )

        updated = await self.repository.update_status(user_id, status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if self.metrics:
            self.metrics.increment(f"user.status.updated.{status.value}")

        return updated

    async def update_preferences(
        self,
        user_id: UUID,
        preferences: Dict[str, Any]
    ) -> User:
        """Update user's preferences."""
        updated = await self.repository.update_preferences(user_id, preferences)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if self.metrics:
            self.metrics.increment("user.preferences.updated")

        return updated

    async def search_users(
        self,
        search_term: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name or email."""
        return await self.repository.search_users(
            search_term,
            offset=offset,
            limit=limit
        )
