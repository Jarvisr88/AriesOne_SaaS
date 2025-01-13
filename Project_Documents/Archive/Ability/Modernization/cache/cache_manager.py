"""Cache manager for Ability module."""
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel
from redis import Redis

T = TypeVar("T", bound=BaseModel)


class CacheManager:
    """Cache manager for application data."""
    
    def __init__(
        self,
        redis_client: Redis,
        default_ttl: int = 3600  # 1 hour
    ):
        """Initialize cache manager.
        
        Args:
            redis_client: Redis client
            default_ttl: Default cache TTL in seconds
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    def _get_cache_key(
        self,
        key_type: str,
        key_id: Any,
        company_id: Optional[int] = None
    ) -> str:
        """Get cache key.
        
        Args:
            key_type: Type of cached data
            key_id: Identifier
            company_id: Optional company ID for isolation
            
        Returns:
            Cache key string
        """
        if company_id:
            return f"{key_type}:{company_id}:{key_id}"
        return f"{key_type}:{key_id}"
    
    async def get(
        self,
        key_type: str,
        key_id: Any,
        model: Type[T],
        company_id: Optional[int] = None
    ) -> Optional[T]:
        """Get item from cache.
        
        Args:
            key_type: Type of cached data
            key_id: Identifier
            model: Pydantic model class
            company_id: Optional company ID
            
        Returns:
            Cached item or None
        """
        key = self._get_cache_key(key_type, key_id, company_id)
        data = self.redis.get(key)
        
        if data:
            try:
                return model.parse_raw(data)
            except Exception:
                # Invalid cache data, remove it
                self.redis.delete(key)
        
        return None
    
    async def set(
        self,
        key_type: str,
        key_id: Any,
        value: BaseModel,
        ttl: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> None:
        """Set item in cache.
        
        Args:
            key_type: Type of cached data
            key_id: Identifier
            value: Item to cache
            ttl: Optional TTL in seconds
            company_id: Optional company ID
        """
        key = self._get_cache_key(key_type, key_id, company_id)
        self.redis.set(
            key,
            value.json(),
            ex=ttl or self.default_ttl
        )
    
    async def delete(
        self,
        key_type: str,
        key_id: Any,
        company_id: Optional[int] = None
    ) -> None:
        """Delete item from cache.
        
        Args:
            key_type: Type of cached data
            key_id: Identifier
            company_id: Optional company ID
        """
        key = self._get_cache_key(key_type, key_id, company_id)
        self.redis.delete(key)
    
    async def delete_pattern(
        self,
        pattern: str
    ) -> None:
        """Delete items matching pattern.
        
        Args:
            pattern: Redis key pattern
        """
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    async def get_many(
        self,
        key_type: str,
        key_ids: list[Any],
        model: Type[T],
        company_id: Optional[int] = None
    ) -> Dict[Any, Optional[T]]:
        """Get multiple items from cache.
        
        Args:
            key_type: Type of cached data
            key_ids: List of identifiers
            model: Pydantic model class
            company_id: Optional company ID
            
        Returns:
            Dictionary of ID to item mappings
        """
        pipeline = self.redis.pipeline()
        keys = [
            self._get_cache_key(key_type, key_id, company_id)
            for key_id in key_ids
        ]
        
        for key in keys:
            pipeline.get(key)
        
        results = pipeline.execute()
        items = {}
        
        for key_id, data in zip(key_ids, results):
            if data:
                try:
                    items[key_id] = model.parse_raw(data)
                except Exception:
                    # Invalid cache data
                    items[key_id] = None
            else:
                items[key_id] = None
        
        return items
    
    async def set_many(
        self,
        key_type: str,
        items: Dict[Any, BaseModel],
        ttl: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> None:
        """Set multiple items in cache.
        
        Args:
            key_type: Type of cached data
            items: Dictionary of ID to item mappings
            ttl: Optional TTL in seconds
            company_id: Optional company ID
        """
        pipeline = self.redis.pipeline()
        
        for key_id, value in items.items():
            key = self._get_cache_key(key_type, key_id, company_id)
            pipeline.set(
                key,
                value.json(),
                ex=ttl or self.default_ttl
            )
        
        pipeline.execute()
    
    async def delete_many(
        self,
        key_type: str,
        key_ids: list[Any],
        company_id: Optional[int] = None
    ) -> None:
        """Delete multiple items from cache.
        
        Args:
            key_type: Type of cached data
            key_ids: List of identifiers
            company_id: Optional company ID
        """
        keys = [
            self._get_cache_key(key_type, key_id, company_id)
            for key_id in key_ids
        ]
        self.redis.delete(*keys)
    
    async def increment(
        self,
        key_type: str,
        key_id: Any,
        amount: int = 1,
        company_id: Optional[int] = None
    ) -> int:
        """Increment counter in cache.
        
        Args:
            key_type: Type of cached data
            key_id: Identifier
            amount: Amount to increment by
            company_id: Optional company ID
            
        Returns:
            New counter value
        """
        key = self._get_cache_key(key_type, key_id, company_id)
        return self.redis.incrby(key, amount)
    
    async def expire_at(
        self,
        key_type: str,
        key_id: Any,
        timestamp: datetime,
        company_id: Optional[int] = None
    ) -> None:
        """Set expiration time for cached item.
        
        Args:
            key_type: Type of cached data
            key_id: Identifier
            timestamp: Expiration timestamp
            company_id: Optional company ID
        """
        key = self._get_cache_key(key_type, key_id, company_id)
        self.redis.expireat(key, int(timestamp.timestamp()))
    
    async def clear_all(self) -> None:
        """Clear all cached data."""
        self.redis.flushall()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        info = self.redis.info()
        return {
            "used_memory": info["used_memory"],
            "used_memory_peak": info["used_memory_peak"],
            "total_connections_received": info["total_connections_received"],
            "total_commands_processed": info["total_commands_processed"],
            "keyspace_hits": info["keyspace_hits"],
            "keyspace_misses": info["keyspace_misses"],
            "uptime_in_seconds": info["uptime_in_seconds"]
        }
