from typing import Optional, Tuple
from datetime import datetime
import time
from fastapi import HTTPException, Request
from redis import Redis
from app.core.config import settings

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # 1 minute window

    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate Redis key for rate limiting"""
        return f"rate_limit:{identifier}:{endpoint}"

    def _get_window_key(self, identifier: str, endpoint: str) -> str:
        """Generate Redis key for the current time window"""
        timestamp = int(time.time() / self.window) * self.window
        return f"{self._get_key(identifier, endpoint)}:{timestamp}"

    async def check_rate_limit(
        self, 
        request: Request,
        identifier: Optional[str] = None
    ) -> Tuple[bool, int]:
        """
        Check if the request should be rate limited
        Returns (is_allowed, remaining_requests)
        """
        if not identifier:
            identifier = request.client.host

        window_key = self._get_window_key(identifier, request.url.path)
        pipe = self.redis.pipeline()

        # Get current count and increment
        pipe.get(window_key)
        pipe.incr(window_key)
        pipe.expire(window_key, self.window)
        
        results = pipe.execute()
        current_count = int(results[1])

        if current_count > self.rate_limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Rate limit exceeded",
                    "reset_at": self._get_reset_time()
                }
            )

        remaining = max(0, self.rate_limit - current_count)
        return True, remaining

    def _get_reset_time(self) -> int:
        """Get timestamp when the current window expires"""
        current = int(time.time())
        window_start = (current // self.window) * self.window
        return window_start + self.window

    async def get_rate_limit_headers(
        self,
        request: Request,
        identifier: Optional[str] = None
    ) -> dict:
        """Get rate limit headers for the response"""
        if not identifier:
            identifier = request.client.host

        window_key = self._get_window_key(identifier, request.url.path)
        current_count = int(self.redis.get(window_key) or 0)
        
        return {
            "X-RateLimit-Limit": str(self.rate_limit),
            "X-RateLimit-Remaining": str(max(0, self.rate_limit - current_count)),
            "X-RateLimit-Reset": str(self._get_reset_time())
        }

    async def clear_rate_limit(
        self,
        identifier: str,
        endpoint: str
    ) -> None:
        """Clear rate limit for a specific identifier and endpoint"""
        key_pattern = f"{self._get_key(identifier, endpoint)}:*"
        keys = self.redis.keys(key_pattern)
        if keys:
            self.redis.delete(*keys)

class CompanyRateLimiter(RateLimiter):
    """Rate limiter that handles different limits per company tier"""

    TIER_LIMITS = {
        "free": 60,      # 60 requests per minute
        "basic": 300,    # 300 requests per minute
        "premium": 600,  # 600 requests per minute
        "enterprise": 1200  # 1200 requests per minute
    }

    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def check_rate_limit(
        self,
        request: Request,
        company_id: str,
        tier: str
    ) -> Tuple[bool, int]:
        """Check rate limit based on company tier"""
        self.rate_limit = self.TIER_LIMITS.get(tier, self.TIER_LIMITS["free"])
        return await super().check_rate_limit(request, f"company:{company_id}")

class BurstRateLimiter(RateLimiter):
    """Rate limiter that allows for burst traffic with cool-down"""

    def __init__(
        self,
        redis_client: Redis,
        burst_limit: int = 100,
        burst_window: int = 10
    ):
        super().__init__(redis_client)
        self.burst_limit = burst_limit
        self.burst_window = burst_window

    async def check_rate_limit(
        self,
        request: Request,
        identifier: Optional[str] = None
    ) -> Tuple[bool, int]:
        """Check both burst and regular rate limits"""
        if not identifier:
            identifier = request.client.host

        # Check burst limit
        burst_key = f"burst:{self._get_key(identifier, request.url.path)}"
        burst_count = int(self.redis.get(burst_key) or 0)

        if burst_count > self.burst_limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Burst rate limit exceeded",
                    "reset_at": int(time.time()) + self.burst_window
                }
            )

        # Increment burst counter
        pipe = self.redis.pipeline()
        pipe.incr(burst_key)
        pipe.expire(burst_key, self.burst_window)
        pipe.execute()

        # Check regular rate limit
        return await super().check_rate_limit(request, identifier)

class SlidingWindowRateLimiter(RateLimiter):
    """Rate limiter using sliding window algorithm"""

    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def check_rate_limit(
        self,
        request: Request,
        identifier: Optional[str] = None
    ) -> Tuple[bool, int]:
        """Check rate limit using sliding window"""
        if not identifier:
            identifier = request.client.host

        now = time.time()
        window_start = now - self.window
        key = self._get_key(identifier, request.url.path)

        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        current_count = self.redis.zcard(key)

        if current_count >= self.rate_limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Rate limit exceeded",
                    "reset_at": int(window_start + self.window)
                }
            )

        # Add current request
        self.redis.zadd(key, {str(now): now})
        self.redis.expire(key, self.window)

        remaining = max(0, self.rate_limit - (current_count + 1))
        return True, remaining
