"""Database monitoring module.

This module provides database monitoring functionality including:
- Metric collection
- Performance tracking
- Error logging
- Dashboard integration
"""
import time
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy import text
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary
)

from infrastructure.database import get_session

# Setup logging
logger = logging.getLogger(__name__)

# Prometheus metrics
query_counter = Counter(
    "db_queries_total",
    "Total number of database queries",
    ["query_type", "status"]
)

query_duration = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type"]
)

connection_errors = Counter(
    "db_connection_errors_total",
    "Total number of database connection errors",
    ["error_type"]
)

active_transactions = Gauge(
    "db_active_transactions",
    "Number of active database transactions"
)

table_size = Gauge(
    "db_table_size_bytes",
    "Size of database tables in bytes",
    ["table_name"]
)

query_rows = Summary(
    "db_query_rows",
    "Number of rows processed by queries",
    ["query_type"]
)


class DatabaseMonitor:
    """Database monitoring class."""
    
    def __init__(self):
        """Initialize database monitor."""
        self.start_time = time.time()
    
    async def collect_table_metrics(self) -> Dict[str, Any]:
        """Collect table metrics.
        
        Returns:
            dict: Table metrics including:
                - sizes: Table sizes
                - row_counts: Table row counts
                - timestamp: Collection timestamp
        """
        metrics = {}
        
        table_queries = {
            "sizes": """
                SELECT relname as table_name,
                       pg_total_relation_size(relid) as total_size,
                       pg_table_size(relid) as table_size,
                       pg_indexes_size(relid) as index_size
                FROM pg_catalog.pg_statio_user_tables
            """,
            "row_counts": """
                SELECT relname as table_name,
                       n_live_tup as row_count
                FROM pg_stat_user_tables
            """
        }
        
        try:
            async with get_session() as session:
                for metric_name, query in table_queries.items():
                    result = await session.execute(text(query))
                    metrics[metric_name] = [dict(row) for row in result]
                    
                    # Update Prometheus metrics
                    if metric_name == "sizes":
                        for row in metrics[metric_name]:
                            table_size.labels(
                                table_name=row["table_name"]
                            ).set(row["total_size"])
            
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to collect table metrics: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics.
        
        Returns:
            dict: Performance metrics including:
                - query_stats: Query statistics
                - index_stats: Index usage statistics
                - timestamp: Collection timestamp
        """
        metrics = {}
        
        performance_queries = {
            "query_stats": """
                SELECT datname,
                       calls,
                       total_exec_time,
                       rows,
                       query
                FROM pg_stat_statements
                JOIN pg_database
                ON pg_stat_statements.dbid = pg_database.oid
                ORDER BY total_exec_time DESC
                LIMIT 10
            """,
            "index_stats": """
                SELECT schemaname,
                       relname as table_name,
                       indexrelname as index_name,
                       idx_scan,
                       idx_tup_read,
                       idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
                LIMIT 10
            """
        }
        
        try:
            async with get_session() as session:
                for metric_name, query in performance_queries.items():
                    result = await session.execute(text(query))
                    metrics[metric_name] = [dict(row) for row in result]
            
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def collect_error_metrics(self) -> Dict[str, Any]:
        """Collect error metrics.
        
        Returns:
            dict: Error metrics including:
                - deadlocks: Deadlock statistics
                - errors: Error statistics
                - timestamp: Collection timestamp
        """
        metrics = {}
        
        error_queries = {
            "deadlocks": """
                SELECT datname,
                       deadlocks,
                       conflicts,
                       temp_files
                FROM pg_stat_database
            """,
            "errors": """
                SELECT state,
                       wait_event_type,
                       wait_event,
                       count(*)
                FROM pg_stat_activity
                WHERE state = 'active'
                GROUP BY state, wait_event_type, wait_event
            """
        }
        
        try:
            async with get_session() as session:
                for metric_name, query in error_queries.items():
                    result = await session.execute(text(query))
                    metrics[metric_name] = [dict(row) for row in result]
            
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to collect error metrics: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all database metrics.
        
        Returns:
            dict: All metrics including:
                - tables: Table metrics
                - performance: Performance metrics
                - errors: Error metrics
                - uptime: Monitor uptime
                - timestamp: Collection timestamp
        """
        table_metrics = await self.collect_table_metrics()
        performance_metrics = await self.collect_performance_metrics()
        error_metrics = await self.collect_error_metrics()
        
        return {
            "status": "success" if all(
                m["status"] == "success" for m in [
                    table_metrics,
                    performance_metrics,
                    error_metrics
                ]
            ) else "partial_failure",
            "metrics": {
                "tables": table_metrics.get("metrics", {}),
                "performance": performance_metrics.get("metrics", {}),
                "errors": error_metrics.get("metrics", {}),
                "uptime": time.time() - self.start_time
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
