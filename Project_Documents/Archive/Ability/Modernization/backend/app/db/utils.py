from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Row
from app.core.logging import logger

class DatabaseUtils:
    @staticmethod
    async def execute_query(
        session: AsyncSession,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Row]:
        """Execute raw SQL query"""
        try:
            result = await session.execute(text(query), params)
            return result.fetchall()
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    @staticmethod
    async def execute_many(
        session: AsyncSession,
        query: str,
        params: List[Dict[str, Any]]
    ) -> None:
        """Execute multiple SQL statements"""
        try:
            await session.execute(text(query), params)
        except Exception as e:
            logger.error(f"Error executing multiple queries: {e}")
            raise

    @staticmethod
    async def check_connection(session: AsyncSession) -> bool:
        """Check database connection"""
        try:
            await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    @staticmethod
    async def get_table_info(
        session: AsyncSession,
        table_name: str
    ) -> List[Dict[str, Any]]:
        """Get table information"""
        try:
            query = """
            SELECT column_name, data_type, character_maximum_length,
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = :table_name
            """
            result = await session.execute(
                text(query),
                {"table_name": table_name}
            )
            return [dict(row) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            raise

    @staticmethod
    async def get_table_size(
        session: AsyncSession,
        table_name: str
    ) -> Dict[str, Any]:
        """Get table size information"""
        try:
            query = """
            SELECT pg_size_pretty(pg_total_relation_size(:table_name)) as total_size,
                   pg_size_pretty(pg_table_size(:table_name)) as table_size,
                   pg_size_pretty(pg_indexes_size(:table_name)) as index_size,
                   (SELECT reltuples::bigint FROM pg_class WHERE relname = :table_name) as row_count
            """
            result = await session.execute(
                text(query),
                {"table_name": table_name}
            )
            return dict(result.fetchone())
        except Exception as e:
            logger.error(f"Error getting table size: {e}")
            raise

    @staticmethod
    async def analyze_query(
        session: AsyncSession,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze query performance"""
        try:
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = await session.execute(text(explain_query), params)
            return result.fetchone()[0]
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            raise

    @staticmethod
    async def vacuum_table(
        session: AsyncSession,
        table_name: str,
        full: bool = False,
        analyze: bool = True
    ) -> None:
        """Vacuum a table"""
        try:
            # Commit any pending transaction as VACUUM cannot run in a transaction block
            await session.commit()
            
            vacuum_type = "FULL" if full else ""
            analyze_cmd = "ANALYZE" if analyze else ""
            
            query = f"VACUUM {vacuum_type} {analyze_cmd} {table_name}"
            await session.execute(text(query))
        except Exception as e:
            logger.error(f"Error vacuuming table: {e}")
            raise

db_utils = DatabaseUtils()
