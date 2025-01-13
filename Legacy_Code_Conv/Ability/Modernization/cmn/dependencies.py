"""
CMN Dependencies Module

This module provides dependency injection for the CMN module.
"""
from functools import lru_cache
from typing import AsyncGenerator, Optional

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from .config import CmnSettings, get_settings
from .services.cmn_service import CmnService
from .repositories.cmn_repository import CmnRepository
from .utils.medicare_client import MedicareClient
from .utils.monitoring import (
    get_logger,
    init_monitoring,
    init_tracing
)

# Initialize settings
settings = get_settings()

# Initialize Azure Key Vault
credential = DefaultAzureCredential()
key_vault = SecretClient(
    vault_url=settings.AZURE_VAULT_URL,
    credential=credential
)

# Initialize database
engine = create_async_engine(
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
    echo=True,
    pool_size=settings.MAX_CONNECTIONS,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    statement_cache_size=settings.STATEMENT_CACHE_SIZE
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

# Initialize API key security
api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER)

# Initialize monitoring
logger = get_logger(__name__)
init_monitoring(settings)
init_tracing(settings)

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

async def get_key_vault() -> SecretClient:
    """Get Azure Key Vault client."""
    return key_vault

@lru_cache
def get_cmn_repository() -> CmnRepository:
    """Get CMN repository instance."""
    return CmnRepository()

@lru_cache
def get_medicare_client() -> MedicareClient:
    """Get Medicare client instance."""
    return MedicareClient(settings)

def get_cmn_service(
    repository: CmnRepository = Depends(get_cmn_repository),
    medicare_client: MedicareClient = Depends(get_medicare_client),
    redis: Redis = Depends(get_redis),
    logger = logger
) -> CmnService:
    """Get CMN service instance."""
    return CmnService(
        repository=repository,
        medicare_client=medicare_client,
        cache_service=redis,
        logger=logger
    )

async def verify_api_key(
    api_key: str = Security(api_key_header),
    key_vault: SecretClient = Depends(get_key_vault)
) -> str:
    """Verify API key."""
    try:
        valid_key = key_vault.get_secret("api-key").value
        if api_key == valid_key:
            return api_key
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    except Exception as e:
        logger.error(f"API key verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )

async def get_current_user(
    api_key: str = Security(verify_api_key)
) -> dict:
    """Get current user from API key."""
    # Implement user lookup based on API key
    return {"api_key": api_key}
