"""
Logging and monitoring module.
"""
import logging
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import Request, Response
from pydantic import BaseModel
from ..Config.config_manager import ConfigManager

class LogEntry(BaseModel):
    """Log entry model."""
    timestamp: str
    level: str
    message: str
    module: str
    function: str
    line: int
    user: Optional[str] = None
    request_id: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

class PerformanceMetrics(BaseModel):
    """Performance metrics model."""
    request_id: str
    endpoint: str
    method: str
    start_time: float
    duration: float
    status_code: int
    user: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

class Logger:
    """Handle application logging and monitoring."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.load_config()
        self.log_dir = Path("logs")
        self.metrics_dir = Path("metrics")
        
        # Create directories
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self._configure_logging()
        
        # Initialize metrics
        self.current_metrics: List[PerformanceMetrics] = []
        
    def _configure_logging(self):
        """Configure logging settings."""
        # Get log level from config
        log_level = getattr(logging, self.config.log_level.upper())
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # Create handlers
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        
        file_handler = logging.FileHandler(
            self.log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(file_formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # Create application logger
        self.logger = logging.getLogger('ariesone')
        self.logger.setLevel(log_level)

    def _format_log_entry(
        self,
        level: str,
        message: str,
        module: str,
        function: str,
        line: int,
        user: Optional[str] = None,
        request_id: Optional[str] = None,
        **kwargs
    ) -> LogEntry:
        """Format log entry."""
        return LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            module=module,
            function=function,
            line=line,
            user=user,
            request_id=request_id,
            extra=kwargs
        )

    def _save_log_entry(self, entry: LogEntry):
        """Save log entry to file."""
        log_file = self.log_dir / f'structured_{datetime.now().strftime("%Y%m%d")}.json'
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry.dict()) + '\n')

    def log(
        self,
        level: str,
        message: str,
        user: Optional[str] = None,
        request_id: Optional[str] = None,
        **kwargs
    ):
        """Log message with structured data."""
        # Get caller information
        frame = traceback.extract_stack()[-2]
        module = frame.filename
        function = frame.name
        line = frame.lineno
        
        # Create log entry
        entry = self._format_log_entry(
            level,
            message,
            module,
            function,
            line,
            user,
            request_id,
            **kwargs
        )
        
        # Log using standard logging
        log_func = getattr(self.logger, level.lower())
        log_func(message)
        
        # Save structured log
        self._save_log_entry(entry)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log('DEBUG', message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log('ERROR', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.log('CRITICAL', message, **kwargs)

    def record_metric(self, metric: PerformanceMetrics):
        """Record performance metric."""
        self.current_metrics.append(metric)
        
        # Save metrics periodically
        if len(self.current_metrics) >= 100:
            self.save_metrics()

    def save_metrics(self):
        """Save current metrics to file."""
        if not self.current_metrics:
            return
            
        metrics_file = self.metrics_dir / f'metrics_{datetime.now().strftime("%Y%m%d")}.json'
        
        with open(metrics_file, 'a') as f:
            for metric in self.current_metrics:
                f.write(json.dumps(metric.dict()) + '\n')
        
        self.current_metrics = []

    async def log_request(
        self,
        request: Request,
        response: Response,
        user: Optional[str] = None
    ):
        """Log request details and performance metrics."""
        request_id = request.headers.get('X-Request-ID')
        start_time = time.time()
        
        # Log request
        self.info(
            f"Request: {request.method} {request.url.path}",
            user=user,
            request_id=request_id,
            headers=dict(request.headers),
            query_params=dict(request.query_params),
            client_host=request.client.host if request.client else None
        )
        
        try:
            # Wait for response
            response_body = b''
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metric
            metric = PerformanceMetrics(
                request_id=request_id,
                endpoint=request.url.path,
                method=request.method,
                start_time=start_time,
                duration=duration,
                status_code=response.status_code,
                user=user,
                extra={
                    'response_size': len(response_body),
                    'client_host': request.client.host if request.client else None
                }
            )
            self.record_metric(metric)
            
            # Log response
            self.info(
                f"Response: {response.status_code}",
                user=user,
                request_id=request_id,
                duration=duration,
                response_size=len(response_body)
            )
            
            return response_body
            
        except Exception as e:
            self.error(
                f"Request failed: {str(e)}",
                user=user,
                request_id=request_id,
                error=str(e),
                traceback=traceback.format_exc()
            )
            raise

    def cleanup(self):
        """Clean up old log files."""
        # Save any remaining metrics
        self.save_metrics()
        
        # Close handlers
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
