"""
Form Base Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides base classes for form management.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field, validator

from ..utils.logging import CoreLogger
from ..utils.validation import ValidationResult
from .EntityBase import EntityBase

logger = CoreLogger(__name__)
T = TypeVar('T', bound=EntityBase)


class FormField(BaseModel):
    """Base model for form fields."""
    name: str = Field(..., description="Field name")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Field type")
    required: bool = Field(default=False, description="Is field required")
    default: Optional[Any] = Field(default=None, description="Default value")
    validators: List[str] = Field(default_factory=list, description="Validation rules")
    options: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Options for select fields"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class FormDefinition(BaseModel):
    """Base model for form definitions."""
    id: str = Field(..., description="Form ID")
    title: str = Field(..., description="Form title")
    description: Optional[str] = Field(None, description="Form description")
    fields: List[FormField] = Field(..., description="Form fields")
    entity_type: Type[T] = Field(..., description="Associated entity type")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    version: str = Field(default="1.0.0", description="Form version")
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        """Set updated_at to current time."""
        return datetime.utcnow()


class FormValidatorBase(ABC):
    """Base class for form validators."""
    
    @abstractmethod
    async def validate_field(self, field: FormField,
                           value: Any) -> ValidationResult:
        """Validate a single field."""
        pass
    
    @abstractmethod
    async def validate_form(self, form: FormDefinition,
                          data: Dict[str, Any]) -> ValidationResult:
        """Validate entire form."""
        pass


class FormProcessorBase(ABC):
    """Base class for form processors."""
    
    @abstractmethod
    async def pre_process(self, form: FormDefinition,
                         data: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process form data before validation."""
        pass
    
    @abstractmethod
    async def post_process(self, form: FormDefinition,
                          data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process form data after validation."""
        pass
    
    @abstractmethod
    async def transform_to_entity(self, form: FormDefinition,
                                data: Dict[str, Any]) -> T:
        """Transform form data to entity."""
        pass
    
    @abstractmethod
    async def transform_from_entity(self, form: FormDefinition,
                                  entity: T) -> Dict[str, Any]:
        """Transform entity to form data."""
        pass


class FormHandlerBase(ABC):
    """Base class for form handlers."""
    
    def __init__(self, validator: FormValidatorBase,
                 processor: FormProcessorBase):
        """Initialize form handler."""
        self.validator = validator
        self.processor = processor
    
    @abstractmethod
    async def handle_submission(self, form: FormDefinition,
                              data: Dict[str, Any]) -> T:
        """Handle form submission."""
        try:
            # Pre-process data
            processed_data = await self.processor.pre_process(form, data)
            
            # Validate form
            validation_result = await self.validator.validate_form(
                form,
                processed_data
            )
            if not validation_result.is_valid:
                logger.error(
                    f"Form validation failed: {validation_result.errors}"
                )
                raise ValueError(validation_result.errors)
            
            # Post-process data
            final_data = await self.processor.post_process(
                form,
                processed_data
            )
            
            # Transform to entity
            entity = await self.processor.transform_to_entity(form, final_data)
            
            return entity
        except Exception as e:
            logger.error(f"Form submission failed: {str(e)}")
            raise
    
    @abstractmethod
    async def load_form_data(self, form: FormDefinition, entity: T) -> Dict[str, Any]:
        """Load form data from entity."""
        try:
            # Transform entity to form data
            data = await self.processor.transform_from_entity(form, entity)
            
            # Pre-process data
            processed_data = await self.processor.pre_process(form, data)
            
            return processed_data
        except Exception as e:
            logger.error(f"Failed to load form data: {str(e)}")
            raise


class FormRepositoryBase(ABC):
    """Base class for form repositories."""
    
    @abstractmethod
    async def get_form_definition(self, form_id: str) -> Optional[FormDefinition]:
        """Get form definition by ID."""
        pass
    
    @abstractmethod
    async def save_form_definition(self, form: FormDefinition) -> FormDefinition:
        """Save form definition."""
        pass
    
    @abstractmethod
    async def delete_form_definition(self, form_id: str) -> bool:
        """Delete form definition."""
        pass
    
    @abstractmethod
    async def list_form_definitions(
        self,
        entity_type: Optional[Type[T]] = None
    ) -> List[FormDefinition]:
        """List form definitions."""
        pass
    
    @abstractmethod
    async def get_form_version(self, form_id: str,
                             version: str) -> Optional[FormDefinition]:
        """Get specific version of form definition."""
        pass
