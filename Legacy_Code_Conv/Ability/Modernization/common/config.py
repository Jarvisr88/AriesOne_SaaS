"""
Common Configuration Module

This module provides configuration settings for the Common module.
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class CommonSettings(BaseSettings):
    """Common module settings."""
    
    # Application
    APP_NAME: str = Field("AriesOne", description="Application name")
    APP_VERSION: str = Field("1.0.0", description="Application version")
    DEBUG: bool = Field(False, description="Debug mode")
    
    # Database
    POSTGRES_USER: str = Field(..., description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL password")
    POSTGRES_HOST: str = Field(..., description="PostgreSQL host")
    POSTGRES_PORT: int = Field(5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(..., description="PostgreSQL database name")
    
    # Redis
    REDIS_HOST: str = Field(..., description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password")
    
    # Azure
    AZURE_STORAGE_CONNECTION_STRING: str = Field(..., description="Azure Storage connection string")
    AZURE_CONTAINER_NAME: str = Field(..., description="Azure container name")
    
    # Security
    SECRET_KEY: str = Field(..., description="Secret key")
    ALGORITHM: str = Field("HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="Token expiry time")
    
    # CORS
    ALLOWED_ORIGINS: list[str] = Field(
        ["*"],
        description="Allowed CORS origins"
    )
    ALLOWED_METHODS: list[str] = Field(
        ["*"],
        description="Allowed CORS methods"
    )
    ALLOWED_HEADERS: list[str] = Field(
        ["*"],
        description="Allowed CORS headers"
    )
    
    # Logging
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # Performance
    CACHE_TTL: int = Field(3600, description="Cache TTL in seconds")
    MAX_CONNECTIONS: int = Field(10, description="Max DB connections")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(
        10 * 1024 * 1024,
        description="Maximum file upload size in bytes"
    )
    ALLOWED_EXTENSIONS: list[str] = Field(
        ["pdf", "jpg", "jpeg", "png"],
        description="Allowed file extensions"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache
def get_settings() -> CommonSettings:
    """Get cached settings instance."""
    return CommonSettings()
