from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json
import csv
from pathlib import Path
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import pandas as pd
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationConfig(BaseModel):
    source_db_url: str
    target_db_url: str
    batch_size: int = 1000
    timeout: int = 3600
    backup_dir: str
    validate: bool = True
    dry_run: bool = False

class MigrationStats(BaseModel):
    started_at: datetime
    completed_at: Optional[datetime]
    total_records: int
    migrated_records: int
    failed_records: int
    validation_errors: int
    warnings: List[str]
    errors: List[str]

class MigrationManager:
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.source_engine = create_engine(config.source_db_url)
        self.target_engine = create_engine(config.target_db_url)
        self.Source_Session = sessionmaker(bind=self.source_engine)
        self.Target_Session = sessionmaker(bind=self.target_engine)
        self.backup_path = Path(config.backup_dir)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.stats = {}

    async def run_migration(self):
        """Run the complete migration process"""
        logger.info("Starting migration process")
        
        try:
            # Initialize migration statistics
            self.stats = {
                "started_at": datetime.utcnow(),
                "completed_at": None,
                "total_records": 0,
                "migrated_records": 0,
                "failed_records": 0,
                "validation_errors": 0,
                "warnings": [],
                "errors": []
            }

            # Create backup
            await self.create_backup()

            # Run migrations in order
            migration_order = [
                self.migrate_provider_data,
                self.migrate_patient_data,
                self.migrate_billing_data,
                self.migrate_audit_data
            ]

            for migration_func in migration_order:
                await migration_func()

            # Validate migration
            if self.config.validate:
                await self.validate_migration()

            self.stats["completed_at"] = datetime.utcnow()
            await self.save_migration_report()

            logger.info("Migration completed successfully")
            return self.stats

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.stats["errors"].append(str(e))
            await self.save_migration_report()
            raise

    async def create_backup(self):
        """Create backup of source data"""
        logger.info("Creating backup of source data")
        
        backup_time = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        tables = [
            "providers",
            "patients",
            "addresses",
            "billing_transactions",
            "audit_logs"
        ]

        source_session = self.Source_Session()
        try:
            for table in tables:
                logger.info(f"Backing up table: {table}")
                query = f"SELECT * FROM {table}"
                df = pd.read_sql(query, source_session.bind)
                
                # Save as both CSV and JSON for redundancy
                backup_file_csv = self.backup_path / f"{table}_{backup_time}.csv"
                backup_file_json = self.backup_path / f"{table}_{backup_time}.json"
                
                df.to_csv(backup_file_csv, index=False)
                df.to_json(backup_file_json, orient="records")

        finally:
            source_session.close()

    async def migrate_provider_data(self):
        """Migrate provider data"""
        logger.info("Migrating provider data")
        
        source_session = self.Source_Session()
        target_session = self.Target_Session()
        
        try:
            # Get total count for progress bar
            total = source_session.execute(
                text("SELECT COUNT(*) FROM providers")
            ).scalar()

            query = text("""
                SELECT p.*, n.* 
                FROM providers p
                LEFT JOIN provider_names n ON p.id = n.provider_id
            """)

            for batch_start in tqdm(range(0, total, self.config.batch_size)):
                rows = source_session.execute(
                    query.offset(batch_start).limit(self.config.batch_size)
                ).fetchall()

                for row in rows:
                    try:
                        if not self.config.dry_run:
                            # Transform and insert provider data
                            provider_data = self._transform_provider_data(row)
                            target_session.execute(
                                text("INSERT INTO providers (id, status, created_at, updated_at) "
                                     "VALUES (:id, :status, :created_at, :updated_at)"),
                                provider_data
                            )

                            # Insert provider name
                            name_data = self._transform_provider_name_data(row)
                            target_session.execute(
                                text("INSERT INTO provider_names (provider_id, name_type, "
                                     "first_name, last_name, credentials) "
                                     "VALUES (:provider_id, :name_type, :first_name, "
                                     ":last_name, :credentials)"),
                                name_data
                            )

                        self.stats["migrated_records"] += 1

                    except Exception as e:
                        logger.error(f"Failed to migrate provider {row.id}: {e}")
                        self.stats["failed_records"] += 1
                        self.stats["errors"].append(f"Provider {row.id}: {str(e)}")

                if not self.config.dry_run:
                    target_session.commit()

            self.stats["total_records"] += total

        finally:
            source_session.close()
            target_session.close()

    async def migrate_patient_data(self):
        """Migrate patient data"""
        logger.info("Migrating patient data")
        
        source_session = self.Source_Session()
        target_session = self.Target_Session()
        
        try:
            total = source_session.execute(
                text("SELECT COUNT(*) FROM patients")
            ).scalar()

            query = text("""
                SELECT p.*, a.*
                FROM patients p
                LEFT JOIN addresses a ON p.id = a.patient_id
            """)

            for batch_start in tqdm(range(0, total, self.config.batch_size)):
                rows = source_session.execute(
                    query.offset(batch_start).limit(self.config.batch_size)
                ).fetchall()

                for row in rows:
                    try:
                        if not self.config.dry_run:
                            # Transform and insert patient data
                            patient_data = self._transform_patient_data(row)
                            target_session.execute(
                                text("INSERT INTO patients (id, status, created_at, updated_at) "
                                     "VALUES (:id, :status, :created_at, :updated_at)"),
                                patient_data
                            )

                            # Insert patient address
                            address_data = self._transform_address_data(row)
                            target_session.execute(
                                text("INSERT INTO patient_addresses (patient_id, address_type, "
                                     "street_address, city, state, postal_code, country) "
                                     "VALUES (:patient_id, :address_type, :street_address, "
                                     ":city, :state, :postal_code, :country)"),
                                address_data
                            )

                        self.stats["migrated_records"] += 1

                    except Exception as e:
                        logger.error(f"Failed to migrate patient {row.id}: {e}")
                        self.stats["failed_records"] += 1
                        self.stats["errors"].append(f"Patient {row.id}: {str(e)}")

                if not self.config.dry_run:
                    target_session.commit()

            self.stats["total_records"] += total

        finally:
            source_session.close()
            target_session.close()

    async def migrate_billing_data(self):
        """Migrate billing data"""
        logger.info("Migrating billing data")
        
        source_session = self.Source_Session()
        target_session = self.Target_Session()
        
        try:
            total = source_session.execute(
                text("SELECT COUNT(*) FROM billing_transactions")
            ).scalar()

            query = text("SELECT * FROM billing_transactions")

            for batch_start in tqdm(range(0, total, self.config.batch_size)):
                rows = source_session.execute(
                    query.offset(batch_start).limit(self.config.batch_size)
                ).fetchall()

                for row in rows:
                    try:
                        if not self.config.dry_run:
                            billing_data = self._transform_billing_data(row)
                            target_session.execute(
                                text("INSERT INTO billing_transactions "
                                     "(id, patient_id, provider_id, amount, status, created_at) "
                                     "VALUES (:id, :patient_id, :provider_id, :amount, "
                                     ":status, :created_at)"),
                                billing_data
                            )

                        self.stats["migrated_records"] += 1

                    except Exception as e:
                        logger.error(f"Failed to migrate transaction {row.id}: {e}")
                        self.stats["failed_records"] += 1
                        self.stats["errors"].append(f"Transaction {row.id}: {str(e)}")

                if not self.config.dry_run:
                    target_session.commit()

            self.stats["total_records"] += total

        finally:
            source_session.close()
            target_session.close()

    async def migrate_audit_data(self):
        """Migrate audit logs"""
        logger.info("Migrating audit data")
        
        source_session = self.Source_Session()
        target_session = self.Target_Session()
        
        try:
            total = source_session.execute(
                text("SELECT COUNT(*) FROM audit_logs")
            ).scalar()

            query = text("SELECT * FROM audit_logs")

            for batch_start in tqdm(range(0, total, self.config.batch_size)):
                rows = source_session.execute(
                    query.offset(batch_start).limit(self.config.batch_size)
                ).fetchall()

                for row in rows:
                    try:
                        if not self.config.dry_run:
                            audit_data = self._transform_audit_data(row)
                            target_session.execute(
                                text("INSERT INTO audit_logs "
                                     "(id, event_type, user_id, details, created_at) "
                                     "VALUES (:id, :event_type, :user_id, :details, :created_at)"),
                                audit_data
                            )

                        self.stats["migrated_records"] += 1

                    except Exception as e:
                        logger.error(f"Failed to migrate audit log {row.id}: {e}")
                        self.stats["failed_records"] += 1
                        self.stats["errors"].append(f"Audit log {row.id}: {str(e)}")

                if not self.config.dry_run:
                    target_session.commit()

            self.stats["total_records"] += total

        finally:
            source_session.close()
            target_session.close()

    async def validate_migration(self):
        """Validate migrated data"""
        logger.info("Validating migrated data")
        
        source_session = self.Source_Session()
        target_session = self.Target_Session()
        
        try:
            # Validate record counts
            tables = ["providers", "patients", "billing_transactions", "audit_logs"]
            
            for table in tables:
                source_count = source_session.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar()
                
                target_count = target_session.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar()
                
                if source_count != target_count:
                    message = f"Count mismatch for {table}: source={source_count}, target={target_count}"
                    logger.warning(message)
                    self.stats["warnings"].append(message)

            # Validate data integrity
            await self._validate_provider_data()
            await self._validate_patient_data()
            await self._validate_billing_data()

        finally:
            source_session.close()
            target_session.close()

    async def save_migration_report(self):
        """Save migration report"""
        report_time = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = self.backup_path / f"migration_report_{report_time}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)

    def _transform_provider_data(self, row: Dict) -> Dict:
        """Transform provider data from source to target format"""
        return {
            "id": row.id,
            "status": row.status,
            "created_at": row.created_at,
            "updated_at": row.updated_at
        }

    def _transform_provider_name_data(self, row: Dict) -> Dict:
        """Transform provider name data from source to target format"""
        return {
            "provider_id": row.id,
            "name_type": "legal",
            "first_name": row.first_name,
            "last_name": row.last_name,
            "credentials": row.credentials
        }

    def _transform_patient_data(self, row: Dict) -> Dict:
        """Transform patient data from source to target format"""
        return {
            "id": row.id,
            "status": row.status,
            "created_at": row.created_at,
            "updated_at": row.updated_at
        }

    def _transform_address_data(self, row: Dict) -> Dict:
        """Transform address data from source to target format"""
        return {
            "patient_id": row.patient_id,
            "address_type": row.address_type,
            "street_address": row.street_address,
            "city": row.city,
            "state": row.state,
            "postal_code": row.postal_code,
            "country": row.country
        }

    def _transform_billing_data(self, row: Dict) -> Dict:
        """Transform billing data from source to target format"""
        return {
            "id": row.id,
            "patient_id": row.patient_id,
            "provider_id": row.provider_id,
            "amount": row.amount,
            "status": row.status,
            "created_at": row.created_at
        }

    def _transform_audit_data(self, row: Dict) -> Dict:
        """Transform audit data from source to target format"""
        return {
            "id": row.id,
            "event_type": row.event_type,
            "user_id": row.user_id,
            "details": row.details,
            "created_at": row.created_at
        }

    async def _validate_provider_data(self):
        """Validate provider data integrity"""
        # Implementation of provider data validation
        pass

    async def _validate_patient_data(self):
        """Validate patient data integrity"""
        # Implementation of patient data validation
        pass

    async def _validate_billing_data(self):
        """Validate billing data integrity"""
        # Implementation of billing data validation
        pass
