from typing import Any, Optional, List
import json
from datetime import timedelta
import asyncio
from redis import Redis
from fastapi import HTTPException
from app.core.config import settings

class CacheManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = settings.CACHE_TTL
        self.prefix = "cache:"

    def _get_key(self, key: str) -> str:
        """Add prefix to cache key"""
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(self._get_key(key))
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            # Log error but don't fail the request
            print(f"Cache get error: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        try:
            serialized = json.dumps(value)
            return self.redis.setex(
                self._get_key(key),
                ttl or self.default_ttl,
                serialized
            )
        except Exception as e:
            print(f"Cache set error: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.redis.delete(self._get_key(key)))
        except Exception as e:
            print(f"Cache delete error: {str(e)}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis.keys(self._get_key(pattern))
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {str(e)}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis.exists(self._get_key(key)))
        except Exception as e:
            print(f"Cache exists error: {str(e)}")
            return False

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in cache"""
        try:
            return self.redis.incrby(self._get_key(key), amount)
        except Exception as e:
            print(f"Cache increment error: {str(e)}")
            return 0

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement value in cache"""
        try:
            return self.redis.decrby(self._get_key(key), amount)
        except Exception as e:
            print(f"Cache decrement error: {str(e)}")
            return 0

class MultiLevelCache:
    """Multi-level cache with local memory and Redis"""
    
    def __init__(
        self,
        redis_client: Redis,
        local_ttl: int = 60,  # 1 minute local cache
        redis_ttl: int = 3600  # 1 hour Redis cache
    ):
        self.local_cache = {}
        self.local_ttl = local_ttl
        self.redis_cache = CacheManager(redis_client)
        self.redis_ttl = redis_ttl

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache, trying local first then Redis"""
        # Try local cache first
        if key in self.local_cache:
            value, expiry = self.local_cache[key]
            if expiry > asyncio.get_event_loop().time():
                return value
            del self.local_cache[key]

        # Try Redis cache
        value = await self.redis_cache.get(key)
        if value is not None:
            # Update local cache
            expiry = asyncio.get_event_loop().time() + self.local_ttl
            self.local_cache[key] = (value, expiry)
        return value

    async def set(
        self,
        key: str,
        value: Any,
        local_ttl: Optional[int] = None,
        redis_ttl: Optional[int] = None
    ) -> bool:
        """Set value in both local and Redis cache"""
        # Set in local cache
        expiry = asyncio.get_event_loop().time() + (local_ttl or self.local_ttl)
        self.local_cache[key] = (value, expiry)

        # Set in Redis cache
        return await self.redis_cache.set(
            key,
            value,
            ttl=redis_ttl or self.redis_ttl
        )

    async def delete(self, key: str) -> bool:
        """Delete value from both caches"""
        if key in self.local_cache:
            del self.local_cache[key]
        return await self.redis_cache.delete(key)

    async def clear(self) -> None:
        """Clear both caches"""
        self.local_cache.clear()
        await self.redis_cache.delete_pattern("*")

class BatchOperationCache:
    """Cache manager for batch operations"""

    def __init__(self, redis_client: Redis):
        self.cache = CacheManager(redis_client)
        self.batch_size = settings.CACHE_BATCH_SIZE
        self.batch_ttl = settings.CACHE_BATCH_TTL

    async def get_batch(self, keys: List[str]) -> dict:
        """Get multiple values from cache"""
        result = {}
        pipe = self.redis.pipeline()
        
        for key in keys:
            pipe.get(self.cache._get_key(key))
        
        values = pipe.execute()
        
        for key, value in zip(keys, values):
            if value:
                result[key] = json.loads(value)
                
        return result

    async def set_batch(
        self,
        items: dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values in cache"""
        pipe = self.redis.pipeline()
        
        for key, value in items.items():
            serialized = json.dumps(value)
            pipe.setex(
                self.cache._get_key(key),
                ttl or self.batch_ttl,
                serialized
            )
            
        results = pipe.execute()
        return all(results)

    async def delete_batch(self, keys: List[str]) -> int:
        """Delete multiple values from cache"""
        pipe = self.redis.pipeline()
        
        for key in keys:
            pipe.delete(self.cache._get_key(key))
            
        results = pipe.execute()
        return sum(results)

class CacheStatistics:
    """Track cache statistics"""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.stats_prefix = "cache:stats:"

    async def increment_hit(self, cache_type: str) -> None:
        """Increment cache hit counter"""
        self.redis.incr(f"{self.stats_prefix}{cache_type}:hits")

    async def increment_miss(self, cache_type: str) -> None:
        """Increment cache miss counter"""
        self.redis.incr(f"{self.stats_prefix}{cache_type}:misses")

    async def get_stats(self, cache_type: str) -> dict:
        """Get cache statistics"""
        hits = int(self.redis.get(f"{self.stats_prefix}{cache_type}:hits") or 0)
        misses = int(self.redis.get(f"{self.stats_prefix}{cache_type}:misses") or 0)
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0

        return {
            "hits": hits,
            "misses": misses,
            "total": total,
            "hit_rate": hit_rate
        }

    async def reset_stats(self, cache_type: str) -> None:
        """Reset cache statistics"""
        self.redis.delete(
            f"{self.stats_prefix}{cache_type}:hits",
            f"{self.stats_prefix}{cache_type}:misses"
        )
