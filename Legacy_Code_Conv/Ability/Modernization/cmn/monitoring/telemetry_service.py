"""
Telemetry Service Module

Handles monitoring, metrics collection, and logging for network operations.
"""
from datetime import datetime
import json
from typing import Any, Dict, Optional
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from prometheus_client import Counter, Histogram, Gauge
import structlog

from ..config import get_settings

settings = get_settings()

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Initialize metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=settings.OTLP_ENDPOINT)
)
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# Initialize Prometheus metrics
REQUEST_COUNT = Counter(
    "network_requests_total",
    "Total number of network requests",
    ["endpoint", "method", "status"]
)

LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["endpoint", "method"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active network connections",
    ["endpoint"]
)

CIRCUIT_BREAKER_STATUS = Gauge(
    "circuit_breaker_status",
    "Circuit breaker status (0=open, 1=closed)",
    ["endpoint"]
)

class TelemetryService:
    """Service for handling telemetry and monitoring."""

    def __init__(self):
        """Initialize telemetry service."""
        # Configure structured logging
        self.logger = structlog.get_logger()
        
        # Initialize OpenTelemetry span processor
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT)
        )
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Create metrics
        self.request_counter = meter.create_counter(
            "network.requests",
            description="Number of network requests"
        )
        
        self.request_duration = meter.create_histogram(
            "network.request.duration",
            description="Duration of network requests",
            unit="ms"
        )
        
        self.error_counter = meter.create_counter(
            "network.errors",
            description="Number of network errors"
        )

    async def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration: float
    ):
        """Record metrics for a network request."""
        # Update Prometheus metrics
        REQUEST_COUNT.labels(
            endpoint=endpoint,
            method=method,
            status=status_code
        ).inc()
        
        LATENCY.labels(
            endpoint=endpoint,
            method=method
        ).observe(duration)
        
        # Update OpenTelemetry metrics
        self.request_counter.add(
            1,
            {"endpoint": endpoint, "method": method, "status": status_code}
        )
        
        self.request_duration.record(
            duration * 1000,  # Convert to milliseconds
            {"endpoint": endpoint, "method": method}
        )
        
        if status_code >= 400:
            self.error_counter.add(
                1,
                {"endpoint": endpoint, "status": status_code}
            )

    async def update_connection_count(self, endpoint: str, count: int):
        """Update active connection count."""
        ACTIVE_CONNECTIONS.labels(endpoint=endpoint).set(count)

    async def update_circuit_breaker(self, endpoint: str, is_open: bool):
        """Update circuit breaker status."""
        CIRCUIT_BREAKER_STATUS.labels(endpoint=endpoint).set(0 if is_open else 1)

    async def log_event(
        self,
        event_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an event with structured data."""
        log_data = {
            "event": event_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "network"
        }
        
        if metadata:
            log_data.update(metadata)
            
        self.logger.info(
            event_type,
            **log_data
        )

    async def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, str]] = None
    ) -> trace.Span:
        """Start a new trace span."""
        return tracer.start_span(
            name,
            attributes=attributes or {}
        )

    def get_current_span(self) -> Optional[trace.Span]:
        """Get the current trace span."""
        return trace.get_current_span()

    async def record_exception(
        self,
        exception: Exception,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record an exception with metadata."""
        span = self.get_current_span()
        if span:
            span.record_exception(exception)
            
        log_data = {
            "event": "exception",
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "network"
        }
        
        if metadata:
            log_data.update(metadata)
            
        self.logger.error(
            "exception_occurred",
            **log_data
        )

telemetry_service = TelemetryService()
