"""
Configuration settings for image processing module.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-west-2"
    AWS_BUCKET_NAME: str
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Image Processing
    MAX_IMAGE_SIZE: tuple[int, int] = (1920, 1080)
    JPEG_QUALITY: int = 85
    ALLOWED_EXTENSIONS: set[str] = {
        "jpg", "jpeg", "png", "gif", "webp"
    }
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # CDN Configuration
    CDN_BASE_URL: str
    
    # Cache Configuration
    CACHE_TTL: int = 86400  # 24 hours
    
    # Security
    CONTENT_SECURITY_POLICY: str = """
        default-src 'self';
        img-src 'self' data: https:;
        style-src 'self' 'unsafe-inline';
        font-src 'self';
        object-src 'none';
    """.strip()
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
