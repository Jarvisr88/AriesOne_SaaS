"""
User repository implementation for managing user-related operations.
"""
from typing import List, Optional
from sqlalchemy import select
from ..core.database import Database, Repository
from .models import User, Role, UserRole

class UserRepository(Repository):
    """Repository for user management operations."""
    
    def __init__(self, db: Database):
        super().__init__(db, User)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        async with self.db.session() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        async with self.db.session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get roles for a user."""
        async with self.db.session() as session:
            result = await session.execute(
                select(Role)
                .join(UserRole)
                .where(UserRole.user_id == user_id)
            )
            return result.scalars().all()

    async def add_role(self, user_id: int, role_id: int, created_by: str) -> None:
        """Add a role to a user."""
        async with self.db.session() as session:
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                created_by=created_by,
                updated_by=created_by
            )
            session.add(user_role)
            await session.commit()

    async def remove_role(self, user_id: int, role_id: int) -> None:
        """Remove a role from a user."""
        async with self.db.session() as session:
            await session.execute(
                UserRole.__table__.delete().where(
                    (UserRole.user_id == user_id) & 
                    (UserRole.role_id == role_id)
                )
            )
            await session.commit()

    async def deactivate(self, user_id: int, updated_by: str) -> None:
        """Deactivate a user."""
        await self.update(user_id, is_active=False, updated_by=updated_by)

    async def activate(self, user_id: int, updated_by: str) -> None:
        """Activate a user."""
        await self.update(user_id, is_active=True, updated_by=updated_by)
