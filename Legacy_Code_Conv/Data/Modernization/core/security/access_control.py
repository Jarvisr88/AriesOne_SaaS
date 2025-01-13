"""Access control module."""
from typing import Any, List, Optional, Protocol, Set
from enum import Enum
from uuid import UUID
from pydantic import BaseModel

class Permission(str, Enum):
    """Permission types."""
    
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class Resource(str, Enum):
    """Resource types."""
    
    COMPANY = "company"
    LOCATION = "location"
    SESSION = "session"
    USER = "user"

class AccessPolicy(BaseModel):
    """Access policy model."""
    
    resource: Resource
    permissions: Set[Permission]
    conditions: Optional[dict] = None

class IAccessControl(Protocol):
    """Access control interface."""

    async def has_permission(
        self,
        user_id: UUID,
        resource: Resource,
        permission: Permission,
        resource_id: Optional[UUID] = None
    ) -> bool:
        """Check if user has permission.
        
        Args:
            user_id: User ID.
            resource: Resource type.
            permission: Permission type.
            resource_id: Optional resource ID.
            
        Returns:
            True if user has permission.
        """
        raise NotImplementedError

    async def get_user_policies(
        self,
        user_id: UUID
    ) -> List[AccessPolicy]:
        """Get user access policies.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of access policies.
        """
        raise NotImplementedError

class AccessControlService(IAccessControl):
    """Access control service implementation."""

    def __init__(self, session_factory):
        """Initialize access control service.
        
        Args:
            session_factory: Database session factory.
        """
        self.session_factory = session_factory

    async def has_permission(
        self,
        user_id: UUID,
        resource: Resource,
        permission: Permission,
        resource_id: Optional[UUID] = None
    ) -> bool:
        """Check if user has permission."""
        policies = await self.get_user_policies(user_id)
        
        for policy in policies:
            if (policy.resource == resource and
                permission in policy.permissions):
                
                if not resource_id:
                    return True
                
                if not policy.conditions:
                    return True
                
                # Check resource-specific conditions
                if await self._check_conditions(
                    user_id,
                    resource,
                    resource_id,
                    policy.conditions
                ):
                    return True
        
        return False

    async def _check_conditions(
        self,
        user_id: UUID,
        resource: Resource,
        resource_id: UUID,
        conditions: dict
    ) -> bool:
        """Check access conditions.
        
        Args:
            user_id: User ID.
            resource: Resource type.
            resource_id: Resource ID.
            conditions: Access conditions.
            
        Returns:
            True if conditions are met.
        """
        async with self.session_factory() as session:
            # Example: Check company membership
            if resource == Resource.COMPANY:
                return await self._check_company_access(
                    session,
                    user_id,
                    resource_id
                )
            
            # Example: Check location access
            if resource == Resource.LOCATION:
                return await self._check_location_access(
                    session,
                    user_id,
                    resource_id
                )
            
            return False

    async def get_user_policies(
        self,
        user_id: UUID
    ) -> List[AccessPolicy]:
        """Get user access policies."""
        async with self.session_factory() as session:
            # Fetch user roles and associated policies
            # This is a simplified example
            return [
                AccessPolicy(
                    resource=Resource.COMPANY,
                    permissions={Permission.READ, Permission.WRITE},
                    conditions={"company_member": True}
                ),
                AccessPolicy(
                    resource=Resource.LOCATION,
                    permissions={Permission.READ},
                    conditions={"company_member": True}
                )
            ]

    async def _check_company_access(
        self,
        session: Any,
        user_id: UUID,
        company_id: UUID
    ) -> bool:
        """Check company access."""
        # Implement company access check logic
        return True

    async def _check_location_access(
        self,
        session: Any,
        user_id: UUID,
        location_id: UUID
    ) -> bool:
        """Check location access."""
        # Implement location access check logic
        return True
