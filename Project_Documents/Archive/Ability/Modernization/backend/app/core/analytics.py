from typing import Any, Dict, Optional
from datetime import datetime
from prometheus_client import Counter, Histogram
from app.core.logging import logger

class Analytics:
    def __init__(self):
        # Form template metrics
        self.template_views = Counter(
            'form_template_views_total',
            'Number of form template views',
            ['template_id']
        )
        self.template_creations = Counter(
            'form_template_creations_total',
            'Number of form template creations'
        )
        self.template_updates = Counter(
            'form_template_updates_total',
            'Number of form template updates',
            ['template_id']
        )
        
        # Form submission metrics
        self.form_submissions = Counter(
            'form_submissions_total',
            'Number of form submissions',
            ['template_id']
        )
        self.submission_views = Counter(
            'form_submission_views_total',
            'Number of form submission views',
            ['submission_id']
        )
        self.submission_updates = Counter(
            'form_submission_updates_total',
            'Number of form submission updates',
            ['submission_id']
        )
        self.submission_downloads = Counter(
            'form_submission_downloads_total',
            'Number of form submission downloads',
            ['submission_id']
        )
        
        # Processing metrics
        self.processing_duration = Histogram(
            'form_processing_duration_seconds',
            'Form processing duration in seconds',
            ['template_id'],
            buckets=(1, 5, 10, 30, 60, 120, 300, 600)
        )
        self.processing_errors = Counter(
            'form_processing_errors_total',
            'Number of form processing errors',
            ['template_id', 'error_type']
        )
        
        # Validation metrics
        self.validation_errors = Counter(
            'form_validation_errors_total',
            'Number of form validation errors',
            ['template_id', 'field']
        )
        
        # File metrics
        self.file_uploads = Counter(
            'form_file_uploads_total',
            'Number of file uploads',
            ['template_id', 'file_type']
        )
        self.file_upload_bytes = Histogram(
            'form_file_upload_bytes',
            'File upload size in bytes',
            ['template_id'],
            buckets=(1024, 10240, 102400, 1048576, 10485760)
        )
        
        # Progress metrics
        self.progress_updates = Counter(
            'form_progress_updates_total',
            'Number of progress updates',
            ['submission_id']
        )

    def track_template_view(self, template_id: str) -> None:
        """Track template view"""
        try:
            self.template_views.labels(template_id=template_id).inc()
        except Exception as e:
            logger.error(f"Error tracking template view: {e}")

    def track_template_creation(self, template_id: str) -> None:
        """Track template creation"""
        try:
            self.template_creations.inc()
        except Exception as e:
            logger.error(f"Error tracking template creation: {e}")

    def track_template_update(self, template_id: str) -> None:
        """Track template update"""
        try:
            self.template_updates.labels(template_id=template_id).inc()
        except Exception as e:
            logger.error(f"Error tracking template update: {e}")

    def track_form_submission(
        self,
        submission_id: str,
        template_id: str
    ) -> None:
        """Track form submission"""
        try:
            self.form_submissions.labels(template_id=template_id).inc()
        except Exception as e:
            logger.error(f"Error tracking form submission: {e}")

    def track_submission_view(self, submission_id: str) -> None:
        """Track submission view"""
        try:
            self.submission_views.labels(submission_id=submission_id).inc()
        except Exception as e:
            logger.error(f"Error tracking submission view: {e}")

    def track_submission_update(self, submission_id: str) -> None:
        """Track submission update"""
        try:
            self.submission_updates.labels(submission_id=submission_id).inc()
        except Exception as e:
            logger.error(f"Error tracking submission update: {e}")

    def track_submission_download(self, submission_id: str) -> None:
        """Track submission download"""
        try:
            self.submission_downloads.labels(submission_id=submission_id).inc()
        except Exception as e:
            logger.error(f"Error tracking submission download: {e}")

    def track_processing_duration(
        self,
        template_id: str,
        duration: float
    ) -> None:
        """Track processing duration"""
        try:
            self.processing_duration.labels(template_id=template_id).observe(duration)
        except Exception as e:
            logger.error(f"Error tracking processing duration: {e}")

    def track_processing_error(
        self,
        template_id: str,
        error_type: str
    ) -> None:
        """Track processing error"""
        try:
            self.processing_errors.labels(
                template_id=template_id,
                error_type=error_type
            ).inc()
        except Exception as e:
            logger.error(f"Error tracking processing error: {e}")

    def track_validation_error(
        self,
        template_id: str,
        field: str
    ) -> None:
        """Track validation error"""
        try:
            self.validation_errors.labels(
                template_id=template_id,
                field=field
            ).inc()
        except Exception as e:
            logger.error(f"Error tracking validation error: {e}")

    def track_file_upload(
        self,
        template_id: str,
        file_type: str,
        size: int
    ) -> None:
        """Track file upload"""
        try:
            self.file_uploads.labels(
                template_id=template_id,
                file_type=file_type
            ).inc()
            self.file_upload_bytes.labels(template_id=template_id).observe(size)
        except Exception as e:
            logger.error(f"Error tracking file upload: {e}")

    def track_progress_update(self, submission_id: str) -> None:
        """Track progress update"""
        try:
            self.progress_updates.labels(submission_id=submission_id).inc()
        except Exception as e:
            logger.error(f"Error tracking progress update: {e}")

# Create global analytics instance
analytics = Analytics()
