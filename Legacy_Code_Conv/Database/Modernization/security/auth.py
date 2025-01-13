"""Database authentication and authorization module.

This module provides functionality for managing database users,
roles, permissions, and password policies.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import argon2
from cryptography.fernet import Fernet

from infrastructure.database import get_session
from infrastructure.config import get_database_settings

# Setup logging
logger = logging.getLogger(__name__)

# Get database settings
settings = get_database_settings()


class DatabaseAuth:
    """Database authentication and authorization management."""
    
    def __init__(self):
        """Initialize database auth manager."""
        self.password_hasher = argon2.using(
            time_cost=4,      # Number of iterations
            memory_cost=65536, # Memory usage in KiB
            parallelism=2,    # Number of parallel threads
            hash_len=32,      # Length of the hash in bytes
            salt_len=16       # Length of the salt in bytes
        )
    
    async def create_role(
        self,
        role_name: str,
        permissions: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create database role with specified permissions.
        
        Args:
            role_name: Name of the role
            permissions: List of permissions to grant
            description: Optional role description
            
        Returns:
            dict: Role creation results
        """
        try:
            async with get_session() as session:
                # Create role
                await session.execute(
                    text(f"CREATE ROLE {role_name}")
                )
                
                # Grant permissions
                for permission in permissions:
                    await session.execute(
                        text(f"GRANT {permission} TO {role_name}")
                    )
                
                # Add description if provided
                if description:
                    await session.execute(
                        text(f"COMMENT ON ROLE {role_name} IS '{description}'")
                    )
                
                await session.commit()
                
                return {
                    "status": "success",
                    "role": role_name,
                    "permissions": permissions,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to create role: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def create_user(
        self,
        username: str,
        password: str,
        roles: List[str],
        connection_limit: int = 5
    ) -> Dict[str, Any]:
        """Create database user with roles and connection limit.
        
        Args:
            username: Username for new user
            password: Password for new user
            roles: List of roles to assign
            connection_limit: Maximum concurrent connections
            
        Returns:
            dict: User creation results
        """
        try:
            # Hash password
            hashed_password = self.password_hasher.hash(password)
            
            async with get_session() as session:
                # Create user with connection limit
                await session.execute(
                    text(
                        f"CREATE USER {username} WITH "
                        f"PASSWORD '{hashed_password}' "
                        f"CONNECTION LIMIT {connection_limit}"
                    )
                )
                
                # Grant roles
                for role in roles:
                    await session.execute(
                        text(f"GRANT {role} TO {username}")
                    )
                
                await session.commit()
                
                return {
                    "status": "success",
                    "username": username,
                    "roles": roles,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to create user: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def update_user_password(
        self,
        username: str,
        new_password: str
    ) -> Dict[str, Any]:
        """Update user password with new hashed password.
        
        Args:
            username: Username to update
            new_password: New password to set
            
        Returns:
            dict: Password update results
        """
        try:
            # Hash new password
            hashed_password = self.password_hasher.hash(new_password)
            
            async with get_session() as session:
                await session.execute(
                    text(
                        f"ALTER USER {username} "
                        f"WITH PASSWORD '{hashed_password}'"
                    )
                )
                await session.commit()
                
                return {
                    "status": "success",
                    "username": username,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to update password: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def revoke_user_access(
        self,
        username: str,
        roles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Revoke user access or specific roles.
        
        Args:
            username: Username to revoke
            roles: Optional list of roles to revoke
            
        Returns:
            dict: Access revocation results
        """
        try:
            async with get_session() as session:
                if roles:
                    # Revoke specific roles
                    for role in roles:
                        await session.execute(
                            text(f"REVOKE {role} FROM {username}")
                        )
                else:
                    # Disable user account
                    await session.execute(
                        text(f"ALTER USER {username} NOLOGIN")
                    )
                
                await session.commit()
                
                return {
                    "status": "success",
                    "username": username,
                    "roles_revoked": roles if roles else "all",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to revoke access: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def audit_user_access(
        self,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Audit user access and roles.
        
        Args:
            username: Optional username to audit
            
        Returns:
            dict: Audit results
        """
        try:
            async with get_session() as session:
                if username:
                    # Audit specific user
                    result = await session.execute(
                        text(
                            "SELECT r.rolname, r.rolcanlogin, "
                            "r.rolconnlimit, r.rolvaliduntil "
                            "FROM pg_roles r "
                            "WHERE r.rolname = :username"
                        ),
                        {"username": username}
                    )
                else:
                    # Audit all users
                    result = await session.execute(
                        text(
                            "SELECT r.rolname, r.rolcanlogin, "
                            "r.rolconnlimit, r.rolvaliduntil "
                            "FROM pg_roles r "
                            "WHERE r.rolcanlogin = true"
                        )
                    )
                
                users = [dict(row) for row in result]
                
                return {
                    "status": "success",
                    "users": users,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to audit access: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
