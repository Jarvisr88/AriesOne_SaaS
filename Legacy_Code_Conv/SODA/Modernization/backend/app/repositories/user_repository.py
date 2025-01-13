"""User repository for database operations."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.sql import Select

from ..core.database.base_repository import BaseRepository
from ..core.database.database import DatabaseService
from ..core.cache import CacheService
from ..core.metrics import MetricsService
from ..domain.models.user import User, UserStatus, UserRole

class UserRepository(BaseRepository[User]):
    """Repository for user operations."""

    def __init__(
        self,
        db: DatabaseService,
        cache: Optional[CacheService] = None,
        metrics: Optional[MetricsService] = None
    ):
        """Initialize user repository."""
        super().__init__(db, User, cache, metrics)
        self.cache_ttl = 3600  # 1 hour for users

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        return await self.find_one(User.email == email)

    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        return await self.find_one(User.username == username)

    async def find_active_users(
        self,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Find all active users."""
        return await self.find_many(
            User.status == UserStatus.ACTIVE,
            offset=offset,
            limit=limit
        )

    async def find_users_by_role(
        self,
        role: UserRole,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Find users by role."""
        return await self.find_many(
            User.role == role,
            offset=offset,
            limit=limit
        )

    async def find_users_by_organization(
        self,
        organization_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Find users by organization."""
        query = (
            select(User)
            .join(User.organizations)
            .where(User.organizations.any(organization_id=organization_id))
            .offset(offset)
            .limit(limit)
        )
        
        async with self.db.session() as session:
            result = await session.execute(query)
            return list(result.scalars().all())

    async def search_users(
        self,
        search_term: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name or email."""
        search_pattern = f"%{search_term}%"
        return await self.find_many(
            or_(
                User.email.ilike(search_pattern),
                User.username.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern)
            ),
            offset=offset,
            limit=limit
        )

    async def update_last_login(self, user_id: UUID) -> Optional[User]:
        """Update user's last login time."""
        user = await self.get_by_id(user_id)
        if user:
            user.update_last_login()
            return await self.update(user_id, {"last_login": user.last_login})
        return None

    async def verify_email(self, user_id: UUID) -> Optional[User]:
        """Mark user's email as verified."""
        user = await self.get_by_id(user_id)
        if user:
            user.verify_email()
            return await self.update(
                user_id,
                {
                    "is_verified": user.is_verified,
                    "email_verified_at": user.email_verified_at,
                    "status": user.status
                }
            )
        return None

    async def update_status(
        self,
        user_id: UUID,
        status: UserStatus
    ) -> Optional[User]:
        """Update user's status."""
        return await self.update(user_id, {"status": status})

    async def update_role(
        self,
        user_id: UUID,
        role: UserRole
    ) -> Optional[User]:
        """Update user's role."""
        return await self.update(user_id, {"role": role})

    async def update_preferences(
        self,
        user_id: UUID,
        preferences: Dict[str, Any]
    ) -> Optional[User]:
        """Update user's preferences."""
        user = await self.get_by_id(user_id)
        if user:
            current_prefs = user.preferences or {}
            current_prefs.update(preferences)
            return await self.update(user_id, {"preferences": current_prefs})
        return None
