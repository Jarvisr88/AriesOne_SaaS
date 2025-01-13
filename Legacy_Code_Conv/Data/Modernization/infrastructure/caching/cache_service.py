"""Cache service module for managing cache operations."""
from typing import Any, Optional, TypeVar
from datetime import timedelta

from core.interfaces.cache import ICache
from infrastructure.caching.cache_strategy import (
    SingleObjectStrategy,
    ListObjectStrategy,
    CounterStrategy
)

T = TypeVar('T')

class CacheService:
    """Service for managing cache operations."""

    def __init__(self, cache: ICache):
        """Initialize cache service.
        
        Args:
            cache: Cache implementation.
        """
        self.cache = cache

    def get_object_cache(
        self,
        prefix: str,
        expire: Optional[timedelta] = None
    ) -> SingleObjectStrategy[Any]:
        """Get cache strategy for single objects.
        
        Args:
            prefix: Cache key prefix.
            expire: Optional expiration time.
            
        Returns:
            Single object cache strategy.
        """
        return SingleObjectStrategy(self.cache, prefix, expire)

    def get_list_cache(
        self,
        prefix: str,
        expire: Optional[timedelta] = None
    ) -> ListObjectStrategy[Any]:
        """Get cache strategy for lists.
        
        Args:
            prefix: Cache key prefix.
            expire: Optional expiration time.
            
        Returns:
            List cache strategy.
        """
        return ListObjectStrategy(self.cache, prefix, expire)

    def get_counter_cache(
        self,
        prefix: str,
        expire: Optional[timedelta] = None
    ) -> CounterStrategy:
        """Get cache strategy for counters.
        
        Args:
            prefix: Cache key prefix.
            expire: Optional expiration time.
            
        Returns:
            Counter cache strategy.
        """
        return CounterStrategy(self.cache, prefix, expire)

    async def clear_all(self) -> None:
        """Clear all cache entries."""
        await self.cache.clear()

    async def health_check(self) -> bool:
        """Check cache health.
        
        Returns:
            True if cache is healthy.
        """
        try:
            await self.cache.set("health_check", "ok", timedelta(seconds=1))
            value = await self.cache.get("health_check")
            return value == "ok"
        except Exception:
            return False
