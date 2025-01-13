"""
Cache Module

This module provides caching utilities.
"""
from typing import Any, Optional
from redis.asyncio import Redis

class CacheService:
    """Service for Redis caching operations."""

    def __init__(self, redis: Redis, ttl: int = 3600):
        """
        Initialize cache service.
        
        Args:
            redis: Redis client
            ttl: Default TTL in seconds
        """
        self.redis = redis
        self.default_ttl = ttl

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value if found
        """
        return await self.redis.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Optional TTL in seconds
        """
        await self.redis.set(
            key,
            value,
            ex=expire or self.default_ttl
        )

    async def delete(self, key: str) -> None:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        """
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
        
        Returns:
            bool indicating if key exists
        """
        return await self.redis.exists(key)

    async def increment(
        self,
        key: str,
        amount: int = 1
    ) -> int:
        """
        Increment counter in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment
        
        Returns:
            New counter value
        """
        return await self.redis.incr(key, amount)

    async def expire(
        self,
        key: str,
        seconds: int
    ) -> None:
        """
        Set key expiration.
        
        Args:
            key: Cache key
            seconds: TTL in seconds
        """
        await self.redis.expire(key, seconds)

    async def clear_pattern(
        self,
        pattern: str
    ) -> None:
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern to match
        """
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
