"""
Form Management Service Module

This module provides services for form management functionality.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union, cast
from uuid import UUID, uuid4
from fastapi import HTTPException
from ..models.form_management import (
    FormData,
    FormEvent,
    FormMetadata,
    FormState,
    ValidationMessage,
    ValidationResult
)
from .base_service import BaseService
from ..models.entity_events import EntityEvent, EntityCreatedEvent

T = TypeVar('T')

class FormManagementService(BaseService, Generic[T]):
    """Service for form management"""
    
    def __init__(self):
        """Initialize form management service"""
        self._forms: Dict[UUID, FormData] = {}
        self._event_handlers: Dict[str, List[callable]] = {}
    
    async def create_form(
        self,
        form_type: str,
        title: str,
        entity_id: Optional[Union[int, str, UUID]] = None,
        initial_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FormData:
        """
        Create a new form.
        
        Args:
            form_type: Type of form
            title: Form title
            entity_id: Optional entity ID
            initial_data: Optional initial data
            metadata: Optional metadata
            
        Returns:
            Form data
        """
        form_id = uuid4()
        form_metadata = FormMetadata(
            form_id=form_id,
            form_type=form_type,
            title=title,
            entity_id=entity_id,
            metadata=metadata or {}
        )
        
        form_data = FormData(
            metadata=form_metadata,
            data=initial_data or {}
        )
        
        self._forms[form_id] = form_data
        await self._publish_event("form_created", form_id)
        
        return form_data
    
    async def get_form(
        self,
        form_id: UUID
    ) -> Optional[FormData]:
        """
        Get form by ID.
        
        Args:
            form_id: Form ID
            
        Returns:
            Form data if found, None otherwise
        """
        return self._forms.get(form_id)
    
    async def update_form(
        self,
        form_id: UUID,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> FormData:
        """
        Update form data.
        
        Args:
            form_id: Form ID
            data: Updated data
            metadata: Optional metadata update
            
        Returns:
            Updated form data
            
        Raises:
            HTTPException: If form not found
        """
        form = await self.get_form(form_id)
        if not form:
            raise HTTPException(
                status_code=404,
                detail=f"Form not found: {form_id}"
            )
        
        # Track changes
        changes = {
            k: v for k, v in data.items()
            if k not in form.data or form.data[k] != v
        }
        
        # Update data
        form.data.update(data)
        form.changes.update(changes)
        
        # Update metadata
        if metadata:
            form.metadata.metadata.update(metadata)
        
        form.metadata.updated_at = datetime.utcnow()
        form.metadata.state = FormState.MODIFIED
        
        await self._publish_event("form_updated", form_id)
        
        return form
    
    async def validate_form(
        self,
        form_id: UUID
    ) -> ValidationResult:
        """
        Validate form data.
        
        Args:
            form_id: Form ID
            
        Returns:
            Validation result
            
        Raises:
            HTTPException: If form not found
        """
        form = await self.get_form(form_id)
        if not form:
            raise HTTPException(
                status_code=404,
                detail=f"Form not found: {form_id}"
            )
        
        form.metadata.state = FormState.VALIDATING
        
        # Perform validation
        # This should be overridden by specific form implementations
        result = ValidationResult(
            is_valid=True,
            messages=[]
        )
        
        form.metadata.validation = result
        form.metadata.state = FormState.ERROR if not result.is_valid else FormState.MODIFIED
        
        await self._publish_event("form_validated", form_id)
        
        return result
    
    async def save_form(
        self,
        form_id: UUID
    ) -> FormData:
        """
        Save form data.
        
        Args:
            form_id: Form ID
            
        Returns:
            Saved form data
            
        Raises:
            HTTPException: If form not found or validation fails
        """
        form = await self.get_form(form_id)
        if not form:
            raise HTTPException(
                status_code=404,
                detail=f"Form not found: {form_id}"
            )
        
        # Validate before saving
        validation = await self.validate_form(form_id)
        if not validation.is_valid:
            raise HTTPException(
                status_code=400,
                detail="Form validation failed"
            )
        
        form.metadata.state = FormState.SAVING
        
        # Save form data
        # This should be overridden by specific form implementations
        form.metadata.updated_at = datetime.utcnow()
        form.metadata.state = FormState.EXISTING
        form.changes.clear()
        
        await self._publish_event("form_saved", form_id)
        
        return form
    
    async def delete_form(
        self,
        form_id: UUID
    ):
        """
        Delete form.
        
        Args:
            form_id: Form ID
            
        Raises:
            HTTPException: If form not found
        """
        form = await self.get_form(form_id)
        if not form:
            raise HTTPException(
                status_code=404,
                detail=f"Form not found: {form_id}"
            )
        
        form.metadata.state = FormState.DELETED
        await self._publish_event("form_deleted", form_id)
        
        del self._forms[form_id]
    
    async def subscribe(
        self,
        event_type: str,
        handler: callable
    ):
        """
        Subscribe to form events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    async def unsubscribe(
        self,
        event_type: str,
        handler: callable
    ):
        """
        Unsubscribe from form events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type in self._event_handlers and handler in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(handler)
    
    async def _publish_event(
        self,
        event_type: str,
        form_id: UUID,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Publish form event.
        
        Args:
            event_type: Type of event
            form_id: Form ID
            data: Optional event data
        """
        form = await self.get_form(form_id)
        if not form:
            return
        
        event = FormEvent(
            event_type=event_type,
            form_id=form_id,
            entity_id=form.metadata.entity_id,
            data=data
        )
        
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                await handler(event)
