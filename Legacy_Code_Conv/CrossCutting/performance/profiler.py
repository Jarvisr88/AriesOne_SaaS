"""Performance profiling module."""

import time
import cProfile
import pstats
import io
from typing import Optional, Callable, Any, Dict
from functools import wraps
from contextlib import contextmanager
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

def profile_function(
    sort_by: str = 'cumulative',
    lines: int = 20
) -> Callable:
    """Profile function decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            profiler = cProfile.Profile()
            try:
                return profiler.runcall(func, *args, **kwargs)
            finally:
                s = io.StringIO()
                stats = pstats.Stats(profiler, stream=s).sort_stats(sort_by)
                stats.print_stats(lines)
                logger.debug(f"Profile for {func.__name__}:\n{s.getvalue()}")
        return wrapper
    return decorator

@contextmanager
def profile_block(
    name: str,
    sort_by: str = 'cumulative',
    lines: int = 20
):
    """Profile code block context manager."""
    profiler = cProfile.Profile()
    profiler.enable()
    yield
    profiler.disable()
    
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats(sort_by)
    stats.print_stats(lines)
    logger.debug(f"Profile for block {name}:\n{s.getvalue()}")

class Timer:
    """Timer for measuring execution time."""
    
    def __init__(self, name: str):
        """Initialize timer."""
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        """Stop timer and log duration."""
        self.end_time = time.time()
        duration = (self.end_time - self.start_time) * 1000
        logger.debug(f"{self.name} took {duration:.2f}ms")

def time_function(func: Callable) -> Callable:
    """Time function decorator."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        with Timer(func.__name__):
            return func(*args, **kwargs)
    return wrapper

class ProfilingMiddleware(BaseHTTPMiddleware):
    """Middleware for request profiling."""
    
    def __init__(
        self,
        app: ASGIApp,
        threshold_ms: int = 500,
        profile_slow: bool = True
    ):
        """Initialize profiling middleware."""
        super().__init__(app)
        self.threshold_ms = threshold_ms
        self.profile_slow = profile_slow
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Any:
        """Process the request."""
        start_time = time.time()
        
        if self.profile_slow:
            profiler = cProfile.Profile()
            response = await profiler.runcall(call_next, request)
        else:
            response = await call_next(request)
        
        duration = (time.time() - start_time) * 1000
        
        # Log request timing
        logger.info(
            f"Request {request.method} {request.url.path} "
            f"took {duration:.2f}ms"
        )
        
        # Profile slow requests
        if duration > self.threshold_ms and self.profile_slow:
            s = io.StringIO()
            stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            stats.print_stats(20)
            logger.warning(
                f"Slow request profile for {request.method} "
                f"{request.url.path}:\n{s.getvalue()}"
            )
        
        return response

class PerformanceMetrics:
    """Collector for performance metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, Dict] = {}
    
    def record_timing(self, name: str, duration_ms: float) -> None:
        """Record timing metric."""
        if name not in self.metrics:
            self.metrics[name] = {
                'count': 0,
                'total_ms': 0,
                'min_ms': float('inf'),
                'max_ms': 0,
            }
        
        self.metrics[name]['count'] += 1
        self.metrics[name]['total_ms'] += duration_ms
        self.metrics[name]['min_ms'] = min(
            self.metrics[name]['min_ms'],
            duration_ms
        )
        self.metrics[name]['max_ms'] = max(
            self.metrics[name]['max_ms'],
            duration_ms
        )
    
    def get_metrics(self) -> Dict[str, Dict]:
        """Get collected metrics."""
        result = {}
        for name, data in self.metrics.items():
            result[name] = {
                'count': data['count'],
                'total_ms': data['total_ms'],
                'avg_ms': data['total_ms'] / data['count'],
                'min_ms': data['min_ms'],
                'max_ms': data['max_ms'],
            }
        return result
    
    def reset(self) -> None:
        """Reset metrics."""
        self.metrics.clear()
