"""Rate limiting middleware for Ability module."""
import time
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException
from redis import Redis
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(
        self,
        app,
        redis_client: Redis,
        rate_limit: int = 100,  # requests
        time_window: int = 60,  # seconds
        burst_limit: int = 10   # concurrent requests
    ):
        """Initialize rate limiter.
        
        Args:
            app: FastAPI application
            redis_client: Redis client for rate limiting
            rate_limit: Maximum requests per time window
            time_window: Time window in seconds
            burst_limit: Maximum concurrent requests
        """
        super().__init__(app)
        self.redis = redis_client
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.burst_limit = burst_limit
    
    async def get_rate_limit_key(
        self,
        request: Request
    ) -> Tuple[str, str]:
        """Get rate limit keys for request.
        
        Args:
            request: FastAPI request
            
        Returns:
            Tuple of rate limit key and burst key
        """
        # Get client identifier (user ID or IP)
        client_id = (
            request.headers.get("user-id")
            or request.client.host
        )
        
        # Get endpoint path
        path = request.url.path
        
        # Create keys
        rate_key = f"rate_limit:{client_id}:{path}"
        burst_key = f"burst_limit:{client_id}:{path}"
        
        return rate_key, burst_key
    
    async def check_rate_limit(
        self,
        rate_key: str,
        burst_key: str
    ) -> Tuple[bool, Dict]:
        """Check if request is within rate limits.
        
        Args:
            rate_key: Rate limit key
            burst_key: Burst limit key
            
        Returns:
            Tuple of (allowed, limit info)
        """
        current_time = int(time.time())
        
        # Check burst limit
        burst_count = self.redis.get(burst_key)
        if burst_count and int(burst_count) >= self.burst_limit:
            return False, {
                "error": "Too many concurrent requests",
                "limit": self.burst_limit,
                "remaining": 0,
                "reset": 1  # Reset after 1 second
            }
        
        # Initialize sliding window
        pipeline = self.redis.pipeline()
        pipeline.incr(rate_key)
        pipeline.expire(rate_key, self.time_window)
        pipeline.incr(burst_key)
        pipeline.expire(burst_key, 1)  # Burst window is 1 second
        result = pipeline.execute()
        
        request_count = result[0]
        
        if request_count > self.rate_limit:
            return False, {
                "error": "Rate limit exceeded",
                "limit": self.rate_limit,
                "remaining": 0,
                "reset": self.time_window - (
                    current_time % self.time_window
                )
            }
        
        return True, {
            "limit": self.rate_limit,
            "remaining": self.rate_limit - request_count,
            "reset": self.time_window - (
                current_time % self.time_window
            )
        }
    
    async def dispatch(
        self,
        request: Request,
        call_next
    ):
        """Process request with rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        # Skip rate limiting for certain paths
        if request.url.path in [
            "/health",
            "/metrics",
            "/docs",
            "/redoc"
        ]:
            return await call_next(request)
        
        # Get rate limit keys
        rate_key, burst_key = await self.get_rate_limit_key(
            request
        )
        
        # Check rate limits
        allowed, limit_info = await self.check_rate_limit(
            rate_key,
            burst_key
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=limit_info
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(
            limit_info["limit"]
        )
        response.headers["X-RateLimit-Remaining"] = str(
            limit_info["remaining"]
        )
        response.headers["X-RateLimit-Reset"] = str(
            limit_info["reset"]
        )
        
        # Cleanup burst counter
        self.redis.delete(burst_key)
        
        return response
