"""Database configuration module.

This module provides configuration settings for the database connection,
including connection pooling, SSL/TLS, and other PostgreSQL-specific settings.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration settings.
    
    Attributes:
        POSTGRES_USER: Database username
        POSTGRES_PASSWORD: Database password
        POSTGRES_HOST: Database host
        POSTGRES_PORT: Database port
        POSTGRES_DB: Database name
        POSTGRES_SCHEMA: Database schema
        POOL_SIZE: Connection pool size
        MAX_OVERFLOW: Maximum number of connections
        POOL_TIMEOUT: Connection timeout in seconds
        POOL_RECYCLE: Connection recycle time in seconds
        SSL_MODE: SSL mode (disable, allow, prefer, require, verify-ca, verify-full)
        SSL_CERT: Path to SSL certificate
        SSL_KEY: Path to SSL key
        SSL_ROOT_CERT: Path to SSL root certificate
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # Connection settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_SCHEMA: str = "public"
    
    # Pool settings
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    
    # SSL settings
    SSL_MODE: str = "prefer"
    SSL_CERT: Optional[str] = None
    SSL_KEY: Optional[str] = None
    SSL_ROOT_CERT: Optional[str] = None
    
    @property
    def async_database_url(self) -> str:
        """Get async database URL with SSL if configured."""
        url = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        
        # Add SSL parameters if enabled
        if self.SSL_MODE != "disable":
            url += f"?sslmode={self.SSL_MODE}"
            if self.SSL_CERT:
                url += f"&sslcert={self.SSL_CERT}"
            if self.SSL_KEY:
                url += f"&sslkey={self.SSL_KEY}"
            if self.SSL_ROOT_CERT:
                url += f"&sslrootcert={self.SSL_ROOT_CERT}"
        
        return url
    
    @property
    def pool_args(self) -> dict:
        """Get connection pool arguments."""
        return {
            "pool_size": self.POOL_SIZE,
            "max_overflow": self.MAX_OVERFLOW,
            "pool_timeout": self.POOL_TIMEOUT,
            "pool_recycle": self.POOL_RECYCLE
        }


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """Get cached database settings.
    
    Returns:
        DatabaseSettings: Cached database configuration
    """
    return DatabaseSettings()
