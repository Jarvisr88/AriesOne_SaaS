"""
AriesOne CSV Profiler Module

Provides performance monitoring and optimization for CSV operations.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time
import logging
import psutil
from datetime import datetime
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ProfileMetrics:
    """Metrics collected during CSV operations."""
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    rows_processed: int = 0
    memory_usage: float = 0.0  # MB
    cpu_percent: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors_encountered: int = 0
    
    @property
    def duration_seconds(self) -> float:
        """Calculate operation duration in seconds."""
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def rows_per_second(self) -> float:
        """Calculate processing rate."""
        if self.duration_seconds == 0:
            return 0.0
        return self.rows_processed / self.duration_seconds
    
    @property
    def cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total

class CSVProfiler:
    """Performance profiler for CSV operations."""
    
    def __init__(self):
        """Initialize profiler."""
        self.metrics: Dict[str, ProfileMetrics] = {}
        self._current_operation: Optional[str] = None
        
    def start_operation(self, operation: str):
        """Start tracking a CSV operation.
        
        Args:
            operation: Name of operation to track
        """
        self._current_operation = operation
        self.metrics[operation] = ProfileMetrics(
            operation=operation,
            start_time=datetime.now()
        )
        
    def end_operation(self):
        """End tracking current operation."""
        if not self._current_operation:
            return
            
        metrics = self.metrics[self._current_operation]
        metrics.end_time = datetime.now()
        metrics.memory_usage = self._get_memory_usage()
        metrics.cpu_percent = self._get_cpu_usage()
        
        self._log_metrics(metrics)
        self._current_operation = None
        
    def record_rows(self, count: int):
        """Record number of rows processed.
        
        Args:
            count: Number of rows
        """
        if self._current_operation:
            self.metrics[self._current_operation].rows_processed += count
            
    def record_cache_hit(self):
        """Record cache hit."""
        if self._current_operation:
            self.metrics[self._current_operation].cache_hits += 1
            
    def record_cache_miss(self):
        """Record cache miss."""
        if self._current_operation:
            self.metrics[self._current_operation].cache_misses += 1
            
    def record_error(self):
        """Record error occurrence."""
        if self._current_operation:
            self.metrics[self._current_operation].errors_encountered += 1
            
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
        
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent()
        
    def _log_metrics(self, metrics: ProfileMetrics):
        """Log operation metrics.
        
        Args:
            metrics: Metrics to log
        """
        logger.info(
            f"CSV Operation: {metrics.operation}\n"
            f"Duration: {metrics.duration_seconds:.2f}s\n"
            f"Rows: {metrics.rows_processed:,}\n"
            f"Rate: {metrics.rows_per_second:.0f} rows/s\n"
            f"Memory: {metrics.memory_usage:.1f}MB\n"
            f"CPU: {metrics.cpu_percent:.1f}%\n"
            f"Cache Hit Ratio: {metrics.cache_hit_ratio:.2%}\n"
            f"Errors: {metrics.errors_encountered}"
        )
        
    def get_metrics(self, operation: str) -> Optional[ProfileMetrics]:
        """Get metrics for specific operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Operation metrics if found
        """
        return self.metrics.get(operation)
        
    def generate_report(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """Generate performance report.
        
        Args:
            file_path: Optional path to save report
            
        Returns:
            DataFrame with performance metrics
        """
        data = []
        for metrics in self.metrics.values():
            data.append({
                'Operation': metrics.operation,
                'Duration (s)': metrics.duration_seconds,
                'Rows': metrics.rows_processed,
                'Rows/s': metrics.rows_per_second,
                'Memory (MB)': metrics.memory_usage,
                'CPU %': metrics.cpu_percent,
                'Cache Hit Ratio': metrics.cache_hit_ratio,
                'Errors': metrics.errors_encountered
            })
            
        df = pd.DataFrame(data)
        
        if file_path:
            df.to_csv(file_path, index=False)
            logger.info(f"Performance report saved to {file_path}")
            
        return df
