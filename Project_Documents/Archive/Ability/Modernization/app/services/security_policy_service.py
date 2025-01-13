from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException
import json
import re

from app.models.access_control import SecurityPolicy
from app.core.config import settings

class SecurityPolicyService:
    def __init__(self, db: Session):
        self.db = db

    def create_policy(
        self,
        name: str,
        policy_type: str,
        settings: Dict[str, Any],
        company_id: int,
        description: Optional[str] = None,
        is_enabled: bool = True,
        priority: int = 0
    ) -> SecurityPolicy:
        """Create a new security policy"""
        # Validate policy settings based on type
        self._validate_policy_settings(policy_type, settings)

        policy = SecurityPolicy(
            name=name,
            description=description,
            policy_type=policy_type,
            settings=settings,
            is_enabled=is_enabled,
            priority=priority,
            company_id=company_id
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy

    def get_policy(
        self,
        policy_id: int,
        company_id: int
    ) -> Optional[SecurityPolicy]:
        """Get security policy by ID"""
        return self.db.query(SecurityPolicy).filter(
            SecurityPolicy.id == policy_id,
            SecurityPolicy.company_id == company_id
        ).first()

    def list_policies(
        self,
        company_id: int,
        policy_type: Optional[str] = None,
        is_enabled: Optional[bool] = None
    ) -> List[SecurityPolicy]:
        """List security policies with filters"""
        query = self.db.query(SecurityPolicy).filter(
            SecurityPolicy.company_id == company_id
        )

        if policy_type:
            query = query.filter(SecurityPolicy.policy_type == policy_type)
        if is_enabled is not None:
            query = query.filter(SecurityPolicy.is_enabled == is_enabled)

        return query.order_by(desc(SecurityPolicy.priority)).all()

    def update_policy(
        self,
        policy_id: int,
        company_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        is_enabled: Optional[bool] = None,
        priority: Optional[int] = None
    ) -> Optional[SecurityPolicy]:
        """Update security policy"""
        policy = self.get_policy(policy_id, company_id)
        if not policy:
            return None

        if name:
            policy.name = name
        if description is not None:
            policy.description = description
        if settings is not None:
            self._validate_policy_settings(policy.policy_type, settings)
            policy.settings = settings
        if is_enabled is not None:
            policy.is_enabled = is_enabled
        if priority is not None:
            policy.priority = priority

        self.db.commit()
        self.db.refresh(policy)
        return policy

    def delete_policy(
        self,
        policy_id: int,
        company_id: int
    ) -> bool:
        """Delete security policy"""
        policy = self.get_policy(policy_id, company_id)
        if not policy:
            return False

        self.db.delete(policy)
        self.db.commit()
        return True

    def evaluate_password_policy(
        self,
        password: str,
        company_id: int
    ) -> Dict[str, Any]:
        """Evaluate password against password policies"""
        policies = self.list_policies(
            company_id=company_id,
            policy_type="password",
            is_enabled=True
        )

        results = {
            "valid": True,
            "violations": []
        }

        for policy in policies:
            settings = policy.settings
            
            # Check minimum length
            min_length = settings.get("min_length", 8)
            if len(password) < min_length:
                results["valid"] = False
                results["violations"].append(
                    f"Password must be at least {min_length} characters long"
                )

            # Check character requirements
            if settings.get("require_uppercase", True):
                if not any(c.isupper() for c in password):
                    results["valid"] = False
                    results["violations"].append(
                        "Password must contain at least one uppercase letter"
                    )

            if settings.get("require_lowercase", True):
                if not any(c.islower() for c in password):
                    results["valid"] = False
                    results["violations"].append(
                        "Password must contain at least one lowercase letter"
                    )

            if settings.get("require_numbers", True):
                if not any(c.isdigit() for c in password):
                    results["valid"] = False
                    results["violations"].append(
                        "Password must contain at least one number"
                    )

            if settings.get("require_special", True):
                special_chars = settings.get("special_chars", "!@#$%^&*()_+-=[]{}|;:,.<>?")
                if not any(c in special_chars for c in password):
                    results["valid"] = False
                    results["violations"].append(
                        "Password must contain at least one special character"
                    )

            # Check against common passwords
            if settings.get("check_common_passwords", True):
                common_passwords = settings.get("common_passwords", [])
                if password.lower() in common_passwords:
                    results["valid"] = False
                    results["violations"].append(
                        "Password is too common"
                    )

        return results

    def evaluate_session_policy(
        self,
        company_id: int
    ) -> Dict[str, Any]:
        """Get session policy settings"""
        policies = self.list_policies(
            company_id=company_id,
            policy_type="session",
            is_enabled=True
        )

        # Combine settings from all policies, with higher priority policies taking precedence
        settings = {
            "max_session_duration": 24 * 60 * 60,  # 24 hours in seconds
            "idle_timeout": 30 * 60,  # 30 minutes in seconds
            "max_concurrent_sessions": 5,
            "require_mfa": False,
            "allowed_ip_ranges": [],
            "allowed_user_agents": []
        }

        for policy in policies:
            settings.update(policy.settings)

        return settings

    def evaluate_rate_limit_policy(
        self,
        company_id: int,
        endpoint: str
    ) -> Dict[str, Any]:
        """Get rate limit settings for endpoint"""
        policies = self.list_policies(
            company_id=company_id,
            policy_type="rate-limit",
            is_enabled=True
        )

        # Default settings
        settings = {
            "requests_per_minute": 60,
            "burst_size": 10,
            "throttle_by": "user"  # or "ip" or "company"
        }

        for policy in policies:
            policy_settings = policy.settings
            
            # Check if this policy applies to the endpoint
            endpoints = policy_settings.get("endpoints", ["*"])
            if "*" in endpoints or endpoint in endpoints:
                settings.update(policy_settings)
                break

        return settings

    def _validate_policy_settings(
        self,
        policy_type: str,
        settings: Dict[str, Any]
    ) -> None:
        """Validate policy settings based on type"""
        if policy_type == "password":
            required_fields = ["min_length"]
            for field in required_fields:
                if field not in settings:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required field: {field}"
                    )

            if settings["min_length"] < 8:
                raise HTTPException(
                    status_code=400,
                    detail="Minimum password length must be at least 8"
                )

        elif policy_type == "session":
            if "max_session_duration" in settings:
                if not isinstance(settings["max_session_duration"], int):
                    raise HTTPException(
                        status_code=400,
                        detail="max_session_duration must be an integer"
                    )
                if settings["max_session_duration"] < 300:  # 5 minutes
                    raise HTTPException(
                        status_code=400,
                        detail="max_session_duration must be at least 300 seconds"
                    )

        elif policy_type == "rate-limit":
            required_fields = ["requests_per_minute"]
            for field in required_fields:
                if field not in settings:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required field: {field}"
                    )

            if settings["requests_per_minute"] < 1:
                raise HTTPException(
                    status_code=400,
                    detail="requests_per_minute must be at least 1"
                )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown policy type: {policy_type}"
            )
