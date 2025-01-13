"""Database encryption module.

This module provides functionality for encrypting sensitive data
at rest and in transit, including key management and audit logging.
"""
import os
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timezone
from sqlalchemy import text, Column
from sqlalchemy.types import TypeDecorator, String
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from base64 import b64encode, b64decode

from infrastructure.database import get_session

# Setup logging
logger = logging.getLogger(__name__)


class EncryptedType(TypeDecorator):
    """SQLAlchemy type for encrypted columns."""
    
    impl = String
    cache_ok = True
    
    def __init__(self, key: bytes, **kwargs):
        """Initialize encrypted type.
        
        Args:
            key: Encryption key
            **kwargs: Additional arguments for String type
        """
        super().__init__(**kwargs)
        self.fernet = Fernet(key)
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt value before saving to database."""
        if value is not None:
            return self.fernet.encrypt(value.encode()).decode()
        return None
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """Decrypt value when reading from database."""
        if value is not None:
            return self.fernet.decrypt(value.encode()).decode()
        return None


class DatabaseEncryption:
    """Database encryption management."""
    
    def __init__(self, master_key: bytes):
        """Initialize database encryption.
        
        Args:
            master_key: Master encryption key
        """
        self.master_key = master_key
        self.key_derivation = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"static_salt",  # In production, use a secure random salt
            iterations=100000,
        )
    
    def _derive_key(self, context: str) -> bytes:
        """Derive encryption key for specific context.
        
        Args:
            context: Context for key derivation
            
        Returns:
            bytes: Derived encryption key
        """
        context_key = self.key_derivation.derive(
            self.master_key + context.encode()
        )
        return b64encode(context_key)
    
    async def setup_column_encryption(
        self,
        table_name: str,
        column_name: str
    ) -> Dict[str, Any]:
        """Setup encryption for database column.
        
        Args:
            table_name: Name of table
            column_name: Name of column
            
        Returns:
            dict: Setup results
        """
        try:
            # Derive key for column
            column_key = self._derive_key(f"{table_name}.{column_name}")
            
            async with get_session() as session:
                # Create encrypted column
                await session.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        f"ADD COLUMN {column_name}_encrypted TEXT"
                    )
                )
                
                # Encrypt existing data
                await session.execute(
                    text(
                        f"UPDATE {table_name} "
                        f"SET {column_name}_encrypted = pgp_sym_encrypt("
                        f"{column_name}::text, :key)"
                    ),
                    {"key": column_key.decode()}
                )
                
                # Drop original column
                await session.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        f"DROP COLUMN {column_name}"
                    )
                )
                
                # Rename encrypted column
                await session.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        f"RENAME COLUMN {column_name}_encrypted "
                        f"TO {column_name}"
                    )
                )
                
                await session.commit()
                
                return {
                    "status": "success",
                    "table": table_name,
                    "column": column_name,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except Exception as e:
            logger.error(f"Failed to setup column encryption: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def rotate_encryption_key(
        self,
        table_name: str,
        column_name: str
    ) -> Dict[str, Any]:
        """Rotate encryption key for column.
        
        Args:
            table_name: Name of table
            column_name: Name of column
            
        Returns:
            dict: Key rotation results
        """
        try:
            # Generate new key
            new_key = self._derive_key(
                f"{table_name}.{column_name}.{datetime.now().isoformat()}"
            )
            
            async with get_session() as session:
                # Create temporary column
                await session.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        f"ADD COLUMN {column_name}_new TEXT"
                    )
                )
                
                # Re-encrypt data with new key
                await session.execute(
                    text(
                        f"UPDATE {table_name} "
                        f"SET {column_name}_new = pgp_sym_encrypt("
                        f"pgp_sym_decrypt({column_name}, :old_key)::text, "
                        f":new_key)"
                    ),
                    {
                        "old_key": self._derive_key(
                            f"{table_name}.{column_name}"
                        ).decode(),
                        "new_key": new_key.decode()
                    }
                )
                
                # Drop old column
                await session.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        f"DROP COLUMN {column_name}"
                    )
                )
                
                # Rename new column
                await session.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        f"RENAME COLUMN {column_name}_new "
                        f"TO {column_name}"
                    )
                )
                
                await session.commit()
                
                return {
                    "status": "success",
                    "table": table_name,
                    "column": column_name,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except Exception as e:
            logger.error(f"Failed to rotate encryption key: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def audit_encryption(
        self,
        table_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Audit database encryption.
        
        Args:
            table_name: Optional table name to audit
            
        Returns:
            dict: Audit results
        """
        try:
            async with get_session() as session:
                if table_name:
                    # Audit specific table
                    result = await session.execute(
                        text(
                            "SELECT c.column_name, c.data_type, "
                            "c.column_default, c.is_nullable "
                            "FROM information_schema.columns c "
                            "WHERE c.table_name = :table_name "
                            "AND c.table_schema = 'public'"
                        ),
                        {"table_name": table_name}
                    )
                else:
                    # Audit all tables
                    result = await session.execute(
                        text(
                            "SELECT c.table_name, c.column_name, "
                            "c.data_type, c.column_default, c.is_nullable "
                            "FROM information_schema.columns c "
                            "WHERE c.table_schema = 'public'"
                        )
                    )
                
                columns = [dict(row) for row in result]
                
                return {
                    "status": "success",
                    "columns": columns,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except Exception as e:
            logger.error(f"Failed to audit encryption: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
