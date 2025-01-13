from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from datetime import datetime, timezone
import json

from app.models.core import User, Tenant, Company, CoreAuditLog, AuditLogType
from app.models.controls import Permission, Role, SecurityPolicy
from app.core.cache import RedisCache
from app.core.config import settings

class AuthorizationService:
    def __init__(self, db: Session, cache: RedisCache):
        self.db = db
        self.cache = cache

    async def check_permission(
        self,
        user_id: int,
        resource_type: str,
        action: str,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if user has permission to perform action on resource"""
        cache_key = f"user_perms:{user_id}"
        
        # Try to get permissions from cache
        cached_perms = await self.cache.get(cache_key)
        if cached_perms:
            permissions = json.loads(cached_perms)
        else:
            # Get user's roles and permissions from database
            permissions = await self._load_user_permissions(user_id)
            # Cache permissions
            await self.cache.set(
                cache_key,
                json.dumps(permissions),
                expire=settings.PERMISSIONS_CACHE_TTL
            )

        # Check if user has required permission
        has_permission = await self._evaluate_permissions(
            permissions,
            resource_type,
            action,
            resource_id,
            context
        )

        # Audit the permission check
        await self._audit_permission_check(
            user_id,
            resource_type,
            action,
            resource_id,
            has_permission,
            context
        )

        return has_permission

    async def get_user_roles(
        self,
        user_id: int,
        tenant_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> List[Role]:
        """Get user's roles"""
        cache_key = f"user_roles:{user_id}"
        
        # Try to get roles from cache
        cached_roles = await self.cache.get(cache_key)
        if cached_roles:
            return json.loads(cached_roles)

        # Get roles from database
        roles = self.db.query(Role).join(
            Role.users
        ).filter(
            Role.user_id == user_id
        )

        if tenant_id:
            roles = roles.filter(Role.tenant_id == tenant_id)
        if company_id:
            roles = roles.filter(Role.company_id == company_id)

        roles = roles.all()
        
        # Cache roles
        await self.cache.set(
            cache_key,
            json.dumps([role.to_dict() for role in roles]),
            expire=settings.ROLES_CACHE_TTL
        )

        return roles

    async def assign_role(
        self,
        user_id: int,
        role_id: int,
        assigner_id: int,
        request: Request
    ) -> None:
        """Assign role to user"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Check if user already has role
        if role in await self.get_user_roles(user_id):
            raise HTTPException(status_code=400, detail="User already has this role")

        # Assign role
        role.users.append(user_id)
        self.db.commit()

        # Invalidate caches
        await self.cache.delete(f"user_roles:{user_id}")
        await self.cache.delete(f"user_perms:{user_id}")

        # Audit role assignment
        await self._audit_role_change(
            user_id,
            role_id,
            "assign",
            assigner_id,
            request
        )

    async def remove_role(
        self,
        user_id: int,
        role_id: int,
        remover_id: int,
        request: Request
    ) -> None:
        """Remove role from user"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Remove role
        role.users.remove(user_id)
        self.db.commit()

        # Invalidate caches
        await self.cache.delete(f"user_roles:{user_id}")
        await self.cache.delete(f"user_perms:{user_id}")

        # Audit role removal
        await self._audit_role_change(
            user_id,
            role_id,
            "remove",
            remover_id,
            request
        )

    async def check_security_policies(
        self,
        user_id: int,
        action_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """Check if action is allowed by security policies"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # Get applicable security policies
        policies = self.db.query(SecurityPolicy).filter(
            SecurityPolicy.tenant_id == user.tenant_id,
            SecurityPolicy.is_enabled == True
        ).order_by(SecurityPolicy.priority.desc()).all()

        # Evaluate policies
        for policy in policies:
            if not await self._evaluate_security_policy(policy, action_type, context):
                return False

        return True

    async def _load_user_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """Load user's permissions from database"""
        roles = await self.get_user_roles(user_id)
        permissions = []

        for role in roles:
            for perm in role.permissions:
                permissions.append({
                    "resource_type": perm.resource_type,
                    "action": perm.action,
                    "conditions": perm.conditions,
                    "effect": perm.effect
                })

        return permissions

    async def _evaluate_permissions(
        self,
        permissions: List[Dict[str, Any]],
        resource_type: str,
        action: str,
        resource_id: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Evaluate if permissions allow the action"""
        context = context or {}
        if resource_id:
            context["resource_id"] = resource_id

        for perm in permissions:
            if perm["resource_type"] == resource_type and perm["action"] == action:
                if await self._evaluate_conditions(perm["conditions"], context):
                    return perm["effect"] == "allow"

        return False

    async def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate permission conditions"""
        if not conditions:
            return True

        # Implement condition evaluation logic here
        # Example conditions:
        # - Resource ownership
        # - Time-based access
        # - IP-based restrictions
        # - Custom business rules
        return True

    async def _evaluate_security_policy(
        self,
        policy: SecurityPolicy,
        action_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate security policy"""
        if policy.policy_type != action_type:
            return True

        # Evaluate policy rules based on type
        if policy.policy_type == "password":
            return self._evaluate_password_policy(policy, context)
        elif policy.policy_type == "session":
            return self._evaluate_session_policy(policy, context)
        elif policy.policy_type == "rate-limit":
            return self._evaluate_rate_limit_policy(policy, context)

        return True

    def _evaluate_password_policy(
        self,
        policy: SecurityPolicy,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate password security policy"""
        password = context.get("password")
        if not password:
            return True

        settings = policy.settings
        # Check password length
        if len(password) < settings.get("min_length", 8):
            return False

        # Check character requirements
        if settings.get("require_uppercase") and not any(c.isupper() for c in password):
            return False
        if settings.get("require_lowercase") and not any(c.islower() for c in password):
            return False
        if settings.get("require_numbers") and not any(c.isdigit() for c in password):
            return False
        if settings.get("require_special"):
            special_chars = settings.get("special_chars", "!@#$%^&*()_+-=[]{}|;:,.<>?")
            if not any(c in special_chars for c in password):
                return False

        return True

    def _evaluate_session_policy(
        self,
        policy: SecurityPolicy,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate session security policy"""
        settings = policy.settings
        session = context.get("session")
        if not session:
            return True

        # Check session duration
        max_duration = settings.get("max_session_duration", 24 * 60 * 60)
        session_age = (datetime.now(timezone.utc) - session.created_at).total_seconds()
        if session_age > max_duration:
            return False

        # Check idle timeout
        idle_timeout = settings.get("idle_timeout", 30 * 60)
        idle_time = (datetime.now(timezone.utc) - session.last_activity).total_seconds()
        if idle_time > idle_timeout:
            return False

        return True

    def _evaluate_rate_limit_policy(
        self,
        policy: SecurityPolicy,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate rate limit security policy"""
        settings = policy.settings
        key = context.get("rate_limit_key")
        if not key:
            return True

        # Check rate limit
        cache_key = f"rate_limit:{key}"
        current_count = self.cache.get(cache_key) or 0
        
        if current_count >= settings.get("requests_per_minute", 60):
            return False

        # Update counter
        self.cache.incr(cache_key)
        self.cache.expire(cache_key, 60)  # Reset after 1 minute

        return True

    async def _audit_permission_check(
        self,
        user_id: int,
        resource_type: str,
        action: str,
        resource_id: Optional[str],
        allowed: bool,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Audit permission check"""
        log = CoreAuditLog(
            user_id=user_id,
            log_type=AuditLogType.SECURITY,
            action="permission_check",
            status="success" if allowed else "denied",
            metadata={
                "resource_type": resource_type,
                "action": action,
                "resource_id": resource_id,
                "context": context
            }
        )
        self.db.add(log)
        self.db.commit()

    async def _audit_role_change(
        self,
        user_id: int,
        role_id: int,
        action: str,
        actor_id: int,
        request: Request
    ) -> None:
        """Audit role assignment/removal"""
        log = CoreAuditLog(
            user_id=actor_id,
            log_type=AuditLogType.SECURITY,
            action=f"role_{action}",
            status="success",
            metadata={
                "target_user_id": user_id,
                "role_id": role_id,
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent")
            }
        )
        self.db.add(log)
        self.db.commit()
