from typing import List
import asyncio
from alembic import command
from alembic.config import Config
from app.core.config import settings
from app.core.logging import logger

class MigrationManager:
    def __init__(self):
        self.alembic_cfg = Config(settings.ALEMBIC_CONFIG_PATH)
        self.alembic_cfg.set_main_option("script_location", settings.ALEMBIC_MIGRATIONS_DIR)
        self.alembic_cfg.set_main_option("sqlalchemy.url", settings.POSTGRES_URL)

    async def create_migration(self, message: str) -> None:
        """Create a new migration"""
        try:
            command.revision(
                self.alembic_cfg,
                message=message,
                autogenerate=True
            )
            logger.info(f"Created migration: {message}")
        except Exception as e:
            logger.error(f"Error creating migration: {e}")
            raise

    async def run_migrations(self) -> None:
        """Run all pending migrations"""
        try:
            command.upgrade(self.alembic_cfg, "head")
            logger.info("Migrations completed successfully")
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            raise

    async def rollback_migration(self, revision: str = "-1") -> None:
        """Rollback to a specific migration"""
        try:
            command.downgrade(self.alembic_cfg, revision)
            logger.info(f"Rolled back to revision: {revision}")
        except Exception as e:
            logger.error(f"Error rolling back migration: {e}")
            raise

    async def get_migration_history(self) -> List[str]:
        """Get migration history"""
        try:
            from alembic.runtime.migration import MigrationContext
            from sqlalchemy import create_engine

            engine = create_engine(settings.POSTGRES_URL)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"Error getting migration history: {e}")
            raise

    async def check_migrations(self) -> bool:
        """Check if all migrations are up to date"""
        try:
            from alembic.runtime.migration import MigrationContext
            from alembic.script import ScriptDirectory
            from sqlalchemy import create_engine

            engine = create_engine(settings.POSTGRES_URL)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                script = ScriptDirectory.from_config(self.alembic_cfg)
                head_rev = script.get_current_head()
                return current_rev == head_rev
        except Exception as e:
            logger.error(f"Error checking migrations: {e}")
            raise

migration_manager = MigrationManager()
