"""Logging configuration module."""

import logging
import sys
from typing import Any, Dict
from loguru import logger
from ..config.settings import get_settings

settings = get_settings()

class InterceptHandler(logging.Handler):
    """Intercept standard logging messages toward Loguru."""
    
    def emit(self, record: logging.LogRecord) -> None:
        """Intercept log records."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging() -> None:
    """Configure logging."""
    # Remove default loguru handler
    logger.remove()
    
    # Configure loguru handler
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.LOG_LEVEL,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler if configured
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            format=log_format,
            level=settings.LOG_LEVEL,
            rotation="00:00",  # Rotate daily
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress rotated files
        )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Update external loggers
    for logger_name in (
        "uvicorn",
        "uvicorn.error",
        "fastapi",
        "sqlalchemy",
        "alembic",
    ):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]

def get_logger() -> Any:
    """Get logger instance."""
    return logger
