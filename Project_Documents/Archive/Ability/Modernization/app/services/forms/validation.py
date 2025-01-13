"""
Form validation service implementation.
"""
from typing import Dict, Any, Optional, List
from pydantic import ValidationError, create_model
from app.services.forms.base import FormValidationService
from app.models.forms import FormModel, FieldModel
from app.db.session import SessionLocal
import logging

logger = logging.getLogger(__name__)

class PydanticFormValidationService(FormValidationService):
    """Pydantic-based form validation service implementation."""
    
    def __init__(self):
        self._validation_cache: Dict[str, Any] = {}
    
    def _build_validation_model(self, form_id: str) -> Any:
        """Build a Pydantic model for form validation."""
        try:
            db = SessionLocal()
            
            # Get form fields
            form = db.query(FormModel).filter(FormModel.id == form_id).first()
            if not form:
                raise ValueError(f"Form not found: {form_id}")
            
            # Build field definitions
            fields: Dict[str, Any] = {}
            for field in form.fields:
                field_type = self._get_field_type(field.type)
                validation = self._build_field_validation(field)
                fields[field.name] = (field_type, validation)
            
            # Create and cache model
            model = create_model(f"Form_{form_id}", **fields)
            self._validation_cache[form_id] = model
            
            return model
            
        finally:
            db.close()
    
    def _get_field_type(self, field_type: str) -> Any:
        """Get Python type for field type."""
        type_mapping = {
            "text": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "email": str,
            "date": str,
            "datetime": str,
            "select": str,
            "multiselect": List[str],
            "file": bytes
        }
        return type_mapping.get(field_type, str)
    
    def _build_field_validation(self, field: FieldModel) -> Dict[str, Any]:
        """Build validation config for a field."""
        validation: Dict[str, Any] = {}
        
        # Required validation
        if field.required:
            validation["required"] = True
        else:
            validation["default"] = None
        
        # Custom validation rules
        if field.validation_rules:
            for rule in field.validation_rules:
                rule_type = rule.get("type")
                if rule_type == "min_length":
                    validation["min_length"] = rule["value"]
                elif rule_type == "max_length":
                    validation["max_length"] = rule["value"]
                elif rule_type == "regex":
                    validation["regex"] = rule["pattern"]
                elif rule_type == "email":
                    validation["email"] = True
                # Add more validation types as needed
        
        return validation
    
    def validate_form(self, form_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form data."""
        try:
            # Get or build validation model
            model = self._validation_cache.get(form_id)
            if not model:
                model = self._build_validation_model(form_id)
            
            # Validate data
            validated_data = model(**data)
            return validated_data.dict()
            
        except ValidationError as e:
            logger.error(f"Validation failed for form {form_id}: {str(e)}")
            return {"errors": e.errors()}
        except Exception as e:
            logger.error(f"Error validating form {form_id}: {str(e)}")
            raise
    
    def add_validation_rule(self, form_id: str, field_id: str, rule: Dict[str, Any]) -> bool:
        """Add a validation rule to a form field."""
        try:
            db = SessionLocal()
            
            # Get field
            field = (
                db.query(FieldModel)
                .filter(
                    FieldModel.form_id == form_id,
                    FieldModel.id == field_id
                )
                .first()
            )
            if not field:
                return False
            
            # Add rule
            if not field.validation_rules:
                field.validation_rules = []
            field.validation_rules.append(rule)
            
            # Clear validation cache
            self._validation_cache.pop(form_id, None)
            
            db.commit()
            logger.info(f"Added validation rule to field {field_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add validation rule: {str(e)}")
            raise
        finally:
            db.close()
    
    def remove_validation_rule(self, form_id: str, field_id: str, rule_id: str) -> bool:
        """Remove a validation rule from a form field."""
        try:
            db = SessionLocal()
            
            # Get field
            field = (
                db.query(FieldModel)
                .filter(
                    FieldModel.form_id == form_id,
                    FieldModel.id == field_id
                )
                .first()
            )
            if not field or not field.validation_rules:
                return False
            
            # Remove rule
            field.validation_rules = [
                rule for rule in field.validation_rules
                if rule.get("id") != rule_id
            ]
            
            # Clear validation cache
            self._validation_cache.pop(form_id, None)
            
            db.commit()
            logger.info(f"Removed validation rule {rule_id} from field {field_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to remove validation rule: {str(e)}")
            raise
        finally:
            db.close()
