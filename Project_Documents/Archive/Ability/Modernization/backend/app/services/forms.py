from typing import List, Optional, AsyncGenerator
import json
import asyncio
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.services.base import BaseService, cached, rate_limited, with_retry
from app.core.logging import logger
from app.core.monitoring import metrics
from app.core.storage import storage_client
from app.schemas.forms import (
    FormTemplate,
    FormSubmission,
    FormProgress,
    FormField,
    FormError
)
from app.db.repositories.forms import FormRepository
from app.core.validation import validate_form_data
from app.core.analytics import analytics

class FormService(BaseService):
    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.repository = FormRepository()

    @cached("template", ttl=3600)
    @with_retry
    async def get_template(self, template_id: str) -> FormTemplate:
        """Get form template by ID"""
        try:
            template = await self.repository.get_template(template_id)
            if not template:
                raise HTTPException(
                    status_code=404,
                    detail="Template not found"
                )
            analytics.track_template_view(template_id)
            return template
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting template: {e}")
            metrics.template_errors.inc()
            raise HTTPException(
                status_code=500,
                detail="Failed to get template"
            )

    @cached("templates", ttl=3600)
    @with_retry
    async def get_templates(
        self,
        type: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[FormTemplate]:
        """Get form templates"""
        try:
            templates = await self.repository.get_templates(type, skip, limit)
            analytics.track_template_list(type)
            return templates
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            metrics.template_errors.inc()
            raise HTTPException(
                status_code=500,
                detail="Failed to get templates"
            )

    @with_retry
    async def create_template(
        self,
        name: str,
        type: str,
        fields: List[FormField]
    ) -> FormTemplate:
        """Create form template"""
        try:
            template = await self.repository.create_template(
                name=name,
                type=type,
                fields=fields
            )
            await self.clear_cache_pattern("template:*")
            analytics.track_template_creation(template.id)
            return template
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            metrics.template_errors.inc()
            raise HTTPException(
                status_code=500,
                detail="Failed to create template"
            )

    @with_retry
    async def update_template(
        self,
        id: str,
        name: Optional[str] = None,
        fields: Optional[List[FormField]] = None
    ) -> FormTemplate:
        """Update form template"""
        try:
            template = await self.repository.update_template(
                id=id,
                name=name,
                fields=fields
            )
            await self.clear_cache_pattern(f"template:*")
            analytics.track_template_update(template.id)
            return template
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            metrics.template_errors.inc()
            raise HTTPException(
                status_code=500,
                detail="Failed to update template"
            )

    @rate_limited("submission")
    @with_retry
    async def submit_form(
        self,
        template_id: str,
        data: str,
        files: Optional[List[UploadFile]] = None
    ) -> FormSubmission:
        """Submit form with files"""
        try:
            # Validate template exists
            template = await self.get_template(template_id)
            
            # Validate form data
            form_data = json.loads(data)
            errors = validate_form_data(template.fields, form_data)
            if errors:
                metrics.validation_errors.inc()
                return FormSubmission(
                    template_id=template_id,
                    status="error",
                    errors=errors
                )

            # Upload files
            file_urls = []
            if files:
                for file in files:
                    try:
                        url = await self._upload_file(file)
                        file_urls.append(url)
                        analytics.track_file_upload(
                            template_id,
                            file.content_type,
                            file.size
                        )
                    except Exception as e:
                        logger.error(f"File upload error: {e}")
                        metrics.file_upload_errors.inc()

            # Create submission
            submission = await self.repository.create_submission(
                template_id=template_id,
                data=form_data,
                file_urls=file_urls
            )
            
            # Start processing
            asyncio.create_task(
                self._process_submission(submission.id)
            )
            
            analytics.track_form_submission(submission.id)
            return submission
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            metrics.submission_errors.inc()
            raise HTTPException(
                status_code=500,
                detail="Failed to submit form"
            )

    @cached("submission", ttl=300)
    @with_retry
    async def get_submission(
        self,
        submission_id: str
    ) -> FormSubmission:
        """Get form submission"""
        try:
            submission = await self.repository.get_submission(submission_id)
            if not submission:
                raise HTTPException(
                    status_code=404,
                    detail="Submission not found"
                )
            analytics.track_submission_view(submission_id)
            return submission
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting submission: {e}")
            metrics.submission_errors.inc()
            raise HTTPException(
                status_code=500,
                detail="Failed to get submission"
            )

    async def track_progress(
        self,
        submission_id: str
    ) -> AsyncGenerator[FormProgress, None]:
        """Track form submission progress"""
        try:
            while True:
                progress = await self.repository.get_progress(submission_id)
                if not progress:
                    break
                    
                analytics.track_progress_update(submission_id)
                yield progress
                
                if progress.status in ["completed", "error"]:
                    break
                    
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error tracking progress: {e}")
            metrics.progress_errors.inc()
            raise HTTPException(
                status_code=500,
                detail="Failed to track progress"
            )

    @rate_limited("upload")
    async def _upload_file(self, file: UploadFile) -> str:
        """Upload file to storage"""
        try:
            return await storage_client.upload_file(
                file.filename,
                await file.read()
            )
        except Exception as e:
            logger.error(f"File upload error: {e}")
            metrics.file_upload_errors.inc()
            raise

    async def _process_submission(self, submission_id: str) -> None:
        """Process form submission"""
        try:
            start_time = datetime.utcnow()
            
            # Update progress
            await self.repository.update_progress(
                submission_id,
                FormProgress(
                    status="processing",
                    progress=0.0,
                    message="Starting processing"
                )
            )
            
            # Get submission
            submission = await self.get_submission(submission_id)
            
            # Process submission (implement your logic here)
            await asyncio.sleep(2)  # Simulated processing
            
            # Update progress
            await self.repository.update_progress(
                submission_id,
                FormProgress(
                    status="completed",
                    progress=1.0,
                    message="Processing completed"
                )
            )
            
            # Track processing time
            duration = (datetime.utcnow() - start_time).total_seconds()
            analytics.track_processing_duration(
                submission.template_id,
                duration
            )
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            metrics.processing_errors.inc()
            
            # Update progress with error
            await self.repository.update_progress(
                submission_id,
                FormProgress(
                    status="error",
                    progress=0.0,
                    message=str(e)
                )
            )
            
            analytics.track_processing_error(
                submission.template_id,
                type(e).__name__
            )
