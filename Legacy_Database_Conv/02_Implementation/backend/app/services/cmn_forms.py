"""
CMN Forms service layer for AriesOne SaaS application.
Implements business logic for Certificate of Medical Necessity (CMN) forms.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.cmn_forms import (
    BaseCMNForm, CMNFormType, CMNStatus,
    CMNForm0102A, CMNForm0102B, CMNForm48403, CMNFormDROrder
)
from ..models.order import Order
from ..models.customer import Customer
from ..models.medical import Doctor

class CMNFormService:
    """Service for managing CMN forms."""

    def __init__(self, db: Session):
        self.db = db

    def get_form_by_id(self, form_id: int) -> Optional[BaseCMNForm]:
        """Retrieve a CMN form by its ID."""
        return self.db.query(BaseCMNForm).filter(BaseCMNForm.id == form_id).first()

    def get_forms_by_customer(self, customer_id: int) -> List[BaseCMNForm]:
        """Get all CMN forms for a customer."""
        return self.db.query(BaseCMNForm).filter(
            BaseCMNForm.customer_id == customer_id
        ).order_by(BaseCMNForm.created_datetime.desc()).all()

    def get_forms_by_order(self, order_id: int) -> List[BaseCMNForm]:
        """Get all CMN forms associated with an order."""
        return self.db.query(BaseCMNForm).filter(
            BaseCMNForm.order_id == order_id
        ).order_by(BaseCMNForm.created_datetime.desc()).all()

    def get_active_forms_by_type(self, form_type: CMNFormType) -> List[BaseCMNForm]:
        """Get all active forms of a specific type."""
        return self.db.query(BaseCMNForm).filter(
            and_(
                BaseCMNForm.form_type == form_type,
                BaseCMNForm.is_active == True,
                BaseCMNForm.form_status != CMNStatus.VOID
            )
        ).order_by(BaseCMNForm.created_datetime.desc()).all()

    def create_form(self, form_type: CMNFormType, data: Dict[str, Any]) -> BaseCMNForm:
        """Create a new CMN form of the specified type."""
        form_class = self._get_form_class(form_type)
        form = form_class(**data)
        self.db.add(form)
        self.db.commit()
        self.db.refresh(form)
        return form

    def update_form(self, form_id: int, data: Dict[str, Any]) -> Optional[BaseCMNForm]:
        """Update an existing CMN form."""
        form = self.get_form_by_id(form_id)
        if not form:
            return None

        for key, value in data.items():
            setattr(form, key, value)

        self.db.commit()
        self.db.refresh(form)
        return form

    def sign_form(self, form_id: int, doctor_id: int) -> Optional[BaseCMNForm]:
        """Sign a CMN form."""
        form = self.get_form_by_id(form_id)
        if not form:
            return None

        form.form_status = CMNStatus.SIGNED
        form.signed_date = date.today()
        form.last_update_user_id = doctor_id
        form.last_update_datetime = datetime.now()

        self.db.commit()
        self.db.refresh(form)
        return form

    def void_form(self, form_id: int, user_id: int) -> Optional[BaseCMNForm]:
        """Void a CMN form."""
        form = self.get_form_by_id(form_id)
        if not form:
            return None

        form.form_status = CMNStatus.VOID
        form.is_active = False
        form.last_update_user_id = user_id
        form.last_update_datetime = datetime.now()

        self.db.commit()
        self.db.refresh(form)
        return form

    def revise_form(self, form_id: int, data: Dict[str, Any]) -> Optional[BaseCMNForm]:
        """Create a revised version of an existing form."""
        original_form = self.get_form_by_id(form_id)
        if not original_form:
            return None

        # Update original form status
        original_form.form_status = CMNStatus.REVISED
        original_form.is_active = False

        # Create new revision
        data['form_type'] = original_form.form_type
        data['revised_date'] = date.today()
        data['form_status'] = CMNStatus.DRAFT
        
        new_form = self.create_form(original_form.form_type, data)
        
        self.db.commit()
        return new_form

    def validate_form(self, form_id: int) -> Dict[str, List[str]]:
        """Validate a CMN form's data."""
        form = self.get_form_by_id(form_id)
        if not form:
            return {"error": ["Form not found"]}

        errors = {}
        
        # Common validations
        if not form.customer_id:
            errors["customer_id"] = ["Customer is required"]
        if not form.doctor_id:
            errors["doctor_id"] = ["Doctor is required"]
        
        # Form type specific validations
        if isinstance(form, CMNForm0102A):
            errors.update(self._validate_0102a(form))
        elif isinstance(form, CMNForm0102B):
            errors.update(self._validate_0102b(form))
        elif isinstance(form, CMNForm48403):
            errors.update(self._validate_48403(form))
        
        return errors

    def _validate_0102a(self, form: CMNForm0102A) -> Dict[str, List[str]]:
        """Validate DMERC 01.02A form."""
        errors = {}
        
        if not form.test_date:
            errors["test_date"] = ["Test date is required"]
        
        if form.o2_saturation is not None:
            if not (0 <= form.o2_saturation <= 100):
                errors["o2_saturation"] = ["O2 saturation must be between 0 and 100"]
        
        return errors

    def _validate_0102b(self, form: CMNForm0102B) -> Dict[str, List[str]]:
        """Validate DMERC 01.02B form."""
        errors = {}
        
        if not form.answer4:
            errors["answer4"] = ["Answer 4 (date) is required"]
        
        return errors

    def _validate_48403(self, form: CMNForm48403) -> Dict[str, List[str]]:
        """Validate DME 484.03 form."""
        errors = {}
        
        if form.answer1a is not None and form.answer1a < 0:
            errors["answer1a"] = ["Answer 1a must be a positive number"]
        
        if form.answer1b is not None and form.answer1b < 0:
            errors["answer1b"] = ["Answer 1b must be a positive number"]
        
        return errors

    def _get_form_class(self, form_type: CMNFormType) -> type:
        """Get the appropriate form class based on form type."""
        form_classes = {
            CMNFormType.DMERC_0102A: CMNForm0102A,
            CMNFormType.DMERC_0102B: CMNForm0102B,
            CMNFormType.DME_48403: CMNForm48403,
            CMNFormType.DMERC_DRORDER: CMNFormDROrder,
            # Add other form types as they are implemented
        }
        return form_classes.get(form_type, BaseCMNForm)
