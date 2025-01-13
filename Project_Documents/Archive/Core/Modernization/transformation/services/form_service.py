"""
Form service for the Core module.
Handles form operations, state management, and validation.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy import and_

from .base_service import BaseService
from ..models.form import (
    FormDefinition, FormState, FormValidation,
    FormDefinitionSchema, FormStateSchema, FormValidationSchema
)

class FormService(BaseService):
    """Service for handling form operations."""

    async def create_form_definition(
        self,
        schema: FormDefinitionSchema
    ) -> FormDefinition:
        """Create a new form definition."""
        # Validate form name uniqueness
        existing = await self._get_form_by_name(schema.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Form with name '{schema.name}' already exists"
            )
        
        return await self.create(FormDefinition, schema)

    async def get_form_definition(
        self,
        form_id: int
    ) -> Optional[FormDefinition]:
        """Get form definition by ID."""
        form = await self.get(FormDefinition, form_id)
        if not form:
            raise HTTPException(
                status_code=404,
                detail=f"Form definition {form_id} not found"
            )
        return form

    async def update_form_definition(
        self,
        form_id: int,
        schema: FormDefinitionSchema
    ) -> FormDefinition:
        """Update form definition."""
        # Check if form exists
        existing = await self.get_form_definition(form_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Form definition {form_id} not found"
            )
        
        # Increment version
        schema.version = existing.version + 1
        
        return await self.update(FormDefinition, form_id, schema)

    async def get_form_state(
        self,
        form_id: int,
        entity_id: int
    ) -> Optional[FormState]:
        """Get form state for an entity."""
        query = select(FormState).where(
            and_(
                FormState.form_definition_id == form_id,
                FormState.entity_id == entity_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def save_form_state(
        self,
        schema: FormStateSchema
    ) -> FormState:
        """Save form state."""
        # Check if state exists
        existing_state = await self.get_form_state(
            schema.form_definition_id,
            schema.entity_id
        )
        
        if existing_state:
            # Update existing state
            return await self.update(FormState, existing_state.id, schema)
        else:
            # Create new state
            return await self.create(FormState, schema)

    async def validate_form(
        self,
        form_id: int,
        entity_id: int,
        data: Dict[str, Any]
    ) -> List[FormValidation]:
        """Validate form data."""
        # Get form definition
        form_def = await self.get_form_definition(form_id)
        if not form_def:
            raise HTTPException(
                status_code=404,
                detail=f"Form definition {form_id} not found"
            )

        validation_results = []
        
        # Apply validation rules
        for field, rules in form_def.validation_rules.items():
            field_value = data.get(field)
            
            for rule in rules:
                try:
                    # Apply validation rule
                    is_valid = await self._apply_validation_rule(
                        rule,
                        field_value,
                        data
                    )
                    
                    if not is_valid:
                        # Create validation error
                        validation = await self.create(
                            FormValidation,
                            FormValidationSchema(
                                form_definition_id=form_id,
                                entity_id=entity_id,
                                field_name=field,
                                error_type=rule.type,
                                error_message=rule.message,
                                severity=rule.severity
                            )
                        )
                        validation_results.append(validation)
                
                except Exception as e:
                    await self._log_error(
                        str(e),
                        "validation_error",
                        f"form_{form_id}"
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Validation error: {str(e)}"
                    )

        return validation_results

    async def publish_form(self, form_id: int) -> FormDefinition:
        """Publish a form definition."""
        form = await self.get_form_definition(form_id)
        if not form:
            raise HTTPException(
                status_code=404,
                detail=f"Form definition {form_id} not found"
            )
        
        # Update published status
        form.is_published = True
        await self.db.commit()
        return form

    async def _get_form_by_name(
        self,
        name: str
    ) -> Optional[FormDefinition]:
        """Get form definition by name."""
        query = select(FormDefinition).where(FormDefinition.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _apply_validation_rule(
        self,
        rule: Dict[str, Any],
        value: Any,
        data: Dict[str, Any]
    ) -> bool:
        """Apply a validation rule to a value."""
        rule_type = rule.get('type')
        params = rule.get('params', {})

        if rule_type == 'required':
            return value is not None and value != ''
        
        elif rule_type == 'min_length':
            min_length = params.get('length', 0)
            return len(str(value)) >= min_length if value else False
        
        elif rule_type == 'max_length':
            max_length = params.get('length', 0)
            return len(str(value)) <= max_length if value else True
        
        elif rule_type == 'pattern':
            import re
            pattern = params.get('pattern', '')
            return bool(re.match(pattern, str(value))) if value else False
        
        elif rule_type == 'range':
            min_val = params.get('min')
            max_val = params.get('max')
            if value is None:
                return True
            return (min_val <= value <= max_val)
        
        elif rule_type == 'custom':
            # Execute custom validation function
            func_name = params.get('function')
            if hasattr(self, func_name):
                return await getattr(self, func_name)(value, data)
            return True
        
        return True  # Unknown rule type passes validation
