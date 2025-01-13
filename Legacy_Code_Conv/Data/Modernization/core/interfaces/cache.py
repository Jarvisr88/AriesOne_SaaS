"""Cache interface module."""
from typing import Any, Optional, Protocol
from datetime import timedelta

class ICache(Protocol):
    """Interface for cache operations."""

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value if exists, None otherwise.
        """
        raise NotImplementedError

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[timedelta] = None
    ) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            expire: Optional expiration time.
        """
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        """Delete value from cache.
        
        Args:
            key: Cache key.
        """
        raise NotImplementedError

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if key exists, False otherwise.
        """
        raise NotImplementedError

    async def clear(self, pattern: str = "*") -> None:
        """Clear cache entries matching pattern.
        
        Args:
            pattern: Pattern to match keys.
        """
        raise NotImplementedError

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache.
        
        Args:
            key: Cache key.
            amount: Amount to increment.
            
        Returns:
            New counter value.
        """
        raise NotImplementedError

    async def get_or_set(
        self,
        key: str,
        factory: callable,
        expire: Optional[timedelta] = None
    ) -> Any:
        """Get value from cache or set if not exists.
        
        Args:
            key: Cache key.
            factory: Function to generate value if not cached.
            expire: Optional expiration time.
            
        Returns:
            Cached or generated value.
        """
        raise NotImplementedError
