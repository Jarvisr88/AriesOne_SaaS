"""
Logging Infrastructure

Provides a unified logging system with structured logging and monitoring integration.
"""
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request
from loguru import logger
import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from ..config import get_settings

settings = get_settings()

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class InterceptHandler(logging.Handler):
    """
    Intercepts standard logging and redirects to loguru.
    """
    
    def emit(self, record: logging.LogRecord):
        """
        Emit log record.
        
        Args:
            record: Log record
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
            
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
            
        logger.opt(
            depth=depth,
            exception=record.exc_info
        ).log(
            level,
            record.getMessage()
        )

class LoggingManager:
    """Manages application logging."""
    
    def __init__(self, app: Optional[FastAPI] = None):
        """Initialize logging manager."""
        self.app = app
        self._setup_logging()
        if app:
            self._setup_middleware()
            self._setup_telemetry()

    def _setup_logging(self):
        """Setup logging configuration."""
        # Remove existing handlers
        logging.root.handlers = []
        
        # Set logging level
        logging.root.setLevel(settings.LOG_LEVEL)
        
        # Configure loguru
        logger.configure(
            handlers=[
                {
                    "sink": sys.stdout,
                    "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                             "<level>{level: <8}</level> | "
                             "<cyan>{name}</cyan>:<cyan>{function}</cyan>:"
                             "<cyan>{line}</cyan> - <level>{message}</level>",
                    "level": settings.LOG_LEVEL,
                    "serialize": True
                }
            ]
        )
        
        # Intercept standard logging
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        
        # Intercept uvicorn logging
        for name in ["uvicorn", "uvicorn.access"]:
            logging_logger = logging.getLogger(name)
            logging_logger.handlers = [InterceptHandler()]

    def _setup_middleware(self):
        """Setup logging middleware."""
        
        @self.app.middleware("http")
        async def logging_middleware(request: Request, call_next):
            """Log request and response."""
            start_time = datetime.utcnow()
            
            # Get request details
            request_id = request.headers.get("X-Request-ID", "")
            path = request.url.path
            method = request.method
            
            # Log request
            logger.info(
                "Request started",
                request_id=request_id,
                path=path,
                method=method
            )
            
            # Process request
            try:
                response = await call_next(request)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                # Log response
                logger.info(
                    "Request completed",
                    request_id=request_id,
                    path=path,
                    method=method,
                    status_code=response.status_code,
                    duration=duration
                )
                
                return response
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                # Log error
                logger.error(
                    "Request failed",
                    request_id=request_id,
                    path=path,
                    method=method,
                    error=str(e),
                    duration=duration,
                    exc_info=True
                )
                raise

    def _setup_telemetry(self):
        """Setup OpenTelemetry integration."""
        if settings.OTLP_ENDPOINT:
            # Configure tracer
            tracer_provider = TracerProvider(
                resource=Resource.create({
                    "service.name": settings.SERVICE_NAME,
                    "environment": settings.ENVIRONMENT
                })
            )
            
            # Configure exporter
            otlp_exporter = OTLPSpanExporter(
                endpoint=settings.OTLP_ENDPOINT
            )
            
            # Add span processor
            tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
            
            # Set tracer provider
            trace.set_tracer_provider(tracer_provider)

    def log(
        self,
        level: str,
        message: str,
        **kwargs: Any
    ):
        """
        Log message with context.
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context
        """
        log_func = getattr(logger, level.lower())
        log_func(message, **kwargs)

    def info(self, message: str, **kwargs: Any):
        """Log info message."""
        self.log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs: Any):
        """Log error message."""
        self.log("ERROR", message, **kwargs)

    def warning(self, message: str, **kwargs: Any):
        """Log warning message."""
        self.log("WARNING", message, **kwargs)

    def debug(self, message: str, **kwargs: Any):
        """Log debug message."""
        self.log("DEBUG", message, **kwargs)

    def critical(self, message: str, **kwargs: Any):
        """Log critical message."""
        self.log("CRITICAL", message, **kwargs)

logging_manager: Optional[LoggingManager] = None

def setup_logging(app: FastAPI) -> LoggingManager:
    """
    Setup logging for application.
    
    Args:
        app: FastAPI application
        
    Returns:
        Logging manager instance
    """
    global logging_manager
    if not logging_manager:
        logging_manager = LoggingManager(app)
    return logging_manager

def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return structlog.get_logger(name)
