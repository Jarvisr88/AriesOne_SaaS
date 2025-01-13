"""Redis cache implementation module."""
import json
from typing import Any, Optional
from datetime import timedelta
import aioredis
from pydantic import BaseModel

from core.interfaces.cache import ICache

class RedisCacheSettings(BaseModel):
    """Redis connection settings."""
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    POOL_SIZE: int = 10
    POOL_TIMEOUT: int = 30

class RedisCache(ICache):
    """Redis cache implementation."""

    def __init__(self, settings: Optional[RedisCacheSettings] = None):
        """Initialize Redis cache.
        
        Args:
            settings: Redis connection settings.
        """
        self.settings = settings or RedisCacheSettings()
        self.redis = aioredis.from_url(
            f"redis{'s' if self.settings.REDIS_SSL else ''}://"
            f"{self.settings.REDIS_HOST}:{self.settings.REDIS_PORT}",
            db=self.settings.REDIS_DB,
            password=self.settings.REDIS_PASSWORD,
            max_connections=self.settings.POOL_SIZE,
            timeout=self.settings.POOL_TIMEOUT,
            encoding="utf-8",
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[timedelta] = None
    ) -> None:
        """Set value in cache."""
        serialized = json.dumps(value)
        if expire:
            await self.redis.setex(key, int(expire.total_seconds()), serialized)
        else:
            await self.redis.set(key, serialized)

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return await self.redis.exists(key) > 0

    async def clear(self, pattern: str = "*") -> None:
        """Clear cache entries matching pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache."""
        return await self.redis.incrby(key, amount)

    async def get_or_set(
        self,
        key: str,
        factory: callable,
        expire: Optional[timedelta] = None
    ) -> Any:
        """Get value from cache or set if not exists."""
        value = await self.get(key)
        if value is None:
            value = await factory()
            await self.set(key, value, expire)
        return value

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache.
        
        Args:
            keys: List of cache keys.
            
        Returns:
            Dictionary of key-value pairs.
        """
        values = await self.redis.mget(keys)
        return {
            key: json.loads(value) if value else None
            for key, value in zip(keys, values)
        }

    async def set_many(
        self,
        mapping: dict[str, Any],
        expire: Optional[timedelta] = None
    ) -> None:
        """Set multiple values in cache.
        
        Args:
            mapping: Dictionary of key-value pairs.
            expire: Optional expiration time.
        """
        serialized = {
            key: json.dumps(value)
            for key, value in mapping.items()
        }
        
        pipeline = self.redis.pipeline()
        pipeline.mset(serialized)
        
        if expire:
            for key in mapping:
                pipeline.expire(key, int(expire.total_seconds()))
        
        await pipeline.execute()

    async def delete_many(self, keys: list[str]) -> None:
        """Delete multiple values from cache.
        
        Args:
            keys: List of cache keys.
        """
        if keys:
            await self.redis.delete(*keys)
