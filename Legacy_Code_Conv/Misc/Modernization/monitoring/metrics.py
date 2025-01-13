"""
Metrics collection and monitoring.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary
)


# API metrics
API_REQUEST_COUNT = Counter(
    "misc_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"]
)

API_REQUEST_LATENCY = Histogram(
    "misc_api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"]
)

API_REQUEST_IN_PROGRESS = Gauge(
    "misc_api_requests_in_progress",
    "Requests currently in progress",
    ["method", "endpoint"]
)

API_REQUEST_SIZE = Summary(
    "misc_api_request_size_bytes",
    "Request size in bytes",
    ["method", "endpoint"]
)

# Business metrics
DEPOSIT_AMOUNT = Counter(
    "misc_deposit_amount_total",
    "Total deposit amount",
    ["customer_id", "payment_method"]
)

VOID_COUNT = Counter(
    "misc_void_count_total",
    "Total void count",
    ["action", "status"]
)

PURCHASE_ORDER_VALUE = Counter(
    "misc_purchase_order_value_total",
    "Total purchase order value",
    ["vendor_id", "status"]
)

PURCHASE_ORDER_ITEMS = Counter(
    "misc_purchase_order_items_total",
    "Total purchase order items",
    ["vendor_id", "status"]
)

# Performance metrics
DB_QUERY_LATENCY = Histogram(
    "misc_db_query_duration_seconds",
    "Database query duration",
    ["operation", "table"]
)

CACHE_HIT_COUNT = Counter(
    "misc_cache_hits_total",
    "Cache hit count",
    ["cache_type"]
)

CACHE_MISS_COUNT = Counter(
    "misc_cache_misses_total",
    "Cache miss count",
    ["cache_type"]
)

# Resource metrics
MEMORY_USAGE = Gauge(
    "misc_memory_usage_bytes",
    "Memory usage in bytes"
)

CPU_USAGE = Gauge(
    "misc_cpu_usage_percent",
    "CPU usage percentage"
)

DISK_USAGE = Gauge(
    "misc_disk_usage_bytes",
    "Disk usage in bytes",
    ["path"]
)


class MetricsService:
    """Service for collecting and managing metrics."""

    @classmethod
    def track_api_request(
        cls,
        method: str,
        endpoint: str,
        status: int,
        duration: float,
        size: int
    ):
        """Track API request metrics.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            status: Response status code
            duration: Request duration in seconds
            size: Request size in bytes
        """
        # Update request count
        API_REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        # Update latency
        API_REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        # Update request size
        API_REQUEST_SIZE.labels(
            method=method,
            endpoint=endpoint
        ).observe(size)

    @classmethod
    def track_deposit(
        cls,
        customer_id: int,
        payment_method: str,
        amount: float
    ):
        """Track deposit metrics.
        
        Args:
            customer_id: Customer identifier
            payment_method: Payment method
            amount: Deposit amount
        """
        DEPOSIT_AMOUNT.labels(
            customer_id=str(customer_id),
            payment_method=payment_method
        ).inc(amount)

    @classmethod
    def track_void(
        cls,
        action: str,
        status: str
    ):
        """Track void metrics.
        
        Args:
            action: Void action
            status: Void status
        """
        VOID_COUNT.labels(
            action=action,
            status=status
        ).inc()

    @classmethod
    def track_purchase_order(
        cls,
        vendor_id: int,
        status: str,
        value: float,
        item_count: int
    ):
        """Track purchase order metrics.
        
        Args:
            vendor_id: Vendor identifier
            status: Order status
            value: Order value
            item_count: Number of items
        """
        # Track value
        PURCHASE_ORDER_VALUE.labels(
            vendor_id=str(vendor_id),
            status=status
        ).inc(value)
        
        # Track items
        PURCHASE_ORDER_ITEMS.labels(
            vendor_id=str(vendor_id),
            status=status
        ).inc(item_count)

    @classmethod
    def track_db_query(
        cls,
        operation: str,
        table: str,
        duration: float
    ):
        """Track database query metrics.
        
        Args:
            operation: Query operation
            table: Database table
            duration: Query duration in seconds
        """
        DB_QUERY_LATENCY.labels(
            operation=operation,
            table=table
        ).observe(duration)

    @classmethod
    def track_cache(
        cls,
        cache_type: str,
        hit: bool
    ):
        """Track cache metrics.
        
        Args:
            cache_type: Type of cache
            hit: Whether cache hit
        """
        if hit:
            CACHE_HIT_COUNT.labels(
                cache_type=cache_type
            ).inc()
        else:
            CACHE_MISS_COUNT.labels(
                cache_type=cache_type
            ).inc()

    @classmethod
    def update_resource_usage(
        cls,
        memory_bytes: int,
        cpu_percent: float,
        disk_usage: Dict[str, int]
    ):
        """Update resource usage metrics.
        
        Args:
            memory_bytes: Memory usage in bytes
            cpu_percent: CPU usage percentage
            disk_usage: Disk usage by path
        """
        # Update memory usage
        MEMORY_USAGE.set(memory_bytes)
        
        # Update CPU usage
        CPU_USAGE.set(cpu_percent)
        
        # Update disk usage
        for path, usage in disk_usage.items():
            DISK_USAGE.labels(path=path).set(usage)
