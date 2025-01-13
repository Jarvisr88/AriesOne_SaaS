"""
Base classes for form management services.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class FormField(BaseModel):
    """Base model for form fields."""
    id: str
    type: str
    label: str
    name: str
    required: bool
    placeholder: Optional[str] = None
    description: Optional[str] = None
    validation_rules: Optional[List[Dict[str, Any]]] = None
    options: Optional[List[Dict[str, str]]] = None
    default_value: Optional[Any] = None

class FormConfig(BaseModel):
    """Base model for form configuration."""
    id: str
    title: str
    description: Optional[str] = None
    fields: List[FormField]
    submit_endpoint: str
    success_message: Optional[str] = None
    error_message: Optional[str] = None

class FormBuilderService(ABC):
    """Base class for form builder services."""
    
    @abstractmethod
    def create_form(self, config: FormConfig) -> str:
        """Create a new form."""
        pass
    
    @abstractmethod
    def get_form(self, form_id: str) -> Optional[FormConfig]:
        """Retrieve a form configuration."""
        pass
    
    @abstractmethod
    def update_form(self, form_id: str, config: FormConfig) -> bool:
        """Update an existing form."""
        pass
    
    @abstractmethod
    def delete_form(self, form_id: str) -> bool:
        """Delete a form."""
        pass

class FormValidationService(ABC):
    """Base class for form validation services."""
    
    @abstractmethod
    def validate_form(self, form_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form data."""
        pass
    
    @abstractmethod
    def add_validation_rule(self, form_id: str, field_id: str, rule: Dict[str, Any]) -> bool:
        """Add a validation rule to a form field."""
        pass
    
    @abstractmethod
    def remove_validation_rule(self, form_id: str, field_id: str, rule_id: str) -> bool:
        """Remove a validation rule from a form field."""
        pass

class FormSubmissionService(ABC):
    """Base class for form submission services."""
    
    @abstractmethod
    def submit_form(self, form_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit form data."""
        pass
    
    @abstractmethod
    def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a form submission."""
        pass
    
    @abstractmethod
    def list_submissions(self, form_id: str) -> List[Dict[str, Any]]:
        """List all submissions for a form."""
        pass

class FormTemplateService(ABC):
    """Base class for form template services."""
    
    @abstractmethod
    def create_template(self, name: str, config: FormConfig) -> str:
        """Create a new form template."""
        pass
    
    @abstractmethod
    def get_template(self, template_id: str) -> Optional[FormConfig]:
        """Retrieve a form template."""
        pass
    
    @abstractmethod
    def update_template(self, template_id: str, config: FormConfig) -> bool:
        """Update an existing template."""
        pass
    
    @abstractmethod
    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        pass

class FormAnalyticsService(ABC):
    """Base class for form analytics services."""
    
    @abstractmethod
    def track_view(self, form_id: str, user_id: Optional[str] = None) -> None:
        """Track form view."""
        pass
    
    @abstractmethod
    def track_submission(self, form_id: str, submission_id: str) -> None:
        """Track form submission."""
        pass
    
    @abstractmethod
    def get_form_stats(self, form_id: str) -> Dict[str, Any]:
        """Get form statistics."""
        pass
    
    @abstractmethod
    def generate_report(self, form_id: str) -> Dict[str, Any]:
        """Generate analytics report."""
        pass
