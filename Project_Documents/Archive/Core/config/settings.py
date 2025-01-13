"""
Configuration management system.
"""
from functools import lru_cache
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AriesOne SaaS"
    VERSION: str = "1.0.0"
    OPENAPI_URL: str = f"{API_V1_STR}/openapi.json"
    
    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[PostgresDsn] = None
    TEST_DATABASE_URL: Optional[PostgresDsn] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Assemble database URL from components"""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @validator("TEST_DATABASE_URL", pre=True)
    def assemble_test_db_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Assemble test database URL"""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB')}_test",
        )
    
    # Security Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = []
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # File Storage Settings
    STORAGE_BACKEND: str = "local"  # or "s3", "azure", etc.
    STORAGE_ROOT: str = "storage"
    
    class Config:
        """Pydantic config"""
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
