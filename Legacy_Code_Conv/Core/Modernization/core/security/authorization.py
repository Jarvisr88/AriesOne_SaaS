"""
Core Authorization Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides authorization functionality.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .authentication import get_current_user
from .models import Permission, Role, User


class AuthorizationService:
    """Service for handling authorization."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self._session = session
    
    async def get_user_permissions(self, user: User) -> List[Permission]:
        """Get all permissions for a user."""
        # Get user's roles with permissions
        stmt = (
            select(Role)
            .join(Role.users)
            .where(User.id == user.id)
            .join(Role.permissions)
        )
        result = await self._session.execute(stmt)
        roles = result.unique().scalars().all()
        
        # Collect all unique permissions
        permissions = set()
        for role in roles:
            permissions.update(role.permissions)
            
        return list(permissions)
    
    async def check_permission(self, user: User, resource: str,
                             action: str) -> bool:
        """Check if user has permission for resource and action."""
        permissions = await self.get_user_permissions(user)
        return any(
            p.resource == resource and p.action == action
            for p in permissions
        )
    
    async def assign_role(self, user_id: UUID, role_name: str) -> bool:
        """Assign role to user."""
        # Get user and role
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        
        stmt = select(Role).where(Role.name == role_name)
        result = await self._session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not user or not role:
            return False
        
        # Assign role if not already assigned
        if role not in user.roles:
            user.roles.append(role)
            await self._session.commit()
            
        return True
    
    async def remove_role(self, user_id: UUID, role_name: str) -> bool:
        """Remove role from user."""
        # Get user and role
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        
        stmt = select(Role).where(Role.name == role_name)
        result = await self._session.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not user or not role:
            return False
        
        # Remove role if assigned
        if role in user.roles:
            user.roles.remove(role)
            await self._session.commit()
            
        return True
    
    async def create_role(self, name: str,
                         description: Optional[str] = None) -> Role:
        """Create new role."""
        role = Role(name=name, description=description)
        self._session.add(role)
        await self._session.commit()
        return role
    
    async def create_permission(self, name: str, resource: str,
                              action: str, description: Optional[str] = None) -> Permission:
        """Create new permission."""
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description
        )
        self._session.add(permission)
        await self._session.commit()
        return permission
    
    async def assign_permission_to_role(self, role_name: str,
                                      permission_name: str) -> bool:
        """Assign permission to role."""
        # Get role and permission
        stmt = select(Role).where(Role.name == role_name)
        result = await self._session.execute(stmt)
        role = result.scalar_one_or_none()
        
        stmt = select(Permission).where(Permission.name == permission_name)
        result = await self._session.execute(stmt)
        permission = result.scalar_one_or_none()
        
        if not role or not permission:
            return False
        
        # Assign permission if not already assigned
        if permission not in role.permissions:
            role.permissions.append(permission)
            await self._session.commit()
            
        return True


def require_permission(resource: str, action: str):
    """Decorator for requiring permission."""
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
    ):
        auth_service = AuthorizationService(session)
        has_permission = await auth_service.check_permission(
            current_user,
            resource,
            action
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions to {action} {resource}"
            )
        
        return current_user
    
    return Depends(permission_dependency)
