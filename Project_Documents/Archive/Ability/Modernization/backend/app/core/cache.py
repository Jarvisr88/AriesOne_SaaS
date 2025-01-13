from typing import Any, Optional, Union
from datetime import datetime, timedelta
import json
import pickle
from redis.asyncio import Redis
from app.core.config import settings

class CacheManager:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
        self.default_ttl = settings.DEFAULT_CACHE_TTL

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = None
    ) -> bool:
        """Set value in cache"""
        try:
            pickled_value = pickle.dumps(value)
            await self.redis.set(
                key,
                pickled_value,
                ex=expire or self.default_ttl
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            print(f"Cache expire error: {e}")
            return False

    async def clear(self, pattern: str = None) -> bool:
        """Clear cache entries matching pattern"""
        try:
            if pattern:
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
            else:
                await self.redis.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

    async def increment(
        self,
        key: str,
        amount: int = 1,
        expire: int = None
    ) -> Optional[int]:
        """Increment counter in cache"""
        try:
            value = await self.redis.incr(key, amount)
            if expire:
                await self.redis.expire(key, expire)
            return value
        except Exception as e:
            print(f"Cache increment error: {e}")
            return None

    async def decrement(
        self,
        key: str,
        amount: int = 1,
        expire: int = None
    ) -> Optional[int]:
        """Decrement counter in cache"""
        try:
            value = await self.redis.decr(key, amount)
            if expire:
                await self.redis.expire(key, expire)
            return value
        except Exception as e:
            print(f"Cache decrement error: {e}")
            return None

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache"""
        try:
            values = await self.redis.mget(keys)
            return {
                key: pickle.loads(value) if value else None
                for key, value in zip(keys, values)
            }
        except Exception as e:
            print(f"Cache get_many error: {e}")
            return {}

    async def set_many(
        self,
        mapping: dict[str, Any],
        expire: int = None
    ) -> bool:
        """Set multiple values in cache"""
        try:
            pickled_mapping = {
                key: pickle.dumps(value)
                for key, value in mapping.items()
            }
            await self.redis.mset(pickled_mapping)
            if expire:
                for key in mapping:
                    await self.redis.expire(key, expire)
            return True
        except Exception as e:
            print(f"Cache set_many error: {e}")
            return False

    async def delete_many(self, keys: list[str]) -> bool:
        """Delete multiple values from cache"""
        try:
            await self.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache delete_many error: {e}")
            return False

cache_manager = CacheManager()
