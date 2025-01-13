"""
Form Management Models Module

This module provides models for form management functionality.
"""
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field

class FormState(str, Enum):
    """Form state enumeration"""
    NEW = "new"
    EXISTING = "existing"
    MODIFIED = "modified"
    DELETED = "deleted"
    LOADING = "loading"
    SAVING = "saving"
    VALIDATING = "validating"
    ERROR = "error"

class ButtonConfig(BaseModel):
    """Button configuration model"""
    button_clone: bool = Field(default=True, description="Enable clone button")
    button_close: bool = Field(default=True, description="Enable close button")
    button_delete: bool = Field(default=True, description="Enable delete button")
    button_missing: bool = Field(default=True, description="Enable missing button")
    button_new: bool = Field(default=True, description="Enable new button")
    button_reload: bool = Field(default=True, description="Enable reload button")
    button_save: bool = Field(default=True, description="Enable save button")
    button_search: bool = Field(default=True, description="Enable search button")
    button_print: bool = Field(default=False, description="Enable print button")
    button_goto: bool = Field(default=True, description="Enable goto button")
    button_actions: bool = Field(default=True, description="Enable actions button")
    button_filter: bool = Field(default=True, description="Enable filter button")

class ValidationMessage(BaseModel):
    """Validation message model"""
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Validation message")
    severity: str = Field(..., description="Message severity (error, warning, info)")
    code: Optional[str] = Field(None, description="Error code")

class ValidationResult(BaseModel):
    """Validation result model"""
    is_valid: bool = Field(..., description="Validation result")
    messages: List[ValidationMessage] = Field(default_factory=list, description="Validation messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class FormMetadata(BaseModel):
    """Form metadata model"""
    form_id: UUID = Field(..., description="Form ID")
    form_type: str = Field(..., description="Form type")
    title: str = Field(..., description="Form title")
    state: FormState = Field(default=FormState.NEW, description="Form state")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    entity_id: Optional[Union[int, str, UUID]] = Field(None, description="Associated entity ID")
    validation: Optional[ValidationResult] = Field(None, description="Validation result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class FormData(BaseModel):
    """Form data model"""
    metadata: FormMetadata = Field(..., description="Form metadata")
    data: Dict[str, Any] = Field(default_factory=dict, description="Form data")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Tracked changes")
    buttons: ButtonConfig = Field(default_factory=ButtonConfig, description="Button configuration")

class FormEvent(BaseModel):
    """Form event model"""
    event_type: str = Field(..., description="Event type")
    form_id: UUID = Field(..., description="Form ID")
    entity_id: Optional[Union[int, str, UUID]] = Field(None, description="Entity ID")
    data: Optional[Dict[str, Any]] = Field(None, description="Event data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
