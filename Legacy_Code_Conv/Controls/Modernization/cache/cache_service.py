from typing import Any, Optional, Union
from datetime import datetime, timedelta
import redis
import json
from functools import wraps

class CacheService:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.default_ttl = timedelta(hours=1)

    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """Set a value in cache with optional TTL"""
        try:
            serialized_value = json.dumps(value)
            return self.redis_client.set(
                key,
                serialized_value,
                ex=int(ttl.total_seconds()) if ttl else int(self.default_ttl.total_seconds())
            )
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

def cached(ttl: Optional[timedelta] = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_service = CacheService()
            
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value

            # If not in cache, execute function and cache result
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

class AddressCache:
    def __init__(self):
        self.cache_service = CacheService()
        self.address_ttl = timedelta(days=7)  # Cache addresses for 7 days

    def get_cached_address(self, address_id: str) -> Optional[dict]:
        return self.cache_service.get(f"address:{address_id}")

    def cache_address(self, address_id: str, address_data: dict):
        self.cache_service.set(f"address:{address_id}", address_data, self.address_ttl)

    def invalidate_address(self, address_id: str):
        self.cache_service.delete(f"address:{address_id}")

class NameCache:
    def __init__(self):
        self.cache_service = CacheService()
        self.name_ttl = timedelta(days=30)  # Cache names for 30 days

    def get_cached_name(self, name_id: str) -> Optional[dict]:
        return self.cache_service.get(f"name:{name_id}")

    def cache_name(self, name_id: str, name_data: dict):
        self.cache_service.set(f"name:{name_id}", name_data, self.name_ttl)

    def invalidate_name(self, name_id: str):
        self.cache_service.delete(f"name:{name_id}")

# Initialize global cache services
address_cache = AddressCache()
name_cache = NameCache()
