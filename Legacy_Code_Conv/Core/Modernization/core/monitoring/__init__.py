"""
Core Monitoring Package
Version: 1.0.0
Last Updated: 2025-01-10

This package provides monitoring functionality for the core module.
"""

from .alerts import Alert, AlertManager, AlertSeverity, AlertChannel, get_alert_manager
from .health import HealthCheck, get_health_check
from .metrics import (MetricsCollector, track_request_metrics, track_db_metrics,
                     REQUEST_LATENCY, REQUEST_COUNT, DB_CONNECTION_POOL,
                     DB_QUERY_LATENCY, CACHE_HITS, CACHE_MISSES, ACTIVE_USERS,
                     ERROR_COUNT, MEMORY_USAGE, CPU_USAGE)

__all__ = [
    # Alerts
    'Alert',
    'AlertManager',
    'AlertSeverity',
    'AlertChannel',
    'get_alert_manager',
    
    # Health Checks
    'HealthCheck',
    'get_health_check',
    
    # Metrics
    'MetricsCollector',
    'track_request_metrics',
    'track_db_metrics',
    'REQUEST_LATENCY',
    'REQUEST_COUNT',
    'DB_CONNECTION_POOL',
    'DB_QUERY_LATENCY',
    'CACHE_HITS',
    'CACHE_MISSES',
    'ACTIVE_USERS',
    'ERROR_COUNT',
    'MEMORY_USAGE',
    'CPU_USAGE'
]
