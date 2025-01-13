from typing import Dict, Optional, Any
import asyncpg
from asyncpg.pool import Pool
from app.core.config import settings
from app.core.logging import logger
from app.core.monitoring import metrics

class ConnectionManager:
    def __init__(self):
        self.pool: Optional[Pool] = None
        self._dsn = settings.POSTGRES_DSN
        self._min_size = settings.DB_POOL_MIN_SIZE
        self._max_size = settings.DB_POOL_SIZE
        self._timeout = settings.DB_POOL_TIMEOUT
        self._command_timeout = settings.DB_COMMAND_TIMEOUT

    async def initialize(self) -> None:
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
                command_timeout=self._command_timeout,
                timeout=self._timeout,
                server_settings={
                    'application_name': settings.APP_NAME,
                    'statement_timeout': str(self._command_timeout * 1000),
                    'idle_in_transaction_session_timeout': '300000'  # 5 minutes
                }
            )
            logger.info("Database connection pool initialized")
            metrics.db_pool_created.inc()
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            metrics.db_pool_errors.inc()
            raise

    async def close(self) -> None:
        """Close connection pool"""
        if self.pool:
            try:
                await self.pool.close()
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")
                metrics.db_pool_errors.inc()
                raise

    async def get_connection(self) -> asyncpg.Connection:
        """Get database connection from pool"""
        if not self.pool:
            await self.initialize()
        
        try:
            conn = await self.pool.acquire()
            metrics.db_connections_active.inc()
            return conn
        except Exception as e:
            logger.error(f"Error acquiring connection: {e}")
            metrics.db_connection_errors.inc()
            raise

    async def release_connection(self, conn: asyncpg.Connection) -> None:
        """Release connection back to pool"""
        if self.pool:
            try:
                await self.pool.release(conn)
                metrics.db_connections_active.dec()
            except Exception as e:
                logger.error(f"Error releasing connection: {e}")
                metrics.db_connection_errors.inc()
                raise

    async def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        timeout: Optional[float] = None
    ) -> Any:
        """Execute single query"""
        async with self.pool.acquire() as conn:
            try:
                metrics.db_queries_total.inc()
                start_time = metrics.time()
                
                result = await conn.execute(
                    query,
                    *params if params else [],
                    timeout=timeout or self._command_timeout
                )
                
                metrics.db_query_duration.observe(metrics.time() - start_time)
                return result
            except Exception as e:
                logger.error(f"Query execution error: {e}")
                metrics.db_query_errors.inc()
                raise

    async def fetch_all(
        self,
        query: str,
        params: Optional[tuple] = None,
        timeout: Optional[float] = None
    ) -> list:
        """Fetch all rows"""
        async with self.pool.acquire() as conn:
            try:
                metrics.db_queries_total.inc()
                start_time = metrics.time()
                
                rows = await conn.fetch(
                    query,
                    *params if params else [],
                    timeout=timeout or self._command_timeout
                )
                
                metrics.db_query_duration.observe(metrics.time() - start_time)
                return rows
            except Exception as e:
                logger.error(f"Query fetch error: {e}")
                metrics.db_query_errors.inc()
                raise

    async def fetch_one(
        self,
        query: str,
        params: Optional[tuple] = None,
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        async with self.pool.acquire() as conn:
            try:
                metrics.db_queries_total.inc()
                start_time = metrics.time()
                
                row = await conn.fetchrow(
                    query,
                    *params if params else [],
                    timeout=timeout or self._command_timeout
                )
                
                metrics.db_query_duration.observe(metrics.time() - start_time)
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Query fetch error: {e}")
                metrics.db_query_errors.inc()
                raise

    async def execute_many(
        self,
        query: str,
        params: list,
        timeout: Optional[float] = None
    ) -> None:
        """Execute multiple queries"""
        async with self.pool.acquire() as conn:
            try:
                metrics.db_queries_total.inc()
                start_time = metrics.time()
                
                await conn.executemany(
                    query,
                    params,
                    timeout=timeout or self._command_timeout
                )
                
                metrics.db_query_duration.observe(metrics.time() - start_time)
            except Exception as e:
                logger.error(f"Batch execution error: {e}")
                metrics.db_query_errors.inc()
                raise

    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('SELECT 1')
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            metrics.db_health_check_errors.inc()
            return False

# Create global connection manager
connection_manager = ConnectionManager()
