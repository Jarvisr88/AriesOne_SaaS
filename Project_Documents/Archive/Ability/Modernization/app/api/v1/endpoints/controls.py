from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.deps import get_db, get_current_user, get_current_active_user
from app.services.permission_service import PermissionService
from app.services.audit_service import AuditService
from app.services.security_policy_service import SecurityPolicyService
from app.models.access_control import ResourceType
from app.schemas.controls import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    SecurityPolicyCreate,
    SecurityPolicyUpdate,
    SecurityPolicyResponse,
    AuditLogResponse,
    AuditLogFilter
)
from app.models.user import User

router = APIRouter()

# Permission endpoints
@router.post("/permissions/", response_model=PermissionResponse)
async def create_permission(
    *,
    db: Session = Depends(get_db),
    permission_in: PermissionCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new permission"""
    permission_service = PermissionService(db)
    audit_service = AuditService(db)
    
    # Check if user has permission to create permissions
    if not permission_service.check_permission(
        current_user.id,
        "create_permission",
        ResourceType.PERMISSION,
        company_id=current_user.company_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    permission = permission_service.create_permission(
        name=permission_in.name,
        resource_type=permission_in.resource_type,
        action=permission_in.action,
        description=permission_in.description,
        conditions=permission_in.conditions,
        company_id=current_user.company_id
    )
    
    await audit_service.log_action(
        actor_id=current_user.id,
        action="create_permission",
        resource_type=ResourceType.PERMISSION,
        resource_id=permission.id,
        company_id=current_user.company_id,
        new_values=permission_in.dict()
    )
    
    return permission

@router.get("/permissions/", response_model=List[PermissionResponse])
async def list_permissions(
    *,
    db: Session = Depends(get_db),
    resource_type: Optional[ResourceType] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List permissions"""
    permission_service = PermissionService(db)
    
    if not permission_service.check_permission(
        current_user.id,
        "list_permissions",
        ResourceType.PERMISSION,
        company_id=current_user.company_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    permissions = permission_service.list_permissions(
        company_id=current_user.company_id,
        resource_type=resource_type,
        action=action
    )
    return permissions[skip : skip + limit]

# Role endpoints
@router.post("/roles/", response_model=RoleResponse)
async def create_role(
    *,
    db: Session = Depends(get_db),
    role_in: RoleCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new role"""
    permission_service = PermissionService(db)
    audit_service = AuditService(db)
    
    if not permission_service.check_permission(
        current_user.id,
        "create_role",
        ResourceType.ROLE,
        company_id=current_user.company_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    role = permission_service.create_role(
        name=role_in.name,
        description=role_in.description,
        is_system_role=role_in.is_system_role,
        parent_role_id=role_in.parent_role_id,
        permission_ids=role_in.permission_ids,
        company_id=current_user.company_id
    )
    
    await audit_service.log_action(
        actor_id=current_user.id,
        action="create_role",
        resource_type=ResourceType.ROLE,
        resource_id=role.id,
        company_id=current_user.company_id,
        new_values=role_in.dict()
    )
    
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    role_in: RoleUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update role"""
    permission_service = PermissionService(db)
    audit_service = AuditService(db)
    
    if not permission_service.check_permission(
        current_user.id,
        "update_role",
        ResourceType.ROLE,
        resource_id=role_id,
        company_id=current_user.company_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    role = permission_service.get_role(role_id, current_user.company_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )
    
    old_values = {
        "name": role.name,
        "description": role.description,
        "permission_ids": [p.id for p in role.permissions]
    }
    
    role = permission_service.update_role(
        role_id=role_id,
        company_id=current_user.company_id,
        name=role_in.name,
        description=role_in.description,
        permission_ids=role_in.permission_ids
    )
    
    await audit_service.log_action(
        actor_id=current_user.id,
        action="update_role",
        resource_type=ResourceType.ROLE,
        resource_id=role_id,
        company_id=current_user.company_id,
        old_values=old_values,
        new_values=role_in.dict()
    )
    
    return role

# Security Policy endpoints
@router.post("/security-policies/", response_model=SecurityPolicyResponse)
async def create_security_policy(
    *,
    db: Session = Depends(get_db),
    policy_in: SecurityPolicyCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new security policy"""
    permission_service = PermissionService(db)
    security_policy_service = SecurityPolicyService(db)
    audit_service = AuditService(db)
    
    if not permission_service.check_permission(
        current_user.id,
        "create_security_policy",
        ResourceType.SETTING,
        company_id=current_user.company_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    policy = security_policy_service.create_policy(
        name=policy_in.name,
        policy_type=policy_in.policy_type,
        settings=policy_in.settings,
        description=policy_in.description,
        is_enabled=policy_in.is_enabled,
        priority=policy_in.priority,
        company_id=current_user.company_id
    )
    
    await audit_service.log_action(
        actor_id=current_user.id,
        action="create_security_policy",
        resource_type=ResourceType.SETTING,
        resource_id=policy.id,
        company_id=current_user.company_id,
        new_values=policy_in.dict()
    )
    
    return policy

@router.get("/audit-logs/", response_model=List[AuditLogResponse])
async def list_audit_logs(
    *,
    db: Session = Depends(get_db),
    filter_params: AuditLogFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List audit logs with filtering"""
    permission_service = PermissionService(db)
    audit_service = AuditService(db)
    
    if not permission_service.check_permission(
        current_user.id,
        "view_audit_logs",
        ResourceType.SETTING,
        company_id=current_user.company_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    logs = audit_service.list_audit_logs(
        company_id=current_user.company_id,
        resource_type=filter_params.resource_type,
        resource_id=filter_params.resource_id,
        actor_id=filter_params.actor_id,
        action=filter_params.action,
        status=filter_params.status,
        start_time=filter_params.start_time,
        end_time=filter_params.end_time,
        skip=skip,
        limit=limit
    )
    return logs

@router.get("/audit-logs/summary", response_model=Dict[str, Any])
async def get_audit_summary(
    *,
    db: Session = Depends(get_db),
    resource_type: Optional[ResourceType] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get audit logs summary"""
    permission_service = PermissionService(db)
    audit_service = AuditService(db)
    
    if not permission_service.check_permission(
        current_user.id,
        "view_audit_logs",
        ResourceType.SETTING,
        company_id=current_user.company_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    summary = audit_service.get_audit_summary(
        company_id=current_user.company_id,
        resource_type=resource_type,
        start_time=start_time,
        end_time=end_time
    )
    return summary
