"""Health check module."""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import asyncio
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.orm import Session
from redis import Redis
from aio_pika import connect_robust
from app.core.config import settings

class HealthStatus(str, Enum):
    """Health status enum."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck(BaseModel):
    """Health check model."""
    
    name: str
    status: HealthStatus
    details: Optional[Dict[str, Any]] = None
    last_check: datetime
    latency_ms: float

class HealthChecker:
    """Service for health checks."""
    
    def __init__(self):
        """Initialize health checker."""
        self.checks: List[Callable] = []
        self.results: Dict[str, HealthCheck] = {}
    
    async def check_database(self, db: Session) -> HealthCheck:
        """Check database health."""
        start_time = datetime.utcnow()
        try:
            # Execute simple query
            db.execute("SELECT 1")
            status = HealthStatus.HEALTHY
            details = {"connected": True}
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            details = {
                "error": str(e),
                "connected": False
            }
        
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return HealthCheck(
            name="database",
            status=status,
            details=details,
            last_check=start_time,
            latency_ms=latency
        )
    
    async def check_redis(self, redis: Redis) -> HealthCheck:
        """Check Redis health."""
        start_time = datetime.utcnow()
        try:
            # Test connection
            redis.ping()
            status = HealthStatus.HEALTHY
            details = {
                "connected": True,
                "used_memory": redis.info()["used_memory_human"]
            }
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            details = {
                "error": str(e),
                "connected": False
            }
        
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return HealthCheck(
            name="redis",
            status=status,
            details=details,
            last_check=start_time,
            latency_ms=latency
        )
    
    async def check_rabbitmq(self) -> HealthCheck:
        """Check RabbitMQ health."""
        start_time = datetime.utcnow()
        try:
            # Test connection
            connection = await connect_robust(settings.RABBITMQ_URL)
            await connection.close()
            status = HealthStatus.HEALTHY
            details = {"connected": True}
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            details = {
                "error": str(e),
                "connected": False
            }
        
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return HealthCheck(
            name="rabbitmq",
            status=status,
            details=details,
            last_check=start_time,
            latency_ms=latency
        )
    
    async def check_disk_space(self) -> HealthCheck:
        """Check disk space."""
        start_time = datetime.utcnow()
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            percent_used = disk.percent
            
            if percent_used >= 90:
                status = HealthStatus.UNHEALTHY
            elif percent_used >= 80:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            details = {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent_used": percent_used
            }
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            details = {"error": str(e)}
        
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return HealthCheck(
            name="disk_space",
            status=status,
            details=details,
            last_check=start_time,
            latency_ms=latency
        )
    
    async def check_memory(self) -> HealthCheck:
        """Check memory usage."""
        start_time = datetime.utcnow()
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            if percent_used >= 90:
                status = HealthStatus.UNHEALTHY
            elif percent_used >= 80:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            details = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "percent_used": percent_used
            }
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            details = {"error": str(e)}
        
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return HealthCheck(
            name="memory",
            status=status,
            details=details,
            last_check=start_time,
            latency_ms=latency
        )
    
    async def check_all(self) -> Dict[str, HealthCheck]:
        """Run all health checks."""
        tasks = [
            self.check_database(settings.DB_SESSION),
            self.check_redis(settings.REDIS_CLIENT),
            self.check_rabbitmq(),
            self.check_disk_space(),
            self.check_memory()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                continue
            self.results[result.name] = result
        
        return self.results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        if not self.results:
            return HealthStatus.UNHEALTHY
        
        statuses = [check.status for check in self.results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
