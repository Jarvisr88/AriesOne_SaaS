"""
Core Metrics Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides metrics collection functionality.
"""
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from prometheus_client import Counter, Gauge, Histogram, Summary

from ..utils.logging import CoreLogger

logger = CoreLogger(__name__)

# Request metrics
REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

REQUEST_COUNT = Counter(
    'request_count_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

# Database metrics
DB_CONNECTION_POOL = Gauge(
    'db_connection_pool',
    'Database connection pool statistics',
    ['state']  # idle, used, overflow
)

DB_QUERY_LATENCY = Histogram(
    'db_query_latency_seconds',
    'Database query latency in seconds',
    ['operation', 'table']
)

# Cache metrics
CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

# Business metrics
ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

ERROR_COUNT = Counter(
    'error_count_total',
    'Total error count',
    ['type', 'location']
)

# Resource metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)


def track_request_metrics(method: str, endpoint: str):
    """Decorator to track request metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            status = "success"
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                ERROR_COUNT.labels(
                    type=type(e).__name__,
                    location=f"{method}:{endpoint}"
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
        return wrapper
    return decorator


def track_db_metrics(operation: str, table: str):
    """Decorator to track database metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                DB_QUERY_LATENCY.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
        return wrapper
    return decorator


class MetricsCollector:
    """Metrics collection service."""
    
    @staticmethod
    def record_cache_operation(cache_name: str, hit: bool) -> None:
        """Record cache hit or miss."""
        if hit:
            CACHE_HITS.labels(cache_name=cache_name).inc()
        else:
            CACHE_MISSES.labels(cache_name=cache_name).inc()
    
    @staticmethod
    def update_active_users(count: int) -> None:
        """Update active users count."""
        ACTIVE_USERS.set(count)
    
    @staticmethod
    def update_resource_usage(memory_bytes: int, cpu_percent: float) -> None:
        """Update resource usage metrics."""
        MEMORY_USAGE.set(memory_bytes)
        CPU_USAGE.set(cpu_percent)
    
    @staticmethod
    def update_db_pool_stats(idle: int, used: int, overflow: int) -> None:
        """Update database pool statistics."""
        DB_CONNECTION_POOL.labels(state="idle").set(idle)
        DB_CONNECTION_POOL.labels(state="used").set(used)
        DB_CONNECTION_POOL.labels(state="overflow").set(overflow)
    
    @staticmethod
    def get_current_metrics() -> Dict[str, Any]:
        """Get current metrics values."""
        return {
            "request_metrics": {
                "latency": REQUEST_LATENCY._samples(),
                "count": REQUEST_COUNT._samples()
            },
            "database_metrics": {
                "pool": DB_CONNECTION_POOL._samples(),
                "query_latency": DB_QUERY_LATENCY._samples()
            },
            "cache_metrics": {
                "hits": CACHE_HITS._samples(),
                "misses": CACHE_MISSES._samples()
            },
            "business_metrics": {
                "active_users": ACTIVE_USERS._value,
                "errors": ERROR_COUNT._samples()
            },
            "resource_metrics": {
                "memory": MEMORY_USAGE._value,
                "cpu": CPU_USAGE._value
            },
            "timestamp": datetime.utcnow().isoformat()
        }
