"""Application settings module."""

from typing import Any, Dict, List, Optional
from pydantic import BaseSettings, PostgresDsn, validator
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    PROJECT_NAME: str = "AriesOne SaaS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Assemble database connection URI."""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: Optional[str] = None
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = None
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    # Feature Flags
    ENABLE_DOCS: bool = False
    ENABLE_OCR: bool = True
    ENABLE_BATCH_PROCESSING: bool = True
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"pdf", "png", "jpg", "jpeg"}
    
    # API Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 1 minute
    
    class Config:
        """Pydantic config."""
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
