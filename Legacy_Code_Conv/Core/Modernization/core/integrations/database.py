"""
Core Database Integration Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides database integration functionality.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List, Optional, Type, TypeVar

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from ..base import EntityBase
from ..database import get_session
from ..utils.logging import CoreLogger

T = TypeVar('T', bound=EntityBase)
logger = CoreLogger(__name__)


class DatabaseIntegration:
    """Database integration service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self._session = session
    
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide transaction context."""
        try:
            yield self._session
            await self._session.commit()
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, str]:
        """Check database health."""
        try:
            await self._session.execute(text("SELECT 1"))
            return {"status": "healthy", "message": "Database connection is active"}
        except SQLAlchemyError as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {"status": "unhealthy", "message": str(e)}
    
    async def get_metrics(self) -> Dict[str, int]:
        """Get database metrics."""
        try:
            metrics = {}
            
            # Connection pool stats
            pool = self._session.get_bind().pool
            metrics["pool_size"] = pool.size()
            metrics["checked_out"] = pool.checkedin()
            metrics["overflow"] = pool.overflow()
            
            # Basic table stats
            for table in self._session.get_bind().dialect.get_table_names():
                result = await self._session.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                )
                metrics[f"{table}_count"] = result.scalar()
            
            return metrics
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database metrics: {str(e)}")
            return {"error": str(e)}
    
    async def backup_table(self, table_name: str, backup_suffix: str = "_backup") -> bool:
        """Create a backup of a table."""
        try:
            async with self.transaction():
                await self._session.execute(
                    text(f"CREATE TABLE IF NOT EXISTS {table_name}{backup_suffix} "
                         f"AS TABLE {table_name}")
                )
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to backup table {table_name}: {str(e)}")
            return False
    
    async def restore_table(self, table_name: str,
                          backup_suffix: str = "_backup") -> bool:
        """Restore a table from backup."""
        try:
            backup_table = f"{table_name}{backup_suffix}"
            async with self.transaction():
                await self._session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                await self._session.execute(
                    text(f"CREATE TABLE {table_name} AS TABLE {backup_table}")
                )
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to restore table {table_name}: {str(e)}")
            return False
    
    async def execute_migration(self, migration_sql: str) -> bool:
        """Execute a migration SQL script."""
        try:
            async with self.transaction():
                await self._session.execute(text(migration_sql))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Migration failed: {str(e)}")
            return False
    
    async def get_table_schema(self, table_name: str) -> Optional[Dict]:
        """Get schema information for a table."""
        try:
            result = await self._session.execute(
                text(f"""
                    SELECT column_name, data_type, character_maximum_length,
                           is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                """),
                {"table_name": table_name}
            )
            columns = result.fetchall()
            
            if not columns:
                return None
            
            return {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col[0],
                        "type": col[1],
                        "max_length": col[2],
                        "nullable": col[3],
                        "default": col[4]
                    }
                    for col in columns
                ]
            }
        except SQLAlchemyError as e:
            logger.error(f"Failed to get schema for {table_name}: {str(e)}")
            return None
    
    async def get_related_entities(self, entity: T,
                                 relationship_paths: List[str]) -> Optional[T]:
        """Get entity with related entities loaded."""
        try:
            stmt = select(entity.__class__).where(
                entity.__class__.id == entity.id
            )
            
            for path in relationship_paths:
                stmt = stmt.options(joinedload(path))
            
            result = await self._session.execute(stmt)
            return result.unique().scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get related entities: {str(e)}")
            return None


async def get_db_integration(
    session: AsyncSession = get_session()
) -> DatabaseIntegration:
    """Get database integration instance."""
    return DatabaseIntegration(session)
