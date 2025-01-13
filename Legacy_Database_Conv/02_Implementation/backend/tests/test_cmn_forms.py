"""
Unit tests for CMN Forms implementation.
"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.cmn_forms import (
    BaseCMNForm, CMNFormType, CMNStatus, AnswerType,
    CMNForm0102A, CMNForm0102B, CMNForm48403, CMNFormDROrder
)
from app.services.cmn_forms import CMNFormService
from app.schemas.cmn_forms import (
    CMNFormCreate, CMNForm0102ACreate, CMNForm0102BCreate,
    CMNForm48403Create, CMNFormDROrderCreate
)

@pytest.fixture
def db_session():
    """Create a test database session."""
    # This would be implemented based on your test database configuration
    pass

@pytest.fixture
def cmn_form_service(db_session):
    """Create a CMNFormService instance for testing."""
    return CMNFormService(db_session)

@pytest.fixture
def sample_form_data():
    """Create sample form data for testing."""
    return {
        "customer_id": 1,
        "doctor_id": 1,
        "order_id": 1,
        "created_by_id": 1,
        "last_update_user_id": 1,
        "initial_date": date.today(),
        "icd10_codes": "E11.9,I10"
    }

class TestCMNFormModels:
    """Test CMN form model classes."""

    def test_base_form_creation(self, db_session):
        """Test creating a base CMN form."""
        form = BaseCMNForm(
            form_type=CMNFormType.DMERC_0102A,
            customer_id=1,
            doctor_id=1,
            created_by_id=1
        )
        assert form.form_status == CMNStatus.DRAFT
        assert form.is_active == True

    def test_form_0102a_creation(self, db_session):
        """Test creating a DMERC 01.02A form."""
        form = CMNForm0102A(
            customer_id=1,
            doctor_id=1,
            created_by_id=1,
            test_date=date.today(),
            o2_saturation=95
        )
        assert form.form_type == CMNFormType.DMERC_0102A
        assert form.o2_saturation == 95

    def test_form_0102b_creation(self, db_session):
        """Test creating a DMERC 01.02B form."""
        form = CMNForm0102B(
            customer_id=1,
            doctor_id=1,
            created_by_id=1,
            answer4=date.today()
        )
        assert form.form_type == CMNFormType.DMERC_0102B
        assert form.answer4 is not None

class TestCMNFormService:
    """Test CMN form service methods."""

    def test_create_form(self, cmn_form_service, sample_form_data):
        """Test form creation through service."""
        form_data = {**sample_form_data, "form_type": CMNFormType.DMERC_0102A}
        form = cmn_form_service.create_form(CMNFormType.DMERC_0102A, form_data)
        assert form.id is not None
        assert form.form_type == CMNFormType.DMERC_0102A
        assert form.form_status == CMNStatus.DRAFT

    def test_get_form_by_id(self, cmn_form_service, sample_form_data):
        """Test retrieving a form by ID."""
        form_data = {**sample_form_data, "form_type": CMNFormType.DMERC_0102A}
        created_form = cmn_form_service.create_form(CMNFormType.DMERC_0102A, form_data)
        retrieved_form = cmn_form_service.get_form_by_id(created_form.id)
        assert retrieved_form is not None
        assert retrieved_form.id == created_form.id

    def test_sign_form(self, cmn_form_service, sample_form_data):
        """Test signing a form."""
        form_data = {**sample_form_data, "form_type": CMNFormType.DMERC_0102A}
        form = cmn_form_service.create_form(CMNFormType.DMERC_0102A, form_data)
        signed_form = cmn_form_service.sign_form(form.id, 1)
        assert signed_form.form_status == CMNStatus.SIGNED
        assert signed_form.signed_date is not None

    def test_void_form(self, cmn_form_service, sample_form_data):
        """Test voiding a form."""
        form_data = {**sample_form_data, "form_type": CMNFormType.DMERC_0102A}
        form = cmn_form_service.create_form(CMNFormType.DMERC_0102A, form_data)
        voided_form = cmn_form_service.void_form(form.id, 1)
        assert voided_form.form_status == CMNStatus.VOID
        assert voided_form.is_active == False

class TestCMNFormValidation:
    """Test CMN form validation rules."""

    def test_validate_0102a(self, cmn_form_service, sample_form_data):
        """Test validation for DMERC 01.02A form."""
        form_data = {
            **sample_form_data,
            "form_type": CMNFormType.DMERC_0102A,
            "o2_saturation": 101  # Invalid value
        }
        form = cmn_form_service.create_form(CMNFormType.DMERC_0102A, form_data)
        errors = cmn_form_service.validate_form(form.id)
        assert "o2_saturation" in errors
        assert len(errors["o2_saturation"]) > 0

    def test_validate_0102b(self, cmn_form_service, sample_form_data):
        """Test validation for DMERC 01.02B form."""
        form_data = {
            **sample_form_data,
            "form_type": CMNFormType.DMERC_0102B,
            "answer4": None  # Required field
        }
        form = cmn_form_service.create_form(CMNFormType.DMERC_0102B, form_data)
        errors = cmn_form_service.validate_form(form.id)
        assert "answer4" in errors
        assert len(errors["answer4"]) > 0

    def test_validate_48403(self, cmn_form_service, sample_form_data):
        """Test validation for DME 484.03 form."""
        form_data = {
            **sample_form_data,
            "form_type": CMNFormType.DME_48403,
            "answer1a": -1  # Invalid value
        }
        form = cmn_form_service.create_form(CMNFormType.DME_48403, form_data)
        errors = cmn_form_service.validate_form(form.id)
        assert "answer1a" in errors
        assert len(errors["answer1a"]) > 0

class TestCMNFormIntegration:
    """Test CMN form integration with other modules."""

    def test_order_integration(self, cmn_form_service, sample_form_data):
        """Test form integration with orders."""
        form_data = {**sample_form_data, "form_type": CMNFormType.DMERC_0102A}
        form = cmn_form_service.create_form(CMNFormType.DMERC_0102A, form_data)
        assert form.order_id == sample_form_data["order_id"]
        assert form.order is not None

    def test_customer_integration(self, cmn_form_service, sample_form_data):
        """Test form integration with customers."""
        form_data = {**sample_form_data, "form_type": CMNFormType.DMERC_0102A}
        form = cmn_form_service.create_form(CMNFormType.DMERC_0102A, form_data)
        assert form.customer_id == sample_form_data["customer_id"]
        assert form.customer is not None

    def test_doctor_integration(self, cmn_form_service, sample_form_data):
        """Test form integration with doctors."""
        form_data = {**sample_form_data, "form_type": CMNFormType.DMERC_0102A}
        form = cmn_form_service.create_form(CMNFormType.DMERC_0102A, form_data)
        assert form.doctor_id == sample_form_data["doctor_id"]
        assert form.doctor is not None
