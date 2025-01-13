"""Database configuration module for AriesOne SaaS platform."""

from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # PostgreSQL settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = ""
    DB_DATABASE: str = "ariesone"
    DB_SSL: bool = False
    DB_POOL_SIZE: int = 20
    DB_POOL_OVERFLOW: int = 10
    DB_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 300
    DB_ECHO: bool = False
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_SSL: bool = False
    
    # Cache settings
    CACHE_TTL: int = 300  # 5 minutes
    
    class Config:
        """Pydantic configuration class."""
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Get the database URL for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
        )
    
    @property
    def redis_url(self) -> str:
        """Get the Redis URL."""
        protocol = "rediss" if self.REDIS_SSL else "redis"
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"{protocol}://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_pool_settings(self) -> Dict[str, Any]:
        """Get database pool settings."""
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_POOL_OVERFLOW,
            "pool_timeout": self.DB_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
            "pool_pre_ping": True,
            "echo": self.DB_ECHO,
            "ssl": self.DB_SSL
        }


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """Get cached database settings instance."""
    return DatabaseSettings()
