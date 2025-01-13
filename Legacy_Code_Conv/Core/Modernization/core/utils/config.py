"""
Core Configuration Utility Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides configuration management utilities.
"""
from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import BaseSettings, Field


class CoreSettings(BaseSettings):
    """Core module configuration settings."""
    
    # Database Settings
    DB_HOST: str = Field(..., env='DB_HOST')
    DB_PORT: int = Field(5432, env='DB_PORT')
    DB_NAME: str = Field(..., env='DB_NAME')
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASSWORD: str = Field(..., env='DB_PASSWORD')
    DB_POOL_SIZE: int = Field(20, env='DB_POOL_SIZE')
    DB_MAX_OVERFLOW: int = Field(10, env='DB_MAX_OVERFLOW')
    
    # Security Settings
    SECRET_KEY: str = Field(..., env='SECRET_KEY')
    ALGORITHM: str = Field('HS256', env='ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env='ACCESS_TOKEN_EXPIRE_MINUTES')
    
    # Cache Settings
    REDIS_HOST: str = Field('localhost', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')
    REDIS_DB: int = Field(0, env='REDIS_DB')
    CACHE_TTL: int = Field(3600, env='CACHE_TTL')
    
    # Event Settings
    EVENT_STORE_URL: str = Field(..., env='EVENT_STORE_URL')
    EVENT_BATCH_SIZE: int = Field(100, env='EVENT_BATCH_SIZE')
    EVENT_FLUSH_INTERVAL: int = Field(60, env='EVENT_FLUSH_INTERVAL')
    
    # Logging Settings
    LOG_LEVEL: str = Field('INFO', env='LOG_LEVEL')
    LOG_FORMAT: str = Field('json', env='LOG_FORMAT')
    LOG_FILE: Optional[str] = Field(None, env='LOG_FILE')
    
    class Config:
        """Pydantic model configuration."""
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache()
def get_settings() -> CoreSettings:
    """Get cached settings instance."""
    return CoreSettings()
