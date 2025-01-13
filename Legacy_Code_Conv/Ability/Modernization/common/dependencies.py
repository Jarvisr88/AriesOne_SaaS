"""
Common Dependencies Module

This module provides dependency injection for the Common module.
"""
from functools import lru_cache
from typing import AsyncGenerator

from azure.storage.blob.aio import BlobServiceClient
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from .config import CommonSettings, get_settings
from .services.application_service import ApplicationService
from .services.error_service import ErrorService
from .services.file_service import FileService
from .repositories.application_repository import ApplicationRepository
from .repositories.error_repository import ErrorRepository
from .repositories.file_repository import FileRepository
from .utils.monitoring import get_logger

# Initialize settings
settings = get_settings()

# Initialize database
engine = create_async_engine(
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
    echo=settings.DEBUG,
    pool_size=settings.MAX_CONNECTIONS,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Initialize Redis
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

# Initialize Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(
    settings.AZURE_STORAGE_CONNECTION_STRING
)

# Initialize logger
logger = get_logger(__name__)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis() -> Redis:
    """Get Redis connection."""
    return redis

async def get_blob_service() -> BlobServiceClient:
    """Get Azure Blob service client."""
    return blob_service_client

@lru_cache
def get_application_repository() -> ApplicationRepository:
    """Get application repository instance."""
    return ApplicationRepository()

@lru_cache
def get_error_repository() -> ErrorRepository:
    """Get error repository instance."""
    return ErrorRepository()

@lru_cache
def get_file_repository() -> FileRepository:
    """Get file repository instance."""
    return FileRepository()

def get_application_service(
    repository: ApplicationRepository = Depends(get_application_repository),
    redis: Redis = Depends(get_redis),
    logger = logger
) -> ApplicationService:
    """Get application service instance."""
    return ApplicationService(
        repository=repository,
        cache_service=redis,
        logger=logger
    )

def get_error_service(
    repository: ErrorRepository = Depends(get_error_repository),
    redis: Redis = Depends(get_redis),
    logger = logger
) -> ErrorService:
    """Get error service instance."""
    return ErrorService(
        repository=repository,
        cache_service=redis,
        logger=logger
    )

def get_file_service(
    repository: FileRepository = Depends(get_file_repository),
    blob_service: BlobServiceClient = Depends(get_blob_service),
    logger = logger
) -> FileService:
    """Get file service instance."""
    return FileService(
        repository=repository,
        blob_service=blob_service,
        container_name=settings.AZURE_CONTAINER_NAME,
        max_size=settings.MAX_UPLOAD_SIZE,
        allowed_extensions=settings.ALLOWED_EXTENSIONS,
        logger=logger
    )
