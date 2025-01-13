"""
FastAPI middleware for monitoring.
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint
)
from starlette.types import ASGIApp
from .metrics import MetricsService


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request metrics."""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list = None
    ):
        """Initialize middleware.
        
        Args:
            app: ASGI application
            exclude_paths: Paths to exclude
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and collect metrics.
        
        Args:
            request: HTTP request
            call_next: Next middleware
            
        Returns:
            HTTP response
        """
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Track request in progress
        MetricsService.API_REQUEST_IN_PROGRESS.labels(
            method=request.method,
            endpoint=request.url.path
        ).inc()

        # Start timing
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate metrics
            duration = time.time() - start_time
            size = len(response.body) if hasattr(
                response,
                "body"
            ) else 0

            # Track metrics
            MetricsService.track_api_request(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                duration=duration,
                size=size
            )

            return response

        except Exception as e:
            # Track error metrics
            MetricsService.track_api_request(
                method=request.method,
                endpoint=request.url.path,
                status=500,
                duration=time.time() - start_time,
                size=0
            )
            raise e

        finally:
            # Decrement in progress
            MetricsService.API_REQUEST_IN_PROGRESS.labels(
                method=request.method,
                endpoint=request.url.path
            ).dec()
