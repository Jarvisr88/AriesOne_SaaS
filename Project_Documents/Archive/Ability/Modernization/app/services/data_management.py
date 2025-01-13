from datetime import datetime, timedelta
import os
import shutil
import tarfile
import logging
from pathlib import Path
from typing import List, Dict, Optional
import boto3
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using Fernet (symmetric encryption)."""
        return self.cipher_suite.encrypt(data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using Fernet."""
        return self.cipher_suite.decrypt(encrypted_data)

    async def create_backup(self, include_files: bool = True) -> str:
        """Create a full backup of the database and optionally files."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(settings.BACKUP_DIR) / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Database backup
            db_file = backup_dir / 'database.sql'
            engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
            with engine.connect() as conn:
                # Get database size before backup
                result = conn.execute(text(
                    "SELECT pg_database_size(current_database())"
                )).scalar()
                db_size = result / (1024 * 1024)  # Convert to MB
                
                logger.info(f"Starting database backup (size: {db_size:.2f}MB)")
                
                # Create backup using pg_dump
                os.system(
                    f"PGPASSWORD={settings.POSTGRES_PASSWORD} pg_dump "
                    f"-h {settings.POSTGRES_HOST} "
                    f"-U {settings.POSTGRES_USER} "
                    f"{settings.POSTGRES_DB} > {db_file}"
                )

            # Encrypt database backup
            with open(db_file, 'rb') as f:
                encrypted_data = self.encrypt_data(f.read())
            with open(db_file, 'wb') as f:
                f.write(encrypted_data)

            if include_files:
                # Backup uploaded files
                files_dir = Path(settings.UPLOAD_DIR)
                if files_dir.exists():
                    shutil.copytree(files_dir, backup_dir / 'files')

            # Create tarball
            backup_file = f"backup_{timestamp}.tar.gz"
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(backup_dir, arcname=os.path.basename(backup_dir))

            # Upload to S3
            self.s3_client.upload_file(
                backup_file,
                settings.BACKUP_BUCKET,
                f"backups/{backup_file}"
            )

            return backup_file

        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise
        finally:
            # Cleanup temporary files
            shutil.rmtree(backup_dir, ignore_errors=True)
            if os.path.exists(backup_file):
                os.remove(backup_file)

    async def restore_backup(self, backup_file: str) -> bool:
        """Restore from a backup file."""
        temp_dir = Path(settings.TEMP_DIR) / 'restore'
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Download from S3
            local_file = temp_dir / backup_file
            self.s3_client.download_file(
                settings.BACKUP_BUCKET,
                f"backups/{backup_file}",
                str(local_file)
            )

            # Extract backup
            with tarfile.open(local_file, "r:gz") as tar:
                tar.extractall(temp_dir)

            # Decrypt and restore database
            db_file = next(temp_dir.rglob('database.sql'))
            with open(db_file, 'rb') as f:
                decrypted_data = self.decrypt_data(f.read())
            with open(db_file, 'wb') as f:
                f.write(decrypted_data)

            # Restore database
            engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
            with engine.connect() as conn:
                conn.execute(text("DROP SCHEMA public CASCADE"))
                conn.execute(text("CREATE SCHEMA public"))
                os.system(
                    f"PGPASSWORD={settings.POSTGRES_PASSWORD} psql "
                    f"-h {settings.POSTGRES_HOST} "
                    f"-U {settings.POSTGRES_USER} "
                    f"{settings.POSTGRES_DB} < {db_file}"
                )

            # Restore files if present
            files_backup = next(temp_dir.rglob('files'), None)
            if files_backup:
                files_dir = Path(settings.UPLOAD_DIR)
                if files_dir.exists():
                    shutil.rmtree(files_dir)
                shutil.copytree(files_backup, files_dir)

            return True

        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def archive_old_data(self, days: int = 365) -> Dict[str, int]:
        """Archive data older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stats = {'archived_records': 0, 'archived_files': 0}

        try:
            db = SessionLocal()
            
            # Archive database records
            for model in settings.ARCHIVABLE_MODELS:
                # Get records to archive
                records = (
                    db.query(model)
                    .filter(model.created_at < cutoff_date)
                    .all()
                )

                if records:
                    # Export to JSON
                    data = [record.to_dict() for record in records]
                    
                    # Encrypt and upload to S3
                    encrypted_data = self.encrypt_data(str(data).encode())
                    archive_key = (
                        f"archives/{model.__tablename__}/"
                        f"{cutoff_date.strftime('%Y%m%d')}.json.enc"
                    )
                    
                    self.s3_client.put_object(
                        Bucket=settings.ARCHIVE_BUCKET,
                        Key=archive_key,
                        Body=encrypted_data
                    )

                    # Delete archived records
                    for record in records:
                        db.delete(record)
                    
                    stats['archived_records'] += len(records)

            db.commit()

            # Archive old files
            upload_dir = Path(settings.UPLOAD_DIR)
            for file_path in upload_dir.rglob('*'):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        # Upload to S3
                        archive_key = (
                            f"archives/files/"
                            f"{cutoff_date.strftime('%Y%m%d')}/"
                            f"{file_path.relative_to(upload_dir)}"
                        )
                        
                        self.s3_client.upload_file(
                            str(file_path),
                            settings.ARCHIVE_BUCKET,
                            archive_key
                        )
                        
                        # Delete local file
                        file_path.unlink()
                        stats['archived_files'] += 1

            return stats

        except Exception as e:
            logger.error(f"Archival failed: {str(e)}")
            raise

    def implement_gdpr_compliance(self):
        """Implement GDPR compliance measures."""
        try:
            db = SessionLocal()

            # 1. Data Minimization
            # Remove unnecessary columns
            for table in settings.GDPR_SENSITIVE_TABLES:
                for column in settings.GDPR_UNNECESSARY_COLUMNS:
                    if column in table.__table__.columns:
                        db.execute(
                            text(f"ALTER TABLE {table.__tablename__} DROP COLUMN IF EXISTS {column}")
                        )

            # 2. Data Encryption
            # Encrypt sensitive columns
            for table in settings.GDPR_SENSITIVE_TABLES:
                for column in settings.GDPR_SENSITIVE_COLUMNS:
                    if column in table.__table__.columns:
                        db.execute(
                            text(
                                f"UPDATE {table.__tablename__} "
                                f"SET {column} = pgp_sym_encrypt({column}, '{settings.ENCRYPTION_KEY}')"
                            )
                        )

            # 3. Implement Right to be Forgotten
            def delete_user_data(user_id: int):
                """Delete all user data across tables."""
                for table in settings.GDPR_USER_TABLES:
                    db.execute(
                        text(
                            f"DELETE FROM {table.__tablename__} "
                            f"WHERE user_id = :user_id"
                        ),
                        {'user_id': user_id}
                    )

            # 4. Data Retention Policies
            retention_days = settings.DATA_RETENTION_DAYS
            for table in settings.GDPR_SENSITIVE_TABLES:
                db.execute(
                    text(
                        f"DELETE FROM {table.__tablename__} "
                        f"WHERE created_at < NOW() - INTERVAL '{retention_days} days'"
                    )
                )

            # 5. Audit Logging
            db.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS gdpr_audit_log (
                        id SERIAL PRIMARY KEY,
                        action VARCHAR(50) NOT NULL,
                        table_name VARCHAR(50) NOT NULL,
                        record_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        timestamp TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            )

            db.commit()
            return True

        except Exception as e:
            logger.error(f"GDPR compliance implementation failed: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()

    def get_data_retention_status(self) -> Dict[str, any]:
        """Get current data retention status."""
        try:
            db = SessionLocal()
            status = {}

            # Check each sensitive table
            for table in settings.GDPR_SENSITIVE_TABLES:
                result = db.execute(
                    text(
                        f"""
                        SELECT 
                            COUNT(*) as total_records,
                            COUNT(CASE WHEN created_at < NOW() - INTERVAL 
                                '{settings.DATA_RETENTION_DAYS} days' 
                                THEN 1 END) as expired_records,
                            MIN(created_at) as oldest_record,
                            MAX(created_at) as newest_record
                        FROM {table.__tablename__}
                        """
                    )
                ).fetchone()

                status[table.__tablename__] = {
                    'total_records': result.total_records,
                    'expired_records': result.expired_records,
                    'oldest_record': result.oldest_record,
                    'newest_record': result.newest_record
                }

            return status

        except Exception as e:
            logger.error(f"Failed to get retention status: {str(e)}")
            raise
        finally:
            db.close()

    def export_user_data(self, user_id: int) -> Dict[str, any]:
        """Export all data for a specific user (GDPR requirement)."""
        try:
            db = SessionLocal()
            user_data = {}

            # Collect data from all relevant tables
            for table in settings.GDPR_USER_TABLES:
                records = db.execute(
                    text(
                        f"SELECT * FROM {table.__tablename__} "
                        f"WHERE user_id = :user_id"
                    ),
                    {'user_id': user_id}
                ).fetchall()

                user_data[table.__tablename__] = [dict(record) for record in records]

            return user_data

        except Exception as e:
            logger.error(f"Failed to export user data: {str(e)}")
            raise
        finally:
            db.close()
