from typing import Any, Callable, Dict, List, Optional
from functools import wraps
import time
import asyncio
from datetime import datetime
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
from redis import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics"""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.metrics_prefix = "metrics:"

    async def record_timing(
        self,
        metric_name: str,
        duration: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record timing metric"""
        key = f"{self.metrics_prefix}{metric_name}"
        pipe = self.redis.pipeline()
        
        # Update average
        pipe.incr(f"{key}:count")
        pipe.incrbyfloat(f"{key}:total", duration)
        
        # Store in time series
        timestamp = int(time.time())
        pipe.zadd(f"{key}:timeseries", {f"{timestamp}:{duration}": timestamp})
        
        # Trim time series to last 24 hours
        pipe.zremrangebyscore(
            f"{key}:timeseries",
            0,
            timestamp - 86400
        )
        
        if tags:
            # Store tagged metrics
            for tag_name, tag_value in tags.items():
                tagged_key = f"{key}:{tag_name}:{tag_value}"
                pipe.incr(f"{tagged_key}:count")
                pipe.incrbyfloat(f"{tagged_key}:total", duration)
                
        pipe.execute()

    async def get_metrics(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """Get metrics for specified time range"""
        key = f"{self.metrics_prefix}{metric_name}"
        
        # Get basic stats
        pipe = self.redis.pipeline()
        pipe.get(f"{key}:count")
        pipe.get(f"{key}:total")
        count, total = pipe.execute()
        
        count = int(count or 0)
        total = float(total or 0)
        avg = total / count if count > 0 else 0
        
        # Get time series data
        timeseries_key = f"{key}:timeseries"
        if start_time and end_time:
            data = self.redis.zrangebyscore(
                timeseries_key,
                start_time.timestamp(),
                end_time.timestamp()
            )
        else:
            data = self.redis.zrange(timeseries_key, 0, -1)
            
        # Parse time series data
        series = []
        for item in data:
            timestamp, value = item.decode().split(":")
            series.append({
                "timestamp": int(timestamp),
                "value": float(value)
            })
            
        return {
            "count": count,
            "total": total,
            "average": avg,
            "series": series
        }

def timing_decorator(metric_name: str):
    """Decorator to measure function execution time"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                monitor = PerformanceMonitor(settings.redis_client)
                await monitor.record_timing(metric_name, duration)
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                monitor = PerformanceMonitor(settings.redis_client)
                asyncio.create_task(
                    monitor.record_timing(metric_name, duration)
                )
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class QueryOptimizer:
    """Optimize database queries"""

    def __init__(self, db: Session):
        self.db = db

    async def analyze_query(self, query: str) -> dict:
        """Analyze query execution plan"""
        result = self.db.execute(
            text(f"EXPLAIN ANALYZE {query}")
        )
        return self._parse_explain_output(result.fetchall())

    def _parse_explain_output(self, explain_rows: List[tuple]) -> dict:
        """Parse EXPLAIN ANALYZE output"""
        return {
            "plan": [row[0] for row in explain_rows],
            "execution_time": self._extract_execution_time(explain_rows)
        }

    def _extract_execution_time(self, explain_rows: List[tuple]) -> float:
        """Extract execution time from EXPLAIN output"""
        for row in explain_rows:
            if "Execution Time:" in row[0]:
                return float(row[0].split(":")[1].strip().split(" ")[0])
        return 0.0

    async def optimize_query(self, query: str) -> str:
        """Suggest query optimizations"""
        analysis = await self.analyze_query(query)
        suggestions = []

        # Check for sequential scans
        if any("Seq Scan" in plan for plan in analysis["plan"]):
            suggestions.append("Consider adding indexes to avoid sequential scans")

        # Check for high execution time
        if analysis["execution_time"] > 1000:  # 1 second
            suggestions.append("Query execution time is high. Consider optimization")

        return "\n".join(suggestions)

class LoadBalancer:
    """Simple load balancer for distributed operations"""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.servers_key = "load_balancer:servers"
        self.stats_key = "load_balancer:stats"

    async def register_server(
        self,
        server_id: str,
        capacity: int = 100
    ) -> None:
        """Register a server with its capacity"""
        self.redis.hset(
            self.servers_key,
            server_id,
            json.dumps({
                "capacity": capacity,
                "current_load": 0,
                "last_heartbeat": time.time()
            })
        )

    async def update_server_load(
        self,
        server_id: str,
        load: int
    ) -> None:
        """Update server's current load"""
        server_data = json.loads(
            self.redis.hget(self.servers_key, server_id) or "{}"
        )
        server_data.update({
            "current_load": load,
            "last_heartbeat": time.time()
        })
        self.redis.hset(
            self.servers_key,
            server_id,
            json.dumps(server_data)
        )

    async def get_best_server(self) -> Optional[str]:
        """Get server with lowest load"""
        servers = self.redis.hgetall(self.servers_key)
        if not servers:
            return None

        best_server = None
        lowest_load = float('inf')

        for server_id, server_data in servers.items():
            data = json.loads(server_data)
            
            # Skip servers that haven't sent heartbeat in 30 seconds
            if time.time() - data["last_heartbeat"] > 30:
                continue
                
            load_percentage = data["current_load"] / data["capacity"]
            if load_percentage < lowest_load:
                lowest_load = load_percentage
                best_server = server_id.decode()

        return best_server

    async def record_request(
        self,
        server_id: str,
        duration: float
    ) -> None:
        """Record request statistics"""
        pipe = self.redis.pipeline()
        
        # Update request count
        pipe.hincrby(f"{self.stats_key}:requests", server_id, 1)
        
        # Update total duration
        pipe.hincrbyfloat(
            f"{self.stats_key}:duration",
            server_id,
            duration
        )
        
        pipe.execute()

    async def get_stats(self) -> dict:
        """Get load balancer statistics"""
        stats = {}
        
        # Get server information
        servers = self.redis.hgetall(self.servers_key)
        for server_id, server_data in servers.items():
            server_id = server_id.decode()
            data = json.loads(server_data)
            
            requests = int(
                self.redis.hget(f"{self.stats_key}:requests", server_id) or 0
            )
            duration = float(
                self.redis.hget(f"{self.stats_key}:duration", server_id) or 0
            )
            
            stats[server_id] = {
                "capacity": data["capacity"],
                "current_load": data["current_load"],
                "total_requests": requests,
                "average_duration": duration / requests if requests > 0 else 0
            }
            
        return stats
