from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import Generator, AsyncGenerator
from functools import wraps
import time
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create sync engine with connection pooling
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
    pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
    pool_recycle=settings.POSTGRES_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.SQL_ECHO,
)

# Create async engine
async_engine = create_async_engine(
    settings.ASYNC_SQLALCHEMY_DATABASE_URI,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
    pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
    pool_recycle=settings.POSTGRES_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.SQL_ECHO,
)

# Create session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=False
)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Get a database session for synchronous operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for asynchronous operations."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def with_db_retry(max_retries: int = 3, delay: float = 0.1):
    """Decorator for retrying database operations."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"Database operation failed, retrying in {wait_time}s. "
                            f"Error: {str(e)}"
                        )
                        time.sleep(wait_time)
            logger.error(f"Database operation failed after {max_retries} attempts")
            raise last_error

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"Database operation failed, retrying in {wait_time}s. "
                            f"Error: {str(e)}"
                        )
                        time.sleep(wait_time)
            logger.error(f"Database operation failed after {max_retries} attempts")
            raise last_error

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class DatabaseStats:
    """Track database connection and query statistics."""
    def __init__(self):
        self.query_count = 0
        self.slow_query_threshold = settings.SLOW_QUERY_THRESHOLD
        self.slow_queries = []
        self.connection_count = 0
        self.peak_connection_count = 0
        self.total_query_time = 0

    def record_query(self, query: str, duration: float):
        """Record query execution statistics."""
        self.query_count += 1
        self.total_query_time += duration

        if duration >= self.slow_query_threshold:
            self.slow_queries.append({
                'query': query,
                'duration': duration,
                'timestamp': time.time()
            })
            # Keep only recent slow queries
            self.slow_queries = self.slow_queries[-100:]

    def record_connection(self, opened: bool):
        """Record connection pool statistics."""
        if opened:
            self.connection_count += 1
            self.peak_connection_count = max(
                self.peak_connection_count,
                self.connection_count
            )
        else:
            self.connection_count -= 1

    def get_stats(self):
        """Get current database statistics."""
        return {
            'query_count': self.query_count,
            'slow_queries': len(self.slow_queries),
            'avg_query_time': (
                self.total_query_time / self.query_count
                if self.query_count > 0 else 0
            ),
            'connection_count': self.connection_count,
            'peak_connection_count': self.peak_connection_count,
        }

db_stats = DatabaseStats()

@event.listens_for(engine, 'before_cursor_execute')
def before_cursor_execute(
    conn, cursor, statement,
    parameters, context, executemany
):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(engine, 'after_cursor_execute')
def after_cursor_execute(
    conn, cursor, statement,
    parameters, context, executemany
):
    total_time = time.time() - conn.info['query_start_time'].pop()
    db_stats.record_query(statement, total_time)

@event.listens_for(engine, 'checkout')
def receive_checkout(dbapi_conn, conn_record, conn_proxy):
    db_stats.record_connection(opened=True)

@event.listens_for(engine, 'checkin')
def receive_checkin(dbapi_conn, conn_record):
    db_stats.record_connection(opened=False)
