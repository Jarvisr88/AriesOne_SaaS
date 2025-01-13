from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from prometheus_client import Counter, Histogram, Gauge
import psutil
import json
from pathlib import Path
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.core import ProcessingJob, ProcessingStatus
from app.core.config import settings

# Prometheus metrics
csv_processing_total = Counter(
    'csv_processing_total',
    'Total number of CSV processing attempts',
    ['schema', 'status']
)

csv_processing_duration = Histogram(
    'csv_processing_duration_seconds',
    'Time spent processing CSV files',
    ['schema'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600)
)

csv_queue_length = Gauge(
    'csv_queue_length',
    'Number of CSV files waiting to be processed'
)

csv_processing_errors = Counter(
    'csv_processing_errors',
    'Number of CSV processing errors',
    ['error_type', 'schema']
)

csv_file_size = Histogram(
    'csv_file_size_bytes',
    'Size of processed CSV files',
    ['schema'],
    buckets=(1024*1024*x for x in (1, 5, 10, 50, 100))
)

csv_row_count = Histogram(
    'csv_row_count',
    'Number of rows in processed CSV files',
    ['schema'],
    buckets=(100, 1000, 5000, 10000, 50000, 100000)
)

class CSVMonitoring:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = SessionLocal()

    def track_processing_start(self, schema: str, file_size: int) -> None:
        """Track the start of CSV processing."""
        csv_processing_total.labels(schema=schema, status='started').inc()
        csv_file_size.labels(schema=schema).observe(file_size)

    def track_processing_complete(
        self,
        schema: str,
        duration: float,
        row_count: int,
        status: ProcessingStatus
    ) -> None:
        """Track the completion of CSV processing."""
        csv_processing_total.labels(schema=schema, status=status).inc()
        csv_processing_duration.labels(schema=schema).observe(duration)
        csv_row_count.labels(schema=schema).observe(row_count)

    def track_error(self, schema: str, error_type: str) -> None:
        """Track CSV processing errors."""
        csv_processing_errors.labels(
            error_type=error_type,
            schema=schema
        ).inc()

    def update_queue_metrics(self) -> None:
        """Update queue-related metrics."""
        pending_count = self.db.query(ProcessingJob).filter(
            ProcessingJob.status == ProcessingStatus.PENDING
        ).count()
        csv_queue_length.set(pending_count)

    def get_processing_stats(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict:
        """Get processing statistics for the specified time range."""
        start_time = datetime.utcnow() - time_range
        
        # Query processing jobs
        jobs = self.db.query(ProcessingJob).filter(
            ProcessingJob.start_time >= start_time
        ).all()

        # Calculate statistics
        total_jobs = len(jobs)
        successful_jobs = sum(1 for job in jobs if job.status == ProcessingStatus.COMPLETED)
        failed_jobs = sum(1 for job in jobs if job.status == ProcessingStatus.FAILED)
        
        total_rows = sum(job.total_rows or 0 for job in jobs)
        processed_rows = sum(job.processed_rows or 0 for job in jobs)
        failed_rows = sum(job.failed_rows or 0 for job in jobs)

        # Calculate average processing time
        completed_jobs = [
            job for job in jobs
            if job.status == ProcessingStatus.COMPLETED and job.end_time
        ]
        avg_processing_time = (
            sum(
                (job.end_time - job.start_time).total_seconds()
                for job in completed_jobs
            ) / len(completed_jobs)
            if completed_jobs else 0
        )

        # Get error distribution
        error_types: Dict[str, int] = {}
        for job in jobs:
            if job.errors:
                for error in job.errors:
                    error_type = error.get('type', 'unknown')
                    error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            'time_range_days': time_range.days,
            'total_jobs': total_jobs,
            'successful_jobs': successful_jobs,
            'failed_jobs': failed_jobs,
            'success_rate': (successful_jobs / total_jobs * 100) if total_jobs else 0,
            'total_rows': total_rows,
            'processed_rows': processed_rows,
            'failed_rows': failed_rows,
            'avg_processing_time': avg_processing_time,
            'error_distribution': error_types
        }

    def get_schema_stats(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict:
        """Get statistics per schema."""
        start_time = datetime.utcnow() - time_range
        
        stats = {}
        jobs = self.db.query(ProcessingJob).filter(
            ProcessingJob.start_time >= start_time
        ).all()

        for job in jobs:
            if job.schema_name not in stats:
                stats[job.schema_name] = {
                    'total_jobs': 0,
                    'successful_jobs': 0,
                    'failed_jobs': 0,
                    'total_rows': 0,
                    'processed_rows': 0,
                    'failed_rows': 0,
                    'error_types': {}
                }

            schema_stats = stats[job.schema_name]
            schema_stats['total_jobs'] += 1
            
            if job.status == ProcessingStatus.COMPLETED:
                schema_stats['successful_jobs'] += 1
            elif job.status == ProcessingStatus.FAILED:
                schema_stats['failed_jobs'] += 1

            schema_stats['total_rows'] += job.total_rows or 0
            schema_stats['processed_rows'] += job.processed_rows or 0
            schema_stats['failed_rows'] += job.failed_rows or 0

            if job.errors:
                for error in job.errors:
                    error_type = error.get('type', 'unknown')
                    schema_stats['error_types'][error_type] = (
                        schema_stats['error_types'].get(error_type, 0) + 1
                    )

        return stats

    def get_performance_metrics(self) -> Dict:
        """Get system performance metrics."""
        return {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

    def generate_report(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> str:
        """Generate a comprehensive monitoring report."""
        processing_stats = self.get_processing_stats(time_range)
        schema_stats = self.get_schema_stats(time_range)
        performance_metrics = self.get_performance_metrics()

        report_dir = Path(settings.REPORTS_DIR)
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"csv_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'time_range_days': time_range.days,
            'processing_stats': processing_stats,
            'schema_stats': schema_stats,
            'performance_metrics': performance_metrics
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        return str(report_file)

    def alert_if_necessary(self) -> List[str]:
        """Check for conditions that require alerts."""
        alerts = []
        
        # Check queue length
        queue_length = self.db.query(ProcessingJob).filter(
            ProcessingJob.status == ProcessingStatus.PENDING
        ).count()
        if queue_length > settings.CSV_MAX_QUEUE_LENGTH:
            alerts.append(f"Queue length ({queue_length}) exceeds maximum")

        # Check failure rate
        recent_jobs = self.db.query(ProcessingJob).filter(
            ProcessingJob.start_time >= datetime.utcnow() - timedelta(hours=1)
        ).all()
        
        if recent_jobs:
            failure_rate = (
                sum(1 for job in recent_jobs if job.status == ProcessingStatus.FAILED)
                / len(recent_jobs)
            )
            if failure_rate > settings.CSV_MAX_FAILURE_RATE:
                alerts.append(
                    f"High failure rate ({failure_rate:.2%}) in the last hour"
                )

        # Check system resources
        performance = self.get_performance_metrics()
        if performance['cpu_usage'] > 90:
            alerts.append(f"High CPU usage: {performance['cpu_usage']}%")
        if performance['memory_usage'] > 90:
            alerts.append(f"High memory usage: {performance['memory_usage']}%")
        if performance['disk_usage'] > 90:
            alerts.append(f"High disk usage: {performance['disk_usage']}%")

        # Log alerts
        if alerts:
            self.logger.warning("CSV Processing Alerts: %s", ", ".join(alerts))

        return alerts

    def cleanup_old_files(self, max_age: timedelta = timedelta(days=7)) -> None:
        """Clean up old processed files and reports."""
        cutoff_time = datetime.utcnow() - max_age

        # Clean up processed files
        processed_dir = Path(settings.PROCESSED_FILES_DIR)
        if processed_dir.exists():
            for file_path in processed_dir.glob("**/*"):
                if file_path.is_file():
                    try:
                        if file_path.stat().st_mtime < cutoff_time.timestamp():
                            file_path.unlink()
                    except Exception as e:
                        self.logger.error(
                            "Failed to clean up file %s: %s",
                            file_path,
                            str(e)
                        )

        # Clean up reports
        report_dir = Path(settings.REPORTS_DIR)
        if report_dir.exists():
            for report_path in report_dir.glob("*.json"):
                try:
                    if report_path.stat().st_mtime < cutoff_time.timestamp():
                        report_path.unlink()
                except Exception as e:
                    self.logger.error(
                        "Failed to clean up report %s: %s",
                        report_path,
                        str(e)
                    )
