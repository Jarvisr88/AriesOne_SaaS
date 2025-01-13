"""
Monitoring Module

This module provides monitoring and observability utilities.
"""
import logging
from typing import Any

import newrelic.agent
import sentry_sdk
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram

# Metrics
REQUEST_COUNT = Counter(
    "cmn_request_total",
    "Total CMN requests",
    ["method", "endpoint", "status"]
)

RESPONSE_TIME = Histogram(
    "cmn_response_time_seconds",
    "Response time in seconds",
    ["method", "endpoint"]
)

ERROR_COUNT = Counter(
    "cmn_error_total",
    "Total errors",
    ["type", "message"]
)

def init_monitoring(settings: Any) -> None:
    """
    Initialize monitoring tools.
    
    Args:
        settings: Application settings
    """
    # Initialize New Relic
    newrelic.agent.initialize(
        config_file="newrelic.ini",
        environment="production"
    )

    # Initialize Sentry
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0
    )

def init_tracing(settings: Any) -> None:
    """
    Initialize distributed tracing.
    
    Args:
        settings: Application settings
    """
    # Set up OpenTelemetry
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

def init_fastapi_monitoring(app: Any) -> None:
    """
    Initialize FastAPI monitoring.
    
    Args:
        app: FastAPI application instance
    """
    FastAPIInstrumentor.instrument_app(app)

def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger.
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def log_error(
    logger: logging.Logger,
    error: Exception,
    context: dict = None
) -> None:
    """
    Log error with context.
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context
    """
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    logger.error(
        "Error occurred",
        extra=error_data,
        exc_info=True
    )
    sentry_sdk.capture_exception(error)
    ERROR_COUNT.labels(
        type=error_data["error_type"],
        message=error_data["error_message"]
    ).inc()

def track_request(
    method: str,
    endpoint: str,
    status: int,
    duration: float
) -> None:
    """
    Track API request metrics.
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        status: Response status code
        duration: Request duration in seconds
    """
    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()
    RESPONSE_TIME.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)
