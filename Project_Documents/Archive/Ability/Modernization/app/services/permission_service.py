from typing import List, Optional, Dict, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException
import json

from app.models.access_control import (
    Permission,
    Role,
    Group,
    AccessControlList,
    AuditLog,
    ResourceType,
    SecurityPolicy
)
from app.models.user import User
from app.core.security import get_password_hash
from app.services.audit_service import AuditService

class PermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def create_permission(
        self,
        name: str,
        resource_type: ResourceType,
        action: str,
        company_id: int,
        description: Optional[str] = None,
        conditions: Optional[Dict] = None
    ) -> Permission:
        """Create a new permission"""
        permission = Permission(
            name=name,
            resource_type=resource_type,
            action=action,
            description=description,
            conditions=conditions,
            company_id=company_id
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_permission(
        self,
        permission_id: int,
        company_id: int
    ) -> Optional[Permission]:
        """Get permission by ID"""
        return self.db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.company_id == company_id
        ).first()

    def list_permissions(
        self,
        company_id: int,
        resource_type: Optional[ResourceType] = None,
        action: Optional[str] = None
    ) -> List[Permission]:
        """List permissions with optional filters"""
        query = self.db.query(Permission).filter(
            Permission.company_id == company_id
        )
        
        if resource_type:
            query = query.filter(Permission.resource_type == resource_type)
        if action:
            query = query.filter(Permission.action == action)
            
        return query.all()

    def create_role(
        self,
        name: str,
        company_id: int,
        description: Optional[str] = None,
        is_system_role: bool = False,
        parent_role_id: Optional[int] = None,
        permission_ids: Optional[List[int]] = None
    ) -> Role:
        """Create a new role"""
        # Check if role name exists
        existing = self.db.query(Role).filter(
            Role.name == name,
            Role.company_id == company_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Role with this name already exists"
            )

        role = Role(
            name=name,
            description=description,
            is_system_role=is_system_role,
            parent_role_id=parent_role_id,
            company_id=company_id
        )
        self.db.add(role)

        if permission_ids:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(permission_ids),
                Permission.company_id == company_id
            ).all()
            role.permissions = permissions

        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role(
        self,
        role_id: int,
        company_id: int
    ) -> Optional[Role]:
        """Get role by ID"""
        return self.db.query(Role).filter(
            Role.id == role_id,
            Role.company_id == company_id
        ).first()

    def list_roles(
        self,
        company_id: int,
        include_system_roles: bool = True
    ) -> List[Role]:
        """List roles"""
        query = self.db.query(Role).filter(Role.company_id == company_id)
        if not include_system_roles:
            query = query.filter(Role.is_system_role == False)
        return query.all()

    def update_role(
        self,
        role_id: int,
        company_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_ids: Optional[List[int]] = None
    ) -> Optional[Role]:
        """Update role"""
        role = self.get_role(role_id, company_id)
        if not role:
            return None

        if role.is_system_role:
            raise HTTPException(
                status_code=400,
                detail="Cannot modify system role"
            )

        if name:
            existing = self.db.query(Role).filter(
                Role.name == name,
                Role.company_id == company_id,
                Role.id != role_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Role with this name already exists"
                )
            role.name = name

        if description is not None:
            role.description = description

        if permission_ids is not None:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(permission_ids),
                Permission.company_id == company_id
            ).all()
            role.permissions = permissions

        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(
        self,
        role_id: int,
        company_id: int
    ) -> bool:
        """Delete role"""
        role = self.get_role(role_id, company_id)
        if not role:
            return False

        if role.is_system_role:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete system role"
            )

        self.db.delete(role)
        self.db.commit()
        return True

    def assign_role_to_user(
        self,
        user_id: int,
        role_id: int,
        company_id: int
    ) -> bool:
        """Assign role to user"""
        user = self.db.query(User).filter(
            User.id == user_id,
            User.company_id == company_id
        ).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        role = self.get_role(role_id, company_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail="Role not found"
            )

        if role not in user.roles:
            user.roles.append(role)
            self.db.commit()
        return True

    def remove_role_from_user(
        self,
        user_id: int,
        role_id: int,
        company_id: int
    ) -> bool:
        """Remove role from user"""
        user = self.db.query(User).filter(
            User.id == user_id,
            User.company_id == company_id
        ).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        role = self.get_role(role_id, company_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail="Role not found"
            )

        if role in user.roles:
            user.roles.remove(role)
            self.db.commit()
        return True

    def get_user_permissions(
        self,
        user_id: int,
        company_id: int,
        resource_type: Optional[ResourceType] = None
    ) -> Set[str]:
        """Get all permissions for a user"""
        user = self.db.query(User).filter(
            User.id == user_id,
            User.company_id == company_id
        ).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        permissions = set()

        # Get permissions from user roles
        for role in user.roles:
            for permission in role.permissions:
                if not resource_type or permission.resource_type == resource_type:
                    permissions.add(permission.name)

        # Get permissions from user groups
        for group in user.groups:
            for role in group.roles:
                for permission in role.permissions:
                    if not resource_type or permission.resource_type == resource_type:
                        permissions.add(permission.name)

        return permissions

    def check_permission(
        self,
        user_id: int,
        permission_name: str,
        resource_type: ResourceType,
        resource_id: Optional[int] = None,
        company_id: int = None
    ) -> bool:
        """Check if user has specific permission"""
        # Get user's permissions
        user_permissions = self.get_user_permissions(
            user_id,
            company_id,
            resource_type
        )
        
        if permission_name not in user_permissions:
            return False

        # If resource_id is provided, check ACL
        if resource_id:
            acl = self.db.query(AccessControlList).filter(
                AccessControlList.resource_type == resource_type,
                AccessControlList.resource_id == resource_id,
                AccessControlList.company_id == company_id,
                or_(
                    and_(
                        AccessControlList.principal_type == "user",
                        AccessControlList.principal_id == user_id
                    ),
                    and_(
                        AccessControlList.principal_type == "group",
                        AccessControlList.principal_id.in_(
                            group.id for group in user.groups
                        )
                    ),
                    and_(
                        AccessControlList.principal_type == "role",
                        AccessControlList.principal_id.in_(
                            role.id for role in user.roles
                        )
                    )
                )
            ).first()

            if acl and permission_name not in acl.permissions:
                return False

        return True

    def create_acl(
        self,
        resource_type: ResourceType,
        resource_id: int,
        principal_type: str,
        principal_id: int,
        permissions: List[str],
        company_id: int,
        conditions: Optional[Dict] = None
    ) -> AccessControlList:
        """Create access control list entry"""
        acl = AccessControlList(
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=principal_type,
            principal_id=principal_id,
            permissions=permissions,
            conditions=conditions,
            company_id=company_id
        )
        self.db.add(acl)
        self.db.commit()
        self.db.refresh(acl)
        return acl

    def update_acl(
        self,
        acl_id: int,
        permissions: List[str],
        company_id: int,
        conditions: Optional[Dict] = None
    ) -> Optional[AccessControlList]:
        """Update access control list entry"""
        acl = self.db.query(AccessControlList).filter(
            AccessControlList.id == acl_id,
            AccessControlList.company_id == company_id
        ).first()
        
        if not acl:
            return None

        acl.permissions = permissions
        if conditions is not None:
            acl.conditions = conditions

        self.db.commit()
        self.db.refresh(acl)
        return acl

    def delete_acl(
        self,
        acl_id: int,
        company_id: int
    ) -> bool:
        """Delete access control list entry"""
        acl = self.db.query(AccessControlList).filter(
            AccessControlList.id == acl_id,
            AccessControlList.company_id == company_id
        ).first()
        
        if not acl:
            return False

        self.db.delete(acl)
        self.db.commit()
        return True
