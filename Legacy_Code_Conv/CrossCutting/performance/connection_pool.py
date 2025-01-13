"""Database connection pool module."""

from typing import Optional, Dict, Any
from contextlib import contextmanager
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from app.core.config import settings

class ConnectionPool:
    """Pool for database connections."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection pool."""
        if not hasattr(self, 'engine'):
            self.engine = create_engine(
                settings.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True
            )
            
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            self.scoped_session = scoped_session(self.session_factory)
    
    @contextmanager
    def get_session(self):
        """Get database session from pool."""
        session = self.scoped_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return {
            'pool_size': self.engine.pool.size(),
            'checkedin': self.engine.pool.checkedin(),
            'checkedout': self.engine.pool.checkedout(),
            'overflow': self.engine.pool.overflow(),
            'checkedout_overflow': self.engine.pool.overflow_checkedout(),
        }
    
    def dispose(self) -> None:
        """Dispose of connection pool."""
        self.engine.dispose()

class AsyncConnectionPool:
    """Pool for async database connections."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize async connection pool."""
        if not hasattr(self, 'engine'):
            from sqlalchemy.ext.asyncio import create_async_engine
            
            self.engine = create_async_engine(
                settings.ASYNC_DATABASE_URL,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True
            )
            
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy.orm import sessionmaker
            
            self.async_session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
    
    @contextmanager
    async def get_session(self):
        """Get async database session from pool."""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get async connection pool statistics."""
        return {
            'pool_size': self.engine.pool.size(),
            'checkedin': self.engine.pool.checkedin(),
            'checkedout': self.engine.pool.checkedout(),
            'overflow': self.engine.pool.overflow(),
            'checkedout_overflow': self.engine.pool.overflow_checkedout(),
        }
    
    async def dispose(self) -> None:
        """Dispose of async connection pool."""
        await self.engine.dispose()
