from typing import Dict, Any, Optional, List
import os
import json
import yaml
from datetime import datetime
from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from fastapi.security import OAuth2PasswordBearer
from app.core.logging import logger
from app.core.monitoring import metrics

class SecurityConfig(BaseModel):
    """Security configuration settings"""
    secret_key: str = Field(..., min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    oauth2_scheme: OAuth2PasswordBearer = Field(
        default_factory=lambda: OAuth2PasswordBearer(tokenUrl="token")
    )

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Secret key must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Secret key must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Secret key must contain at least one number")
        return v

class DatabaseConfig(BaseModel):
    """Database configuration settings"""
    url: str
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False

class RedisConfig(BaseModel):
    """Redis configuration settings"""
    url: str
    pool_size: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True

class CDNConfig(BaseModel):
    """CDN configuration settings"""
    provider: str
    region: str
    bucket: str
    access_key: Optional[str]
    secret_key: Optional[str]
    max_file_size: int = 100 * 1024 * 1024  # 100MB

class ProcessingConfig(BaseModel):
    """Processing configuration settings"""
    max_batch_size: int = 100
    timeout_seconds: int = 300
    max_retries: int = 3
    supported_formats: List[str] = []
    quality_threshold: float = 0.8

class MonitoringConfig(BaseModel):
    """Monitoring configuration settings"""
    enabled: bool = True
    interval_seconds: int = 60
    retention_days: int = 30
    alert_threshold: float = 0.9

class AppConfig(BaseModel):
    """Main application configuration"""
    env: str = "development"
    debug: bool = False
    version: str
    security: SecurityConfig
    database: DatabaseConfig
    redis: RedisConfig
    cdn: List[CDNConfig]
    processing: ProcessingConfig
    monitoring: MonitoringConfig

class ConfigManager:
    def __init__(self):
        self.config: Optional[AppConfig] = None
        self.redis_client: Optional[redis.Redis] = None
        self._setup_monitoring()
        self._load_config()
        self._setup_redis()

    def _setup_monitoring(self):
        """Setup monitoring metrics"""
        self.metrics = {
            "config_updates": metrics.config_updates,
            "config_errors": metrics.config_errors,
            "validation_errors": metrics.config_validation_errors,
            "cache_hits": metrics.config_cache_hits,
            "cache_misses": metrics.config_cache_misses
        }

    def _load_config(self):
        """Load configuration from various sources"""
        try:
            # Load base config from YAML
            base_config = self._load_yaml_config()

            # Override with environment variables
            env_config = self._load_env_config()
            base_config.update(env_config)

            # Validate configuration
            self.config = AppConfig(**base_config)
            
            # Track configuration update
            self.metrics["config_updates"].inc()
            
        except Exception as e:
            logger.error(f"Configuration loading error: {e}")
            self.metrics["config_errors"].inc()
            raise

    def _load_yaml_config(self) -> Dict:
        """Load configuration from YAML file"""
        config_path = os.getenv(
            "APP_CONFIG_PATH",
            "config/config.yaml"
        )
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"YAML config loading error: {e}")
            return {}

    def _load_env_config(self) -> Dict:
        """Load configuration from environment variables"""
        config = {}
        prefix = "APP_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                try:
                    # Try to parse as JSON for complex values
                    config[config_key] = json.loads(value)
                except json.JSONDecodeError:
                    config[config_key] = value
                    
        return config

    async def _setup_redis(self):
        """Setup Redis connection"""
        if not self.config:
            return

        try:
            self.redis_client = redis.Redis.from_url(
                self.config.redis.url,
                decode_responses=True
            )
            await self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis connection error: {e}")

    async def get_config(self, key: str) -> Any:
        """Get configuration value with caching"""
        try:
            # Try to get from Redis cache
            if self.redis_client:
                cached = await self.redis_client.get(f"config:{key}")
                if cached:
                    self.metrics["cache_hits"].inc()
                    return json.loads(cached)
                self.metrics["cache_misses"].inc()

            # Get from config object
            value = self._get_nested_attr(self.config, key)
            
            # Cache in Redis
            if self.redis_client and value is not None:
                await self.redis_client.set(
                    f"config:{key}",
                    json.dumps(value),
                    ex=3600  # 1 hour
                )
                
            return value
            
        except Exception as e:
            logger.error(f"Config retrieval error: {e}")
            raise

    async def set_config(self, key: str, value: Any):
        """Set configuration value with validation"""
        try:
            # Validate new value
            self._validate_config_value(key, value)
            
            # Update config object
            self._set_nested_attr(self.config, key, value)
            
            # Update Redis cache
            if self.redis_client:
                await self.redis_client.set(
                    f"config:{key}",
                    json.dumps(value),
                    ex=3600
                )
                
            self.metrics["config_updates"].inc()
            
        except Exception as e:
            logger.error(f"Config update error: {e}")
            self.metrics["validation_errors"].inc()
            raise

    def _get_nested_attr(self, obj: Any, path: str) -> Any:
        """Get nested attribute using dot notation"""
        attrs = path.split('.')
        for attr in attrs:
            if hasattr(obj, attr):
                obj = getattr(obj, attr)
            else:
                return None
        return obj

    def _set_nested_attr(self, obj: Any, path: str, value: Any):
        """Set nested attribute using dot notation"""
        attrs = path.split('.')
        for i, attr in enumerate(attrs[:-1]):
            if not hasattr(obj, attr):
                setattr(obj, attr, BaseModel())
            obj = getattr(obj, attr)
        setattr(obj, attrs[-1], value)

    def _validate_config_value(self, key: str, value: Any):
        """Validate configuration value"""
        try:
            # Get parent model class
            parent_path = '.'.join(key.split('.')[:-1])
            parent = self._get_nested_attr(self.config, parent_path)
            
            if parent and isinstance(parent, BaseModel):
                # Create temporary model for validation
                temp_dict = parent.dict()
                temp_dict[key.split('.')[-1]] = value
                type(parent)(**temp_dict)
        except Exception as e:
            raise ValueError(f"Invalid configuration value: {e}")

    async def get_metrics(self) -> Dict:
        """Get configuration metrics"""
        return {
            "updates": self.metrics["config_updates"]._value.get(),
            "errors": self.metrics["config_errors"]._value.get(),
            "validation_errors": self.metrics["validation_errors"]._value.get(),
            "cache_hits": self.metrics["cache_hits"]._value.get(),
            "cache_misses": self.metrics["cache_misses"]._value.get()
        }

# Create global configuration manager
config_manager = ConfigManager()
