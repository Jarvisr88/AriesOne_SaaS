"""
Redis caching implementation for the imaging service.
"""
from typing import Optional, Any, Dict
import json
import asyncio
from redis import Redis
import logging
from .config import settings


class CacheManager:
    """Manages Redis caching operations."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.logger = logging.getLogger(__name__)
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found
        """
        try:
            value = await asyncio.to_thread(
                self.redis.get,
                f"image:{key}"
            )
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get error: {str(e)}")
            return None
            
    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            ttl = ttl or settings.CACHE_TTL
            json_value = json.dumps(value)
            
            await asyncio.to_thread(
                self.redis.setex,
                f"image:{key}",
                ttl,
                json_value
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Cache set error: {str(e)}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete cached value.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        try:
            await asyncio.to_thread(
                self.redis.delete,
                f"image:{key}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Cache delete error: {str(e)}")
            return False
            
    async def invalidate_pattern(self, pattern: str) -> bool:
        """Invalidate cache by pattern.
        
        Args:
            pattern: Key pattern to match
            
        Returns:
            True if successful
        """
        try:
            # Get matching keys
            keys = await asyncio.to_thread(
                self.redis.keys,
                f"image:{pattern}"
            )
            
            if keys:
                # Delete in batches
                pipeline = self.redis.pipeline()
                for key in keys:
                    pipeline.delete(key)
                await asyncio.to_thread(pipeline.execute)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Cache invalidation error: {str(e)}")
            return False
            
    async def get_or_set(
        self,
        key: str,
        getter: callable,
        ttl: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get from cache or compute and cache.
        
        Args:
            key: Cache key
            getter: Function to get value if not cached
            ttl: Time to live in seconds
            
        Returns:
            Cached or computed value
        """
        # Try cache first
        cached = await self.get(key)
        if cached is not None:
            return cached
            
        try:
            # Compute value
            value = await getter()
            if value:
                # Cache result
                await self.set(key, value, ttl)
            return value
            
        except Exception as e:
            self.logger.error(f"Cache get_or_set error: {str(e)}")
            return None
