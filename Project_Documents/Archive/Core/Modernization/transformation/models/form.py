"""
Form models for the Core module.
Handles form definitions, states, and validation rules.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator

from .base import BaseDBModel, BaseSchema

class FormDefinition(BaseDBModel):
    """Database model for form definitions."""
    __tablename__ = "core_form_definitions"

    name = Column(String(100), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    components = Column(JSON, nullable=False)
    validation_rules = Column(JSON, nullable=False)
    permissions = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    is_published = Column(Boolean, nullable=False, default=False)

class FormState(BaseDBModel):
    """Database model for form states."""
    __tablename__ = "core_form_states"

    form_definition_id = Column(Integer, ForeignKey("core_form_definitions.id"), nullable=False)
    entity_id = Column(Integer, nullable=False)
    state_data = Column(JSON, nullable=False)
    is_dirty = Column(Boolean, nullable=False, default=False)
    is_new = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    validation_errors = Column(JSON, nullable=True)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FormValidation(BaseDBModel):
    """Database model for form validation results."""
    __tablename__ = "core_form_validations"

    form_definition_id = Column(Integer, ForeignKey("core_form_definitions.id"), nullable=False)
    entity_id = Column(Integer, nullable=False)
    field_name = Column(String(100), nullable=False)
    error_type = Column(String(50), nullable=False)
    error_message = Column(String, nullable=False)
    severity = Column(String(20), nullable=False)  # error, warning, info

# Pydantic Schemas

class ComponentDefinition(BaseModel):
    """Schema for form component definition."""
    type: str
    name: str
    label: str
    required: bool = False
    visible: bool = True
    enabled: bool = True
    default_value: Optional[Any] = None
    validation_rules: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None

    @validator('type')
    def validate_type(cls, v):
        valid_types = {'text', 'number', 'date', 'select', 'checkbox', 'radio', 'grid'}
        if v not in valid_types:
            raise ValueError(f'Invalid component type. Must be one of {valid_types}')
        return v

class ValidationRule(BaseModel):
    """Schema for validation rule."""
    type: str
    message: str
    params: Optional[Dict[str, Any]] = None
    severity: str = 'error'

    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = {'error', 'warning', 'info'}
        if v not in valid_severities:
            raise ValueError(f'Invalid severity. Must be one of {valid_severities}')
        return v

class FormDefinitionSchema(BaseSchema):
    """Schema for form definition."""
    name: str
    title: str
    description: Optional[str] = None
    components: List[ComponentDefinition]
    validation_rules: Dict[str, List[ValidationRule]]
    permissions: Dict[str, List[str]]
    version: int = 1
    is_published: bool = False

    @validator('name')
    def validate_name(cls, v):
        if not v.isidentifier():
            raise ValueError('Name must be a valid Python identifier')
        return v

class FormStateSchema(BaseSchema):
    """Schema for form state."""
    form_definition_id: int
    entity_id: int
    state_data: Dict[str, Any]
    is_dirty: bool = False
    is_new: bool = True
    is_deleted: bool = False
    validation_errors: Optional[Dict[str, List[str]]] = None
    last_modified: Optional[datetime] = None

class FormValidationSchema(BaseSchema):
    """Schema for form validation."""
    form_definition_id: int
    entity_id: int
    field_name: str
    error_type: str
    error_message: str
    severity: str

    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = {'error', 'warning', 'info'}
        if v not in valid_severities:
            raise ValueError(f'Invalid severity. Must be one of {valid_severities}')
        return v
