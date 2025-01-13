"""Metrics collection module."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass, field
from prometheus_client import Counter, Gauge, Histogram, Summary
from app.core.config import settings

@dataclass
class MetricPoint:
    """Single metric data point."""
    
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """Collector for application metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
        )
        self.http_request_size = Summary(
            'http_request_size_bytes',
            'HTTP request size in bytes',
            ['method', 'endpoint']
        )
        self.http_response_size = Summary(
            'http_response_size_bytes',
            'HTTP response size in bytes',
            ['method', 'endpoint']
        )
        
        # Database metrics
        self.db_connections = Gauge(
            'db_connections',
            'Number of active database connections',
            ['database']
        )
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table']
        )
        self.db_errors = Counter(
            'db_errors_total',
            'Total database errors',
            ['operation', 'error_type']
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache']
        )
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache']
        )
        self.cache_size = Gauge(
            'cache_size_bytes',
            'Cache size in bytes',
            ['cache']
        )
        
        # Queue metrics
        self.queue_size = Gauge(
            'queue_size',
            'Number of messages in queue',
            ['queue']
        )
        self.queue_processing_time = Histogram(
            'queue_processing_time_seconds',
            'Message processing time in seconds',
            ['queue']
        )
        self.queue_errors = Counter(
            'queue_errors_total',
            'Total queue processing errors',
            ['queue', 'error_type']
        )
        
        # Business metrics
        self.active_users = Gauge(
            'active_users',
            'Number of active users'
        )
        self.business_operations = Counter(
            'business_operations_total',
            'Total business operations',
            ['operation_type']
        )
        self.operation_value = Summary(
            'operation_value_dollars',
            'Value of business operations in dollars',
            ['operation_type']
        )
    
    def track_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float,
        request_size: int,
        response_size: int
    ) -> None:
        """Track HTTP request metrics."""
        labels = {'method': method, 'endpoint': endpoint}
        status_labels = {**labels, 'status': str(status)}
        
        self.http_requests_total.labels(**status_labels).inc()
        self.http_request_duration.labels(**labels).observe(duration)
        self.http_request_size.labels(**labels).observe(request_size)
        self.http_response_size.labels(**labels).observe(response_size)
    
    def track_database(
        self,
        operation: str,
        table: str,
        duration: float,
        error: Optional[Exception] = None
    ) -> None:
        """Track database metrics."""
        labels = {'operation': operation, 'table': table}
        
        self.db_query_duration.labels(**labels).observe(duration)
        if error:
            error_labels = {
                'operation': operation,
                'error_type': type(error).__name__
            }
            self.db_errors.labels(**error_labels).inc()
    
    def track_cache(
        self,
        cache_name: str,
        hit: bool,
        size: Optional[int] = None
    ) -> None:
        """Track cache metrics."""
        labels = {'cache': cache_name}
        
        if hit:
            self.cache_hits.labels(**labels).inc()
        else:
            self.cache_misses.labels(**labels).inc()
        
        if size is not None:
            self.cache_size.labels(**labels).set(size)
    
    def track_queue(
        self,
        queue_name: str,
        size: int,
        processing_time: Optional[float] = None,
        error: Optional[Exception] = None
    ) -> None:
        """Track queue metrics."""
        labels = {'queue': queue_name}
        
        self.queue_size.labels(**labels).set(size)
        
        if processing_time is not None:
            self.queue_processing_time.labels(**labels).observe(
                processing_time
            )
        
        if error:
            error_labels = {
                'queue': queue_name,
                'error_type': type(error).__name__
            }
            self.queue_errors.labels(**error_labels).inc()
    
    def track_business(
        self,
        operation_type: str,
        value: Optional[float] = None
    ) -> None:
        """Track business metrics."""
        self.business_operations.labels(
            operation_type=operation_type
        ).inc()
        
        if value is not None:
            self.operation_value.labels(
                operation_type=operation_type
            ).observe(value)
    
    def set_active_users(self, count: int) -> None:
        """Set number of active users."""
        self.active_users.set(count)

class MetricsAggregator:
    """Aggregator for metrics data."""
    
    def __init__(self, window_size: timedelta = timedelta(minutes=5)):
        """Initialize metrics aggregator."""
        self.window_size = window_size
        self.metrics: Dict[str, List[MetricPoint]] = {}
    
    def add_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Add metric data point."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {}
        )
        self.metrics[name].append(point)
        
        # Clean old data points
        self._clean_old_points(name)
    
    def _clean_old_points(self, metric_name: str) -> None:
        """Remove data points outside window."""
        cutoff = datetime.utcnow() - self.window_size
        self.metrics[metric_name] = [
            p for p in self.metrics[metric_name]
            if p.timestamp > cutoff
        ]
    
    def get_stats(
        self,
        metric_name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """Get statistics for metric."""
        if metric_name not in self.metrics:
            return {}
        
        points = self.metrics[metric_name]
        if labels:
            points = [
                p for p in points
                if all(p.labels.get(k) == v for k, v in labels.items())
            ]
        
        if not points:
            return {}
        
        values = [p.value for p in points]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
