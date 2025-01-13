"""Caching service module."""

from typing import Any, Optional, Union, Callable
from datetime import timedelta
import json
import hashlib
from functools import wraps
import redis
from fastapi import Request, Response
from app.core.config import settings

class CacheService:
    """Service for handling caching operations."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize cache service."""
        self.redis = redis.from_url(redis_url or settings.REDIS_URL)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> None:
        """Set value in cache."""
        serialized = json.dumps(value)
        if expire:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            self.redis.setex(key, expire, serialized)
        else:
            self.redis.set(key, serialized)
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.redis.delete(key)
    
    def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern."""
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)

def cache_response(
    expire: Optional[Union[int, timedelta]] = 300,
    key_prefix: str = "response",
    vary_on_headers: Optional[list] = None
):
    """Cache decorator for FastAPI response."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object
            request = next(
                (arg for arg in args if isinstance(arg, Request)),
                None
            )
            
            if not request:
                return await func(*args, **kwargs)
            
            # Build cache key
            key_parts = [key_prefix, request.url.path]
            
            # Add query params
            if request.query_params:
                key_parts.append(str(request.query_params))
            
            # Add varying headers
            if vary_on_headers:
                for header in vary_on_headers:
                    value = request.headers.get(header)
                    if value:
                        key_parts.append(f"{header}:{value}")
            
            cache_key = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            # Try to get from cache
            cache = CacheService()
            cached = cache.get(cache_key)
            
            if cached:
                return Response(
                    content=cached["content"],
                    media_type=cached["media_type"],
                    status_code=cached["status_code"],
                    headers=cached["headers"]
                )
            
            # Get fresh response
            response = await func(*args, **kwargs)
            
            # Cache response
            if response.status_code < 400:
                to_cache = {
                    "content": response.body,
                    "media_type": response.media_type,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
                cache.set(cache_key, to_cache, expire)
            
            return response
        return wrapper
    return decorator

class QueryCache:
    """Cache for database queries."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize query cache."""
        self.redis = redis.from_url(redis_url or settings.REDIS_URL)
        self.prefix = "query:"
    
    def _make_key(self, query: str, params: tuple) -> str:
        """Make cache key from query and params."""
        key_parts = [query]
        if params:
            key_parts.extend(str(p) for p in params)
        
        return self.prefix + hashlib.md5(
            ":".join(key_parts).encode()
        ).hexdigest()
    
    def get(self, query: str, params: tuple) -> Optional[Any]:
        """Get cached query result."""
        key = self._make_key(query, params)
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(
        self,
        query: str,
        params: tuple,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> None:
        """Set query result in cache."""
        key = self._make_key(query, params)
        serialized = json.dumps(value)
        if expire:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            self.redis.setex(key, expire, serialized)
        else:
            self.redis.set(key, serialized)
    
    def invalidate(self, pattern: str = "*") -> None:
        """Invalidate cached queries."""
        pattern = f"{self.prefix}{pattern}"
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)
