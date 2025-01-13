"""
Monitoring service for system health and performance.
"""
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime, timedelta
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    CollectorRegistry,
    push_to_gateway
)
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import aiohttp
from .config import settings


# Initialize metrics
REGISTRY = CollectorRegistry()

# System metrics
SYSTEM_UP = Gauge(
    'system_up',
    'System uptime in seconds',
    registry=REGISTRY
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage',
    registry=REGISTRY
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    registry=REGISTRY
)

# API metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Business metrics
STORAGE_QUOTA = Gauge(
    'storage_quota_bytes',
    'Storage quota by company',
    ['company_id'],
    registry=REGISTRY
)

ERROR_RATE = Summary(
    'error_rate_percent',
    'Error rate percentage',
    ['type'],
    registry=REGISTRY
)


class MonitoringService:
    """Manages system monitoring and alerts."""
    
    def __init__(self):
        """Initialize monitoring service."""
        self.logger = logging.getLogger(__name__)
        self.tracer = trace.get_tracer(__name__)
        
    async def start_monitoring(self):
        """Start monitoring tasks."""
        try:
            # Start background tasks
            asyncio.create_task(
                self._collect_system_metrics()
            )
            asyncio.create_task(
                self._check_service_health()
            )
            asyncio.create_task(
                self._monitor_quotas()
            )
            
            # Initialize tracing
            self._setup_tracing()
            
        except Exception as e:
            self.logger.error(f"Monitoring startup error: {str(e)}")
            
    async def _collect_system_metrics(
        self,
        interval: int = 60
    ):
        """Collect system metrics.
        
        Args:
            interval: Collection interval in seconds
        """
        while True:
            try:
                # Update system metrics
                SYSTEM_UP.set(
                    (datetime.utcnow() - settings.START_TIME)
                    .total_seconds()
                )
                
                # Get CPU usage
                cpu = await self._get_cpu_usage()
                CPU_USAGE.set(cpu)
                
                # Get memory usage
                memory = await self._get_memory_usage()
                MEMORY_USAGE.set(memory)
                
                # Push to Prometheus
                push_to_gateway(
                    settings.PROMETHEUS_GATEWAY,
                    job='imaging_service',
                    registry=REGISTRY
                )
                
            except Exception as e:
                self.logger.error(
                    f"Metric collection error: {str(e)}"
                )
                
            await asyncio.sleep(interval)
            
    async def _check_service_health(
        self,
        interval: int = 30
    ):
        """Check service health.
        
        Args:
            interval: Check interval in seconds
        """
        while True:
            try:
                # Check dependencies
                results = await asyncio.gather(
                    self._check_storage(),
                    self._check_cache(),
                    self._check_search(),
                    return_exceptions=True
                )
                
                # Process results
                for i, result in enumerate(results):
                    service = [
                        "storage",
                        "cache",
                        "search"
                    ][i]
                    
                    if isinstance(result, Exception):
                        self.logger.error(
                            f"{service} health check failed: {str(result)}"
                        )
                        await self._send_alert(
                            f"{service}_health_check_failed",
                            str(result)
                        )
                    else:
                        self.logger.info(
                            f"{service} health check passed"
                        )
                        
            except Exception as e:
                self.logger.error(
                    f"Health check error: {str(e)}"
                )
                
            await asyncio.sleep(interval)
            
    async def _monitor_quotas(
        self,
        interval: int = 300
    ):
        """Monitor storage quotas.
        
        Args:
            interval: Check interval in seconds
        """
        while True:
            try:
                # Get company quotas
                quotas = await self._get_company_quotas()
                
                for company_id, quota in quotas.items():
                    # Update metric
                    STORAGE_QUOTA.labels(
                        company_id=str(company_id)
                    ).set(quota["used"])
                    
                    # Check threshold
                    if quota["used"] / quota["total"] > 0.9:
                        await self._send_alert(
                            "quota_near_limit",
                            f"Company {company_id} at {quota['used']} bytes"
                        )
                        
            except Exception as e:
                self.logger.error(
                    f"Quota monitoring error: {str(e)}"
                )
                
            await asyncio.sleep(interval)
            
    async def _send_alert(
        self,
        alert_type: str,
        message: str
    ):
        """Send monitoring alert.
        
        Args:
            alert_type: Type of alert
            message: Alert message
        """
        try:
            # Prepare payload
            payload = {
                "type": alert_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "imaging",
                "environment": settings.ENVIRONMENT
            }
            
            # Send to alert service
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.ALERT_WEBHOOK_URL,
                    json=payload
                ) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"Alert sending failed: {await response.text()}"
                        )
                        
        except Exception as e:
            self.logger.error(f"Alert error: {str(e)}")
            
    def _setup_tracing(self):
        """Set up OpenTelemetry tracing."""
        try:
            # Initialize FastAPI instrumentation
            FastAPIInstrumentor.instrument(
                excluded_urls="health,metrics",
                trace_internal_requests=True
            )
            
        except Exception as e:
            self.logger.error(f"Tracing setup error: {str(e)}")
            
    async def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage.
        
        Returns:
            CPU usage percentage
        """
        try:
            # Read /proc/stat
            with open('/proc/stat', 'r') as f:
                cpu = f.readline().split()
                
            # Calculate usage
            total = sum(float(x) for x in cpu[1:])
            idle = float(cpu[4])
            
            return 100 * (1 - idle / total)
            
        except Exception:
            return 0.0
            
    async def _get_memory_usage(self) -> int:
        """Get memory usage in bytes.
        
        Returns:
            Memory usage in bytes
        """
        try:
            # Read /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                
            # Parse memory info
            mem_total = int(lines[0].split()[1]) * 1024
            mem_free = int(lines[1].split()[1]) * 1024
            mem_available = int(lines[2].split()[1]) * 1024
            
            return mem_total - mem_available
            
        except Exception:
            return 0
            
    async def _check_storage(self) -> bool:
        """Check storage service health.
        
        Returns:
            True if healthy
            
        Raises:
            Exception: If health check fails
        """
        # Implement storage health check
        pass
        
    async def _check_cache(self) -> bool:
        """Check cache service health.
        
        Returns:
            True if healthy
            
        Raises:
            Exception: If health check fails
        """
        # Implement cache health check
        pass
        
    async def _check_search(self) -> bool:
        """Check search service health.
        
        Returns:
            True if healthy
            
        Raises:
            Exception: If health check fails
        """
        # Implement search health check
        pass
        
    async def _get_company_quotas(self) -> Dict[int, Dict[str, int]]:
        """Get company storage quotas.
        
        Returns:
            Dictionary of company quotas
        """
        # Implement quota retrieval
        pass
