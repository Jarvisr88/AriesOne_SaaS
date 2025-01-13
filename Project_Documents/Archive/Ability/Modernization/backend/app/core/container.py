from typing import AsyncGenerator, Callable, Dict, Optional, Type
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import async_session
from app.core.unit_of_work import UnitOfWork, get_uow
from app.repositories.base import BaseRepository
from app.core.logging import logger

class Container:
    """Dependency Injection Container"""
    
    def __init__(self):
        self._repositories: Dict[str, Type[BaseRepository]] = {}
        self._services: Dict[str, Callable] = {}
        self._session_factory = async_session

    def register_repository(
        self,
        name: str,
        repository_class: Type[BaseRepository]
    ) -> None:
        """Register a repository"""
        self._repositories[name] = repository_class

    def register_service(
        self,
        name: str,
        service_factory: Callable
    ) -> None:
        """Register a service"""
        self._services[name] = service_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self._session_factory() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Session error: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_repository(
        self,
        name: str,
        session: AsyncSession
    ) -> Optional[BaseRepository]:
        """Get repository instance"""
        try:
            repository_class = self._repositories.get(name)
            if repository_class:
                return repository_class(session)
            return None
        except Exception as e:
            logger.error(f"Error getting repository {name}: {e}")
            raise

    async def get_service(
        self,
        name: str,
        **kwargs
    ) -> Optional[Any]:
        """Get service instance"""
        try:
            service_factory = self._services.get(name)
            if service_factory:
                return service_factory(**kwargs)
            return None
        except Exception as e:
            logger.error(f"Error getting service {name}: {e}")
            raise

    async def get_uow(self) -> AsyncGenerator[UnitOfWork, None]:
        """Get unit of work instance"""
        async with get_uow() as uow:
            yield uow

# Create container instance
container = Container()

# Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in container.get_session():
        yield session

# Unit of work dependency
async def get_unit_of_work() -> AsyncGenerator[UnitOfWork, None]:
    async for uow in container.get_uow():
        yield uow

# Repository dependencies
def get_repository(name: str):
    async def _get_repository(
        session: AsyncSession = Depends(get_db)
    ) -> BaseRepository:
        return await container.get_repository(name, session)
    return _get_repository

# Service dependencies
def get_service(name: str, **kwargs):
    async def _get_service() -> Any:
        return await container.get_service(name, **kwargs)
    return _get_service

# Connection pool configuration
def configure_connection_pool():
    """Configure database connection pool"""
    engine_args = {
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True
    }
    return engine_args
