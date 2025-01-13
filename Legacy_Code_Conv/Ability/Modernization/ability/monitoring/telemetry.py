"""
Telemetry Module

This module handles monitoring, metrics, and logging for the Ability module.
"""
import logging
from datetime import datetime
from typing import Dict, Optional

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram, Gauge

from ..config import Settings


class TelemetryService:
    """Service for handling telemetry data."""

    def __init__(self, settings: Settings):
        """Initialize telemetry service."""
        self.settings = settings
        self._setup_tracing()
        self._setup_metrics()
        self._setup_logging()

    def _setup_tracing(self):
        """Set up OpenTelemetry tracing."""
        resource = Resource.create({"service.name": "ability-service"})
        tracer_provider = TracerProvider(resource=resource)
        
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.settings.otlp_endpoint,
            insecure=not self.settings.otlp_secure
        )
        
        tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        
        trace.set_tracer_provider(tracer_provider)
        self.tracer = trace.get_tracer(__name__)

    def _setup_metrics(self):
        """Set up Prometheus metrics."""
        self.eligibility_requests = Counter(
            'eligibility_requests_total',
            'Total number of eligibility requests',
            ['payer_type', 'status']
        )
        
        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration in seconds',
            ['payer_type', 'endpoint']
        )
        
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections',
            ['payer_type']
        )

    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=self.settings.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def record_request(
        self,
        payer_type: str,
        endpoint: str,
        duration: float,
        status: str
    ):
        """Record a request metric."""
        self.eligibility_requests.labels(
            payer_type=payer_type,
            status=status
        ).inc()
        
        self.request_duration.labels(
            payer_type=payer_type,
            endpoint=endpoint
        ).observe(duration)

    async def update_connections(self, payer_type: str, count: int):
        """Update active connection count."""
        self.active_connections.labels(payer_type=payer_type).set(count)

    async def log_error(
        self,
        error_type: str,
        message: str,
        details: Optional[Dict] = None
    ):
        """Log an error with details."""
        self.logger.error(
            f"Error: {error_type} - {message}",
            extra={"details": details or {}}
        )

    async def create_span(
        self,
        name: str,
        attributes: Optional[Dict] = None
    ) -> trace.Span:
        """Create a new trace span."""
        return self.tracer.start_span(
            name,
            attributes=attributes or {}
        )

    async def get_metrics(self) -> Dict:
        """Get current metrics."""
        return {
            "timestamp": datetime.utcnow(),
            "metrics": {
                "requests": {
                    payer_type: self.eligibility_requests.labels(
                        payer_type=payer_type,
                        status="success"
                    )._value.get()
                    for payer_type in ["medicare", "medicaid", "private"]
                },
                "active_connections": {
                    payer_type: self.active_connections.labels(
                        payer_type=payer_type
                    )._value.get()
                    for payer_type in ["medicare", "medicaid", "private"]
                }
            }
        }
