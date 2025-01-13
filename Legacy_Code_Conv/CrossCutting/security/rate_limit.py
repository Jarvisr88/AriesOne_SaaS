"""Rate limiting middleware module."""

import time
from typing import Optional, Dict, Tuple, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis
from app.core.config import settings

class RateLimiter:
    """Rate limiter using Redis."""
    
    def __init__(
        self,
        redis_url: str,
        rate_limit: int,
        rate_limit_period: int
    ):
        """Initialize rate limiter."""
        self.redis = redis.from_url(redis_url)
        self.rate_limit = rate_limit
        self.rate_limit_period = rate_limit_period
    
    def is_rate_limited(self, key: str) -> Tuple[bool, Dict[str, int]]:
        """Check if request is rate limited."""
        pipe = self.redis.pipeline()
        now = time.time()
        cleanup_before = now - self.rate_limit_period
        
        # Remove old requests
        pipe.zremrangebyscore(key, 0, cleanup_before)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Count requests in window
        pipe.zcard(key)
        
        # Set key expiration
        pipe.expire(key, self.rate_limit_period)
        
        # Execute pipeline
        _, _, num_requests, _ = pipe.execute()
        
        # Get remaining requests
        remaining = max(self.rate_limit - num_requests, 0)
        reset_time = int(now) + self.rate_limit_period
        
        headers = {
            "X-RateLimit-Limit": self.rate_limit,
            "X-RateLimit-Remaining": remaining,
            "X-RateLimit-Reset": reset_time
        }
        
        return num_requests > self.rate_limit, headers

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(
        self,
        app: ASGIApp,
        rate_limit: int = 100,
        rate_limit_period: int = 60,
        redis_url: Optional[str] = None
    ):
        """Initialize rate limit middleware."""
        super().__init__(app)
        self.limiter = RateLimiter(
            redis_url or settings.REDIS_URL,
            rate_limit,
            rate_limit_period
        )
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process the request."""
        # Get client identifier (IP address or API key)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        is_limited, headers = self.limiter.is_rate_limited(
            f"rate_limit:{client_id}"
        )
        
        if is_limited:
            return Response(
                status_code=429,
                content="Too many requests",
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        for key, value in headers.items():
            response.headers[key] = str(value)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier."""
        # Try to get API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        
        return request.client.host
