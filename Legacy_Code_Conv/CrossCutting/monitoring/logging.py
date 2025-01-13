"""Logging configuration module."""

import sys
import json
import logging
import logging.config
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import structlog
from app.core.config import settings

def configure_logging() -> None:
    """Configure logging system."""
    # Create logs directory
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "json_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "app.json",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "json",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "error.json",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "json",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "json_file"],
                "level": settings.LOG_LEVEL,
            },
            "error": {
                "handlers": ["error_file"],
                "level": "ERROR",
                "propagate": False,
            },
        },
    }
    
    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

class RequestLogger:
    """Logger for HTTP requests."""
    
    def __init__(self):
        """Initialize request logger."""
        self.logger = structlog.get_logger("request")
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Log HTTP request."""
        self.logger.info(
            "http_request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            **kwargs
        )

class AuditLogger:
    """Logger for audit events."""
    
    def __init__(self):
        """Initialize audit logger."""
        self.logger = structlog.get_logger("audit")
    
    def log_event(
        self,
        event_type: str,
        user_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log audit event."""
        self.logger.info(
            "audit_event",
            event_type=event_type,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            metadata=metadata,
            timestamp=datetime.utcnow().isoformat()
        )

class ErrorLogger:
    """Logger for errors and exceptions."""
    
    def __init__(self):
        """Initialize error logger."""
        self.logger = structlog.get_logger("error")
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> None:
        """Log error event."""
        self.logger.error(
            "error_occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            user_id=user_id,
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat(),
            exc_info=True
        )

class PerformanceLogger:
    """Logger for performance metrics."""
    
    def __init__(self):
        """Initialize performance logger."""
        self.logger = structlog.get_logger("performance")
    
    def log_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log performance metric."""
        self.logger.info(
            "performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            context=context,
            timestamp=datetime.utcnow().isoformat()
        )
