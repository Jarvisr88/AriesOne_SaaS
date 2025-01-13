"""
Core Logging Utility Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides logging utilities for the core module.
"""
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from .config import get_settings

settings = get_settings()


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = str(record.user_id)
        
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = str(record.correlation_id)
            
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        return json.dumps(log_data)


class CoreLogger:
    """Core logger with structured logging capabilities."""
    
    def __init__(self, name: str):
        """Initialize logger with name."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(console_handler)
        
        # Add file handler if configured
        if settings.LOG_FILE:
            file_handler = logging.FileHandler(settings.LOG_FILE)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def _log(self, level: int, msg: str, *args: Any,
             user_id: Optional[UUID] = None,
             correlation_id: Optional[UUID] = None,
             extra: Optional[Dict[str, Any]] = None,
             exc_info: Optional[Exception] = None) -> None:
        """Internal logging method."""
        extra_data = extra or {}
        if user_id:
            extra_data['user_id'] = user_id
        if correlation_id:
            extra_data['correlation_id'] = correlation_id
            
        self.logger.log(level, msg, *args, extra={'extra_data': extra_data}, exc_info=exc_info)
    
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, msg, *args, **kwargs)
    
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log exception with traceback."""
        kwargs['exc_info'] = sys.exc_info()
        self._log(logging.ERROR, msg, *args, **kwargs)
