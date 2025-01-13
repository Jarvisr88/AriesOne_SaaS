"""Database health check module.

This module provides comprehensive health checks for the database system,
including connection testing, query performance, and resource monitoring.
"""
import time
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy import text
from prometheus_client import Counter, Gauge, Histogram

from infrastructure.database import get_session, get_connection_stats

# Setup logging
logger = logging.getLogger(__name__)

# Prometheus metrics
health_check_counter = Counter(
    "db_health_checks_total",
    "Total number of health checks performed",
    ["status"]
)

connection_gauge = Gauge(
    "db_connections_current",
    "Current number of database connections",
    ["state"]
)

query_latency = Histogram(
    "db_query_latency_seconds",
    "Database query latency in seconds",
    ["query_type"]
)


async def check_connection_health() -> Dict[str, Any]:
    """Check database connection health.
    
    Performs basic connection test and collects pool statistics.
    
    Returns:
        dict: Health check results including:
            - status: Connection status
            - pool_stats: Connection pool statistics
            - latency: Connection latency
            - timestamp: Check timestamp
    """
    start_time = time.time()
    status = "healthy"
    
    try:
        # Test basic connection
        async with get_session() as session:
            await session.execute(text("SELECT 1"))
        
        # Get pool statistics
        pool_stats = await get_connection_stats()
        
        # Update metrics
        connection_gauge.labels(state="total").set(pool_stats["size"])
        connection_gauge.labels(state="in_use").set(pool_stats["checked_out"])
        health_check_counter.labels(status="success").inc()
        
        return {
            "status": status,
            "pool_stats": pool_stats,
            "latency": time.time() - start_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        status = "unhealthy"
        health_check_counter.labels(status="failure").inc()
        logger.error(f"Connection health check failed: {str(e)}")
        
        return {
            "status": status,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


async def check_query_health() -> Dict[str, Any]:
    """Check database query health.
    
    Performs test queries and measures their performance.
    
    Returns:
        dict: Query health results including:
            - status: Overall query health status
            - queries: List of query test results
            - timestamp: Check timestamp
    """
    queries = [
        ("simple_select", "SELECT 1"),
        ("count_tables", """
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """),
        ("check_indexes", """
            SELECT schemaname, tablename, indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            LIMIT 1
        """)
    ]
    
    results = []
    status = "healthy"
    
    async with get_session() as session:
        for query_type, query in queries:
            start_time = time.time()
            try:
                await session.execute(text(query))
                latency = time.time() - start_time
                
                # Record query latency
                query_latency.labels(query_type=query_type).observe(latency)
                
                results.append({
                    "query_type": query_type,
                    "status": "success",
                    "latency": latency
                })
            
            except Exception as e:
                status = "unhealthy"
                logger.error(f"Query health check failed: {str(e)}")
                results.append({
                    "query_type": query_type,
                    "status": "failure",
                    "error": str(e)
                })
    
    return {
        "status": status,
        "queries": results,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


async def check_resource_health() -> Dict[str, Any]:
    """Check database resource health.
    
    Monitors database resource usage including:
    - Table sizes
    - Index sizes
    - Buffer cache
    - Connections
    
    Returns:
        dict: Resource health data including:
            - status: Overall resource health
            - metrics: Resource usage metrics
            - timestamp: Check timestamp
    """
    resource_queries = {
        "table_sizes": """
            SELECT relname as table_name,
                   pg_size_pretty(pg_total_relation_size(relid)) as total_size,
                   pg_size_pretty(pg_table_size(relid)) as table_size,
                   pg_size_pretty(pg_indexes_size(relid)) as index_size
            FROM pg_catalog.pg_statio_user_tables
            ORDER BY pg_total_relation_size(relid) DESC
            LIMIT 5
        """,
        "connection_count": """
            SELECT count(*) as connection_count,
                   state,
                   wait_event_type
            FROM pg_stat_activity
            GROUP BY state, wait_event_type
        """,
        "cache_hit_ratio": """
            SELECT 
                sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
            FROM pg_statio_user_tables
        """
    }
    
    metrics = {}
    status = "healthy"
    
    async with get_session() as session:
        for metric_name, query in resource_queries.items():
            try:
                result = await session.execute(text(query))
                metrics[metric_name] = [dict(row) for row in result]
            except Exception as e:
                status = "unhealthy"
                logger.error(f"Resource health check failed: {str(e)}")
                metrics[metric_name] = {"error": str(e)}
    
    return {
        "status": status,
        "metrics": metrics,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


async def get_complete_health_check() -> Dict[str, Any]:
    """Get comprehensive health check results.
    
    Performs all health checks and returns combined results.
    
    Returns:
        dict: Complete health check results
    """
    connection_health = await check_connection_health()
    query_health = await check_query_health()
    resource_health = await check_resource_health()
    
    overall_status = "healthy"
    if any(check["status"] == "unhealthy" for check in [
        connection_health,
        query_health,
        resource_health
    ]):
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "connection": connection_health,
            "query": query_health,
            "resource": resource_health
        }
    }
