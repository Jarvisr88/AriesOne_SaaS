"""Cache strategy module for defining caching patterns."""
from typing import Any, Optional, TypeVar, Generic
from datetime import timedelta
from abc import ABC, abstractmethod

from core.interfaces.cache import ICache

T = TypeVar('T')

class CacheStrategy(ABC, Generic[T]):
    """Base class for cache strategies."""

    def __init__(
        self,
        cache: ICache,
        prefix: str,
        expire: Optional[timedelta] = None
    ):
        """Initialize cache strategy.
        
        Args:
            cache: Cache implementation.
            prefix: Cache key prefix.
            expire: Optional expiration time.
        """
        self.cache = cache
        self.prefix = prefix
        self.expire = expire

    def make_key(self, *parts: Any) -> str:
        """Make cache key from parts.
        
        Args:
            parts: Key parts to combine.
            
        Returns:
            Cache key.
        """
        return f"{self.prefix}:{':'.join(str(p) for p in parts)}"

    @abstractmethod
    async def get(self, *args: Any, **kwargs: Any) -> Optional[T]:
        """Get value from cache."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, value: T, *args: Any, **kwargs: Any) -> None:
        """Set value in cache."""
        raise NotImplementedError

    @abstractmethod
    async def invalidate(self, *args: Any, **kwargs: Any) -> None:
        """Invalidate cached value."""
        raise NotImplementedError

class SingleObjectStrategy(CacheStrategy[T]):
    """Strategy for caching single objects."""

    async def get(self, id: Any) -> Optional[T]:
        """Get object from cache by ID."""
        key = self.make_key(id)
        return await self.cache.get(key)

    async def set(self, value: T, id: Any) -> None:
        """Set object in cache by ID."""
        key = self.make_key(id)
        await self.cache.set(key, value, self.expire)

    async def invalidate(self, id: Any) -> None:
        """Invalidate cached object by ID."""
        key = self.make_key(id)
        await self.cache.delete(key)

class ListObjectStrategy(CacheStrategy[list[T]]):
    """Strategy for caching lists of objects."""

    async def get(self, filter_key: str = "") -> Optional[list[T]]:
        """Get list from cache by filter key."""
        key = self.make_key(filter_key)
        return await self.cache.get(key)

    async def set(self, value: list[T], filter_key: str = "") -> None:
        """Set list in cache by filter key."""
        key = self.make_key(filter_key)
        await self.cache.set(key, value, self.expire)

    async def invalidate(self, filter_key: str = "") -> None:
        """Invalidate cached list by filter key."""
        if filter_key:
            key = self.make_key(filter_key)
            await self.cache.delete(key)
        else:
            await self.cache.clear(f"{self.prefix}:*")

class CounterStrategy(CacheStrategy[int]):
    """Strategy for caching counters."""

    async def get(self, counter_key: str) -> Optional[int]:
        """Get counter value."""
        key = self.make_key(counter_key)
        return await self.cache.get(key)

    async def set(self, value: int, counter_key: str) -> None:
        """Set counter value."""
        key = self.make_key(counter_key)
        await self.cache.set(key, value, self.expire)

    async def increment(self, counter_key: str, amount: int = 1) -> int:
        """Increment counter value."""
        key = self.make_key(counter_key)
        return await self.cache.increment(key, amount)

    async def invalidate(self, counter_key: str) -> None:
        """Invalidate counter."""
        key = self.make_key(counter_key)
        await self.cache.delete(key)
