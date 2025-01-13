"""
Form management orchestration service.
"""
from typing import Dict, Any, Optional, Type, List
from app.services.forms.base import (
    FormBuilderService,
    FormValidationService,
    FormSubmissionService,
    FormTemplateService,
    FormAnalyticsService,
    FormConfig
)
from app.services.forms.builder import SQLFormBuilderService
from app.services.forms.validation import PydanticFormValidationService
import logging

logger = logging.getLogger(__name__)

class FormManager:
    """
    Form management orchestrator that coordinates various form services.
    
    This class follows the Facade pattern to provide a simplified interface
    to the complex subsystem of form services. It also implements the
    Strategy pattern to allow runtime configuration of service implementations.
    """
    
    def __init__(
        self,
        builder_service: Optional[Type[FormBuilderService]] = None,
        validation_service: Optional[Type[FormValidationService]] = None,
        submission_service: Optional[Type[FormSubmissionService]] = None,
        template_service: Optional[Type[FormTemplateService]] = None,
        analytics_service: Optional[Type[FormAnalyticsService]] = None
    ):
        # Initialize with default or provided service implementations
        self._builder = (builder_service or SQLFormBuilderService)()
        self._validator = (validation_service or PydanticFormValidationService)()
        self._submission = submission_service() if submission_service else None
        self._template = template_service() if template_service else None
        self._analytics = analytics_service() if analytics_service else None
        
        # Track service status
        self._services_status: Dict[str, bool] = {
            "builder": True,
            "validator": True,
            "submission": submission_service is not None,
            "template": template_service is not None,
            "analytics": analytics_service is not None
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all form services."""
        return {
            "services_status": self._services_status,
            "active_services": [
                service for service, status in self._services_status.items()
                if status
            ]
        }
    
    async def create_form(self, config: FormConfig) -> str:
        """Create a new form."""
        try:
            # Create form
            form_id = self._builder.create_form(config)
            logger.info(f"Created form: {form_id}")
            
            # Track analytics if available
            if self._analytics:
                self._analytics.track_view(form_id)
            
            return form_id
            
        except Exception as e:
            logger.error(f"Failed to create form: {str(e)}")
            raise
    
    async def get_form(self, form_id: str) -> Optional[FormConfig]:
        """Retrieve a form configuration."""
        try:
            # Get form
            form = self._builder.get_form(form_id)
            
            # Track analytics if available
            if form and self._analytics:
                self._analytics.track_view(form_id)
            
            return form
            
        except Exception as e:
            logger.error(f"Failed to get form: {str(e)}")
            raise
    
    async def update_form(self, form_id: str, config: FormConfig) -> bool:
        """Update an existing form."""
        try:
            return self._builder.update_form(form_id, config)
            
        except Exception as e:
            logger.error(f"Failed to update form: {str(e)}")
            raise
    
    async def delete_form(self, form_id: str) -> bool:
        """Delete a form."""
        try:
            return self._builder.delete_form(form_id)
            
        except Exception as e:
            logger.error(f"Failed to delete form: {str(e)}")
            raise
    
    async def validate_form_data(
        self,
        form_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate form data."""
        try:
            return self._validator.validate_form(form_id, data)
            
        except Exception as e:
            logger.error(f"Failed to validate form data: {str(e)}")
            raise
    
    async def submit_form(
        self,
        form_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit form data."""
        try:
            if not self._submission:
                raise RuntimeError("Submission service not configured")
            
            # Validate data
            validation_result = self._validator.validate_form(form_id, data)
            if "errors" in validation_result:
                return validation_result
            
            # Submit form
            result = self._submission.submit_form(form_id, validation_result)
            
            # Track analytics if available
            if self._analytics:
                self._analytics.track_submission(
                    form_id,
                    result.get("submission_id", "unknown")
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to submit form: {str(e)}")
            raise
    
    async def get_form_stats(self, form_id: str) -> Dict[str, Any]:
        """Get form statistics."""
        try:
            if not self._analytics:
                raise RuntimeError("Analytics service not configured")
            
            return self._analytics.get_form_stats(form_id)
            
        except Exception as e:
            logger.error(f"Failed to get form stats: {str(e)}")
            raise
    
    async def generate_analytics_report(
        self,
        form_id: str
    ) -> Dict[str, Any]:
        """Generate form analytics report."""
        try:
            if not self._analytics:
                raise RuntimeError("Analytics service not configured")
            
            return self._analytics.generate_report(form_id)
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {str(e)}")
            raise
