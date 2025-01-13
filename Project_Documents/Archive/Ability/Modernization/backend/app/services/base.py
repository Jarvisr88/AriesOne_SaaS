from typing import Any, Optional, TypeVar, Generic
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import aiocache
import aioredis
from fastapi import HTTPException
from app.core.config import settings
from app.core.logging import logger
from app.core.monitoring import metrics
from app.core.redis import redis_client

T = TypeVar('T')

class RateLimiter:
    """Rate limiter using Redis"""
    def __init__(self, key_prefix: str, limit: int, window: int):
        self.key_prefix = key_prefix
        self.limit = limit
        self.window = window

    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        redis_key = f"{self.key_prefix}:{key}"
        async with redis_client() as redis:
            pipeline = redis.pipeline()
            now = datetime.utcnow().timestamp()
            pipeline.zremrangebyscore(
                redis_key,
                0,
                now - self.window
            )
            pipeline.zadd(redis_key, {str(now): now})
            pipeline.zcard(redis_key)
            pipeline.expire(redis_key, self.window)
            _, _, count, _ = await pipeline.execute()
            return count <= self.limit

class RetryPolicy:
    """Retry policy with exponential backoff"""
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        return delay * (0.5 + asyncio.random())

class BaseService:
    """Base service with caching, rate limiting, and retry logic"""
    
    def __init__(self):
        self.cache = aiocache.Cache.from_url(settings.REDIS_URL)
        self.rate_limiters = {
            "default": RateLimiter("rate_limit", 100, 60),
            "upload": RateLimiter("upload_limit", 10, 60),
            "submission": RateLimiter("submission_limit", 50, 60)
        }
        self.retry_policy = RetryPolicy()

    def cache_key(self, prefix: str, *args: Any) -> str:
        """Generate cache key"""
        return f"{prefix}:" + ":".join(str(arg) for arg in args)

    async def get_cached(
        self,
        key: str,
        ttl: Optional[int] = None
    ) -> Optional[Any]:
        """Get item from cache"""
        try:
            value = await self.cache.get(key)
            if value is not None:
                metrics.cache_hits.inc()
            else:
                metrics.cache_misses.inc()
            return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            metrics.cache_errors.inc()
            return None

    async def set_cached(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set item in cache"""
        try:
            await self.cache.set(key, value, ttl=ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            metrics.cache_errors.inc()

    async def delete_cached(self, key: str) -> None:
        """Delete item from cache"""
        try:
            await self.cache.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            metrics.cache_errors.inc()

    async def check_rate_limit(
        self,
        limiter_key: str,
        identifier: str
    ) -> None:
        """Check rate limit"""
        limiter = self.rate_limiters.get(limiter_key)
        if limiter and not await limiter.is_allowed(identifier):
            metrics.rate_limit_exceeded.inc()
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )

    async def with_retry(
        self,
        func: callable,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """Execute function with retry logic"""
        last_error = None
        metrics.retry_attempts.inc()

        for attempt in range(self.retry_policy.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Retry attempt {attempt + 1} failed: {e}"
                )
                if attempt < self.retry_policy.max_retries - 1:
                    delay = self.retry_policy.get_delay(attempt)
                    metrics.retry_delays.observe(delay)
                    await asyncio.sleep(delay)

        metrics.retry_failures.inc()
        raise last_error

    def validate_input(self, data: Any, validator: callable) -> None:
        """Validate input data"""
        try:
            validator(data)
        except Exception as e:
            metrics.validation_errors.inc()
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )

    async def clear_cache_pattern(self, pattern: str) -> None:
        """Clear cache keys matching pattern"""
        try:
            async with redis_client() as redis:
                keys = await redis.keys(pattern)
                if keys:
                    await redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            metrics.cache_errors.inc()

def cached(
    prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[callable] = None
):
    """Cache decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'cache'):
                return await func(self, *args, **kwargs)

            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = self.cache_key(prefix, *args)

            result = await self.get_cached(cache_key)
            if result is not None:
                return result

            result = await func(self, *args, **kwargs)
            await self.set_cached(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

def rate_limited(limiter_key: str = "default"):
    """Rate limit decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if hasattr(self, 'check_rate_limit'):
                await self.check_rate_limit(
                    limiter_key,
                    str(args[0]) if args else "default"
                )
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator

def with_retry(func):
    """Retry decorator"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if hasattr(self, 'with_retry'):
            return await self.with_retry(func, self, *args, **kwargs)
        return await func(self, *args, **kwargs)
    return wrapper
