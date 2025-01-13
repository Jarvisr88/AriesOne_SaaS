"""Database access control module.

This module provides functionality for managing database access controls,
including row-level security, schema permissions, and object ownership.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database import get_session

# Setup logging
logger = logging.getLogger(__name__)


class DatabaseAccess:
    """Database access control management."""
    
    async def enable_row_level_security(
        self,
        table_name: str,
        policy_name: str,
        policy: str,
        roles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Enable row-level security policy on table.
        
        Args:
            table_name: Name of table
            policy_name: Name of policy
            policy: Policy definition (WHERE clause)
            roles: Optional list of roles to apply policy to
            
        Returns:
            dict: Policy creation results
        """
        try:
            async with get_session() as session:
                # Enable RLS on table
                await session.execute(
                    text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")
                )
                
                # Create policy
                policy_sql = (
                    f"CREATE POLICY {policy_name} ON {table_name} "
                    f"FOR ALL "
                )
                
                if roles:
                    policy_sql += f"TO {','.join(roles)} "
                
                policy_sql += f"USING ({policy})"
                
                await session.execute(text(policy_sql))
                await session.commit()
                
                return {
                    "status": "success",
                    "table": table_name,
                    "policy": policy_name,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to enable RLS: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def set_schema_permissions(
        self,
        schema_name: str,
        role: str,
        permissions: List[str]
    ) -> Dict[str, Any]:
        """Set permissions on schema for role.
        
        Args:
            schema_name: Name of schema
            role: Role to grant permissions to
            permissions: List of permissions to grant
            
        Returns:
            dict: Permission results
        """
        try:
            async with get_session() as session:
                # Grant schema usage
                await session.execute(
                    text(f"GRANT USAGE ON SCHEMA {schema_name} TO {role}")
                )
                
                # Grant specified permissions
                for permission in permissions:
                    await session.execute(
                        text(
                            f"GRANT {permission} ON ALL TABLES "
                            f"IN SCHEMA {schema_name} TO {role}"
                        )
                    )
                    
                    # Grant for future tables
                    await session.execute(
                        text(
                            f"ALTER DEFAULT PRIVILEGES "
                            f"IN SCHEMA {schema_name} "
                            f"GRANT {permission} ON TABLES TO {role}"
                        )
                    )
                
                await session.commit()
                
                return {
                    "status": "success",
                    "schema": schema_name,
                    "role": role,
                    "permissions": permissions,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to set schema permissions: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def transfer_ownership(
        self,
        object_type: str,
        object_name: str,
        new_owner: str
    ) -> Dict[str, Any]:
        """Transfer ownership of database object.
        
        Args:
            object_type: Type of object (TABLE, SEQUENCE, etc.)
            object_name: Name of object
            new_owner: New owner role
            
        Returns:
            dict: Transfer results
        """
        try:
            async with get_session() as session:
                await session.execute(
                    text(
                        f"ALTER {object_type} {object_name} "
                        f"OWNER TO {new_owner}"
                    )
                )
                await session.commit()
                
                return {
                    "status": "success",
                    "object_type": object_type,
                    "object_name": object_name,
                    "new_owner": new_owner,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to transfer ownership: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def set_connection_limits(
        self,
        role: str,
        connection_limit: int
    ) -> Dict[str, Any]:
        """Set connection limits for role.
        
        Args:
            role: Role to set limits for
            connection_limit: Maximum concurrent connections
            
        Returns:
            dict: Limit setting results
        """
        try:
            async with get_session() as session:
                await session.execute(
                    text(
                        f"ALTER ROLE {role} "
                        f"CONNECTION LIMIT {connection_limit}"
                    )
                )
                await session.commit()
                
                return {
                    "status": "success",
                    "role": role,
                    "connection_limit": connection_limit,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to set connection limits: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def audit_permissions(
        self,
        object_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Audit database permissions.
        
        Args:
            object_name: Optional object name to audit
            
        Returns:
            dict: Audit results
        """
        try:
            async with get_session() as session:
                if object_name:
                    # Audit specific object
                    result = await session.execute(
                        text(
                            "SELECT grantee, privilege_type "
                            "FROM information_schema.role_table_grants "
                            "WHERE table_name = :object_name"
                        ),
                        {"object_name": object_name}
                    )
                else:
                    # Audit all objects
                    result = await session.execute(
                        text(
                            "SELECT table_schema, table_name, "
                            "grantee, privilege_type "
                            "FROM information_schema.role_table_grants "
                            "WHERE table_schema = 'public'"
                        )
                    )
                
                permissions = [dict(row) for row in result]
                
                return {
                    "status": "success",
                    "permissions": permissions,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except SQLAlchemyError as e:
            logger.error(f"Failed to audit permissions: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
