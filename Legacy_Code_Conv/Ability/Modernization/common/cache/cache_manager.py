"""
Caching Infrastructure

Provides a unified caching system with support for multiple backends.
"""
from datetime import datetime, timedelta
from functools import wraps
import json
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union
import aioredis
from fastapi import FastAPI
from pydantic import BaseModel

from ..config import get_settings
from ..monitoring.logger import get_logger
from ..errors.error_handler import TechnicalError

settings = get_settings()
logger = get_logger(__name__)

T = TypeVar("T")

class CacheConfig(BaseModel):
    """Cache configuration."""
    ttl: int = 3600  # Default TTL in seconds
    prefix: str = ""
    namespace: str = ""
    serializer: str = "json"  # json or pickle

class CacheManager:
    """Manages caching operations."""
    
    def __init__(self, app: Optional[FastAPI] = None):
        """Initialize cache manager."""
        self.redis: Optional[aioredis.Redis] = None
        if app:
            self.init_app(app)

    async def init_app(self, app: FastAPI):
        """
        Initialize cache with FastAPI app.
        
        Args:
            app: FastAPI application
        """
        try:
            self.redis = await aioredis.create_redis_pool(
                settings.REDIS_URL,
                minsize=5,
                maxsize=10,
                encoding='utf-8'
            )
            
            @app.on_event("shutdown")
            async def shutdown_cache():
                """Cleanup cache connections."""
                if self.redis:
                    self.redis.close()
                    await self.redis.wait_closed()
                    
        except Exception as e:
            logger.error(f"Failed to initialize cache: {str(e)}")
            raise TechnicalError(
                "Failed to initialize cache",
                {"error": str(e)}
            )

    def _build_key(
        self,
        key: str,
        config: CacheConfig
    ) -> str:
        """
        Build cache key.
        
        Args:
            key: Base key
            config: Cache configuration
            
        Returns:
            Full cache key
        """
        parts = []
        if config.prefix:
            parts.append(config.prefix)
        if config.namespace:
            parts.append(config.namespace)
        parts.append(key)
        return ":".join(parts)

    def _serialize(
        self,
        value: Any,
        config: CacheConfig
    ) -> str:
        """
        Serialize value for caching.
        
        Args:
            value: Value to serialize
            config: Cache configuration
            
        Returns:
            Serialized value
        """
        if config.serializer == "json":
            if isinstance(value, BaseModel):
                return value.json()
            return json.dumps(value)
        raise ValueError(f"Unsupported serializer: {config.serializer}")

    def _deserialize(
        self,
        value: str,
        target_type: Optional[Type[T]] = None,
        config: CacheConfig = CacheConfig()
    ) -> Any:
        """
        Deserialize cached value.
        
        Args:
            value: Value to deserialize
            target_type: Optional target type
            config: Cache configuration
            
        Returns:
            Deserialized value
        """
        if config.serializer == "json":
            data = json.loads(value)
            if target_type and issubclass(target_type, BaseModel):
                return target_type.parse_raw(value)
            return data
        raise ValueError(f"Unsupported serializer: {config.serializer}")

    async def get(
        self,
        key: str,
        target_type: Optional[Type[T]] = None,
        config: CacheConfig = CacheConfig()
    ) -> Optional[T]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            target_type: Optional target type
            config: Cache configuration
            
        Returns:
            Cached value if exists
        """
        try:
            if not self.redis:
                raise TechnicalError("Cache not initialized")
                
            full_key = self._build_key(key, config)
            value = await self.redis.get(full_key)
            
            if value:
                return self._deserialize(value, target_type, config)
            return None
            
        except Exception as e:
            logger.error(f"Cache get failed: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        config: CacheConfig = CacheConfig()
    ):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override
            config: Cache configuration
        """
        try:
            if not self.redis:
                raise TechnicalError("Cache not initialized")
                
            full_key = self._build_key(key, config)
            serialized = self._serialize(value, config)
            
            await self.redis.set(
                full_key,
                serialized,
                expire=ttl or config.ttl
            )
            
        except Exception as e:
            logger.error(f"Cache set failed: {str(e)}")

    async def delete(
        self,
        key: str,
        config: CacheConfig = CacheConfig()
    ):
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            config: Cache configuration
        """
        try:
            if not self.redis:
                raise TechnicalError("Cache not initialized")
                
            full_key = self._build_key(key, config)
            await self.redis.delete(full_key)
            
        except Exception as e:
            logger.error(f"Cache delete failed: {str(e)}")

    async def exists(
        self,
        key: str,
        config: CacheConfig = CacheConfig()
    ) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            config: Cache configuration
            
        Returns:
            True if key exists
        """
        try:
            if not self.redis:
                raise TechnicalError("Cache not initialized")
                
            full_key = self._build_key(key, config)
            return await self.redis.exists(full_key)
            
        except Exception as e:
            logger.error(f"Cache exists check failed: {str(e)}")
            return False

    async def clear(
        self,
        pattern: str = "*",
        config: CacheConfig = CacheConfig()
    ):
        """
        Clear cache entries matching pattern.
        
        Args:
            pattern: Key pattern
            config: Cache configuration
        """
        try:
            if not self.redis:
                raise TechnicalError("Cache not initialized")
                
            pattern = self._build_key(pattern, config)
            keys = await self.redis.keys(pattern)
            
            if keys:
                await self.redis.delete(*keys)
                
        except Exception as e:
            logger.error(f"Cache clear failed: {str(e)}")

def cached(
    key_pattern: str,
    ttl: Optional[int] = None,
    config: Optional[CacheConfig] = None
):
    """
    Cache decorator.
    
    Args:
        key_pattern: Cache key pattern
        ttl: Optional TTL override
        config: Optional cache configuration
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = cache_manager
            if not cache:
                return await func(*args, **kwargs)
                
            # Build cache key
            key = key_pattern.format(*args, **kwargs)
            cfg = config or CacheConfig()
            if ttl:
                cfg.ttl = ttl
                
            # Try to get from cache
            result = await cache.get(key, config=cfg)
            if result is not None:
                return result
                
            # Get fresh value
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache.set(key, result, config=cfg)
            return result
            
        return wrapper
    return decorator

cache_manager: Optional[CacheManager] = None

def setup_cache(app: FastAPI) -> CacheManager:
    """
    Setup cache for application.
    
    Args:
        app: FastAPI application
        
    Returns:
        Cache manager instance
    """
    global cache_manager
    if not cache_manager:
        cache_manager = CacheManager(app)
    return cache_manager

def get_cache() -> CacheManager:
    """
    Get cache manager instance.
    
    Returns:
        Cache manager instance
    """
    if not cache_manager:
        raise RuntimeError("Cache not initialized")
    return cache_manager
