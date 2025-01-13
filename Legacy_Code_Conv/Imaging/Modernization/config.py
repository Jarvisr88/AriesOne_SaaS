"""
Configuration settings for the imaging service.
"""
from typing import Set
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-west-2"
    AWS_BUCKET_NAME: str
    AWS_CLOUDFRONT_DOMAIN: str
    
    # Storage Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: Set[str] = {
        "jpg", "jpeg", "png", "gif", "webp", "tiff"
    }
    IMAGE_QUALITY: int = 85
    MAX_IMAGE_SIZE: tuple[int, int] = (4096, 4096)
    THUMBNAIL_SIZES: dict[str, tuple[int, int]] = {
        "small": (150, 150),
        "medium": (300, 300),
        "large": (600, 600)
    }
    
    # Cache Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    CACHE_TTL: int = 3600  # 1 hour
    
    # Security Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AriesOne Imaging Service"
    DEBUG: bool = False
    
    # Backup Configuration
    BACKUP_ENABLED: bool = True
    BACKUP_BUCKET: str
    BACKUP_RETENTION_DAYS: int = 30
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
