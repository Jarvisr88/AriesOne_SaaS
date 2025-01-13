"""
Database Rollback Procedures
Version: 1.0.0
Last Updated: 2025-01-10
"""
import os
import sys
import logging
import subprocess
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from alembic import command
from alembic.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseRollback:
    def __init__(
        self,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        backup_dir: str
    ):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self):
        """Create database connection."""
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
    
    def create_backup(self, tag: str = None) -> Path:
        """Create a database backup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tag = tag or 'pre_migration'
        backup_file = self.backup_dir / f"{self.db_name}_{tag}_{timestamp}.dump"
        
        try:
            logger.info(f"Creating backup: {backup_file}")
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_password
            
            result = subprocess.run([
                'pg_dump',
                '-h', self.db_host,
                '-p', str(self.db_port),
                '-U', self.db_user,
                '-Fc',  # Custom format
                '-v',   # Verbose
                '-f', str(backup_file),
                self.db_name
            ], env=env, check=True, capture_output=True, text=True)
            
            logger.info(f"Backup created successfully: {backup_file}")
            return backup_file
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e.stderr}")
            raise
    
    def restore_backup(self, backup_file: Path) -> bool:
        """Restore database from backup."""
        try:
            logger.info(f"Restoring backup: {backup_file}")
            
            # Drop existing connections
            with self._get_connection() as conn:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = %s
                        AND pid <> pg_backend_pid()
                    """, [self.db_name])
            
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_password
            
            # Restore backup
            result = subprocess.run([
                'pg_restore',
                '-h', self.db_host,
                '-p', str(self.db_port),
                '-U', self.db_user,
                '-d', self.db_name,
                '-c',  # Clean (drop) database objects before recreating
                '-v',  # Verbose
                str(backup_file)
            ], env=env, check=True, capture_output=True, text=True)
            
            logger.info("Backup restored successfully")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Restore failed: {e.stderr}")
            raise
    
    def rollback_migration(self, target_revision: str):
        """Rollback database to specific migration version."""
        try:
            logger.info(f"Rolling back to revision: {target_revision}")
            
            # Create backup before rollback
            backup_file = self.create_backup(tag='pre_rollback')
            
            # Initialize Alembic config
            alembic_cfg = Config("alembic.ini")
            
            # Execute rollback
            command.downgrade(alembic_cfg, target_revision)
            
            logger.info(f"Successfully rolled back to revision: {target_revision}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            logger.info("Attempting to restore from backup...")
            self.restore_backup(backup_file)
            raise
    
    def verify_database_state(self) -> bool:
        """Verify database state after rollback."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Check table existence
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                    tables = {row[0] for row in cur.fetchall()}
                    
                    # Verify core tables exist
                    required_tables = {
                        'users', 'tenants', 'inventory_items',
                        'orders', 'order_items', 'audit_logs'
                    }
                    missing_tables = required_tables - tables
                    
                    if missing_tables:
                        logger.error(f"Missing tables: {missing_tables}")
                        return False
                    
                    # Check data integrity
                    for table in required_tables:
                        cur.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cur.fetchone()[0]
                        logger.info(f"Table {table}: {count} rows")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
    
    def cleanup_old_backups(self, max_age_days: int = 30):
        """Clean up old backup files."""
        try:
            logger.info(f"Cleaning up backups older than {max_age_days} days")
            cutoff = datetime.now().timestamp() - (max_age_days * 86400)
            
            for backup_file in self.backup_dir.glob("*.dump"):
                if backup_file.stat().st_mtime < cutoff:
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file}")
                    
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python database_rollback.py [backup|restore|rollback|verify|cleanup]")
        sys.exit(1)
    
    # Load configuration from environment
    db_config = {
        'db_host': os.getenv('DB_HOST', 'localhost'),
        'db_port': int(os.getenv('DB_PORT', '5432')),
        'db_name': os.getenv('DB_NAME', 'ariesone'),
        'db_user': os.getenv('DB_USER', 'postgres'),
        'db_password': os.getenv('DB_PASSWORD', ''),
        'backup_dir': os.getenv('BACKUP_DIR', './backups')
    }
    
    rollback = DatabaseRollback(**db_config)
    command = sys.argv[1]
    
    try:
        if command == 'backup':
            rollback.create_backup()
        
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("Please specify backup file to restore")
                sys.exit(1)
            rollback.restore_backup(Path(sys.argv[2]))
        
        elif command == 'rollback':
            if len(sys.argv) < 3:
                print("Please specify target revision")
                sys.exit(1)
            rollback.rollback_migration(sys.argv[2])
        
        elif command == 'verify':
            success = rollback.verify_database_state()
            sys.exit(0 if success else 1)
        
        elif command == 'cleanup':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            rollback.cleanup_old_backups(days)
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
