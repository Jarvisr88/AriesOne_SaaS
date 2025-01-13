"""Database backup management module.

This module provides functionality for managing database backups,
including creation, encryption, verification, and restoration.
"""
import os
import gzip
import logging
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
from cryptography.fernet import Fernet

from infrastructure.config import get_database_settings

# Setup logging
logger = logging.getLogger(__name__)

# Get database settings
settings = get_database_settings()


class BackupManager:
    """Database backup management class."""
    
    def __init__(
        self,
        backup_dir: str = "backups",
        retention_days: int = 30,
        encryption_key: Optional[str] = None
    ):
        """Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
            retention_days: Number of days to retain backups
            encryption_key: Key for backup encryption
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.encryption_key = encryption_key.encode() if encryption_key else None
        self.fernet = Fernet(self.encryption_key) if self.encryption_key else None
    
    def _get_backup_filename(self, prefix: str = "backup") -> str:
        """Generate backup filename with timestamp."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.sql.gz"
    
    def _get_pg_dump_cmd(self, output_file: Path) -> list:
        """Get pg_dump command with proper arguments."""
        return [
            "pg_dump",
            "-h", settings.POSTGRES_HOST,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-F", "p",  # Plain text format
            "-f", str(output_file)
        ]
    
    def _get_pg_restore_cmd(self, input_file: Path) -> list:
        """Get pg_restore command with proper arguments."""
        return [
            "psql",
            "-h", settings.POSTGRES_HOST,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", str(input_file)
        ]
    
    async def create_backup(self) -> Dict[str, Any]:
        """Create database backup.
        
        Returns:
            dict: Backup results including:
                - status: Backup status
                - filename: Backup filename
                - size: Backup size
                - timestamp: Backup timestamp
        """
        try:
            filename = self._get_backup_filename()
            backup_path = self.backup_dir / filename
            temp_path = backup_path.with_suffix(".tmp")
            
            # Create backup using pg_dump
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
            
            process = await subprocess.create_subprocess_exec(
                *self._get_pg_dump_cmd(temp_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Backup failed: {stderr.decode()}")
            
            # Compress backup
            with open(temp_path, "rb") as f_in:
                with gzip.open(backup_path, "wb") as f_out:
                    f_out.write(f_in.read())
            
            # Encrypt if key provided
            if self.fernet:
                with open(backup_path, "rb") as f:
                    encrypted_data = self.fernet.encrypt(f.read())
                with open(backup_path, "wb") as f:
                    f.write(encrypted_data)
            
            # Cleanup temp file
            temp_path.unlink()
            
            return {
                "status": "success",
                "filename": filename,
                "size": backup_path.stat().st_size,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def restore_backup(self, filename: str) -> Dict[str, Any]:
        """Restore database from backup.
        
        Args:
            filename: Name of backup file to restore
            
        Returns:
            dict: Restore results including:
                - status: Restore status
                - filename: Backup filename
                - timestamp: Restore timestamp
        """
        try:
            backup_path = self.backup_dir / filename
            temp_path = backup_path.with_suffix(".tmp")
            
            # Decrypt if encrypted
            if self.fernet:
                with open(backup_path, "rb") as f:
                    decrypted_data = self.fernet.decrypt(f.read())
                with open(temp_path, "wb") as f:
                    f.write(decrypted_data)
            else:
                temp_path = backup_path
            
            # Decompress backup
            with gzip.open(temp_path, "rb") as f_in:
                with open(temp_path.with_suffix(""), "wb") as f_out:
                    f_out.write(f_in.read())
            
            # Restore using psql
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
            
            process = await subprocess.create_subprocess_exec(
                *self._get_pg_restore_cmd(temp_path.with_suffix("")),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Restore failed: {stderr.decode()}")
            
            # Cleanup temp files
            if temp_path != backup_path:
                temp_path.unlink()
            temp_path.with_suffix("").unlink()
            
            return {
                "status": "success",
                "filename": filename,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def verify_backup(self, filename: str) -> Dict[str, Any]:
        """Verify backup integrity.
        
        Args:
            filename: Name of backup file to verify
            
        Returns:
            dict: Verification results including:
                - status: Verification status
                - filename: Backup filename
                - timestamp: Verification timestamp
        """
        try:
            backup_path = self.backup_dir / filename
            
            # Check file exists
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {filename}")
            
            # Try to read and decompress
            with gzip.open(backup_path, "rb") as f:
                # Read first few bytes to verify format
                f.read(1024)
            
            # Decrypt if encrypted
            if self.fernet:
                with open(backup_path, "rb") as f:
                    self.fernet.decrypt(f.read())
            
            return {
                "status": "success",
                "filename": filename,
                "size": backup_path.stat().st_size,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def cleanup_old_backups(self) -> Dict[str, Any]:
        """Remove backups older than retention period.
        
        Returns:
            dict: Cleanup results including:
                - status: Cleanup status
                - removed: List of removed backups
                - timestamp: Cleanup timestamp
        """
        try:
            removed = []
            cutoff = datetime.now(timezone.utc).timestamp() - (
                self.retention_days * 24 * 60 * 60
            )
            
            for backup_file in self.backup_dir.glob("backup_*.sql.gz"):
                if backup_file.stat().st_mtime < cutoff:
                    backup_file.unlink()
                    removed.append(backup_file.name)
            
            return {
                "status": "success",
                "removed": removed,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
