"""
Form builder service implementation.
"""
from typing import Dict, Any, Optional, List
import uuid
from sqlalchemy.orm import Session
from app.services.forms.base import FormBuilderService, FormConfig
from app.models.forms import FormModel, FieldModel
from app.db.session import SessionLocal
import logging

logger = logging.getLogger(__name__)

class SQLFormBuilderService(FormBuilderService):
    """SQL-based form builder service implementation."""
    
    def __init__(self):
        self._db: Optional[Session] = None
    
    def _get_db(self) -> Session:
        """Get database session."""
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def _close_db(self) -> None:
        """Close database session."""
        if self._db is not None:
            self._db.close()
            self._db = None
    
    def create_form(self, config: FormConfig) -> str:
        """Create a new form."""
        try:
            db = self._get_db()
            
            # Create form record
            form = FormModel(
                id=str(uuid.uuid4()),
                title=config.title,
                description=config.description,
                submit_endpoint=config.submit_endpoint,
                success_message=config.success_message,
                error_message=config.error_message
            )
            db.add(form)
            
            # Create field records
            for field_config in config.fields:
                field = FieldModel(
                    id=field_config.id,
                    form_id=form.id,
                    type=field_config.type,
                    label=field_config.label,
                    name=field_config.name,
                    required=field_config.required,
                    placeholder=field_config.placeholder,
                    description=field_config.description,
                    validation_rules=field_config.validation_rules,
                    options=field_config.options,
                    default_value=field_config.default_value
                )
                db.add(field)
            
            db.commit()
            logger.info(f"Created form with ID: {form.id}")
            return form.id
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create form: {str(e)}")
            raise
        finally:
            self._close_db()
    
    def get_form(self, form_id: str) -> Optional[FormConfig]:
        """Retrieve a form configuration."""
        try:
            db = self._get_db()
            
            # Get form and fields
            form = db.query(FormModel).filter(FormModel.id == form_id).first()
            if not form:
                return None
            
            # Convert to FormConfig
            return FormConfig(
                id=form.id,
                title=form.title,
                description=form.description,
                submit_endpoint=form.submit_endpoint,
                success_message=form.success_message,
                error_message=form.error_message,
                fields=[
                    field.to_field_config()
                    for field in form.fields
                ]
            )
            
        except Exception as e:
            logger.error(f"Failed to get form: {str(e)}")
            raise
        finally:
            self._close_db()
    
    def update_form(self, form_id: str, config: FormConfig) -> bool:
        """Update an existing form."""
        try:
            db = self._get_db()
            
            # Get existing form
            form = db.query(FormModel).filter(FormModel.id == form_id).first()
            if not form:
                return False
            
            # Update form
            form.title = config.title
            form.description = config.description
            form.submit_endpoint = config.submit_endpoint
            form.success_message = config.success_message
            form.error_message = config.error_message
            
            # Delete existing fields
            db.query(FieldModel).filter(FieldModel.form_id == form_id).delete()
            
            # Create new fields
            for field_config in config.fields:
                field = FieldModel(
                    id=field_config.id,
                    form_id=form.id,
                    type=field_config.type,
                    label=field_config.label,
                    name=field_config.name,
                    required=field_config.required,
                    placeholder=field_config.placeholder,
                    description=field_config.description,
                    validation_rules=field_config.validation_rules,
                    options=field_config.options,
                    default_value=field_config.default_value
                )
                db.add(field)
            
            db.commit()
            logger.info(f"Updated form with ID: {form_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update form: {str(e)}")
            raise
        finally:
            self._close_db()
    
    def delete_form(self, form_id: str) -> bool:
        """Delete a form."""
        try:
            db = self._get_db()
            
            # Delete form and fields (cascade)
            result = db.query(FormModel).filter(FormModel.id == form_id).delete()
            
            db.commit()
            logger.info(f"Deleted form with ID: {form_id}")
            return result > 0
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete form: {str(e)}")
            raise
        finally:
            self._close_db()
