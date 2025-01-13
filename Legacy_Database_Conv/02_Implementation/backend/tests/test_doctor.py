"""
Unit tests for Doctor Management implementation.
"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.doctor import (
    Doctor, DoctorType, ProviderNumber, ProviderNumberType
)
from app.services.doctor import DoctorService, ProviderNumberService
from app.schemas.doctor import (
    DoctorCreate, DoctorUpdate,
    ProviderNumberCreate, ProviderNumberUpdate
)

@pytest.fixture
def db_session():
    """Create a test database session."""
    # This would be implemented based on your test database configuration
    pass

@pytest.fixture
def doctor_service(db_session):
    """Create a DoctorService instance for testing."""
    return DoctorService(db_session)

@pytest.fixture
def provider_number_service(db_session):
    """Create a ProviderNumberService instance for testing."""
    return ProviderNumberService(db_session)

@pytest.fixture
def sample_doctor_data():
    """Create sample doctor data for testing."""
    return {
        "courtesy": "Dr.",
        "first_name": "John",
        "middle_name": "A",
        "last_name": "Smith",
        "suffix": "MD",
        "title": "Physician",
        "address1": "123 Medical Center Dr",
        "city": "Test City",
        "state": "TS",
        "zip": "12345",
        "phone": "555-1234",
        "npi": "1234567890",
        "upin_number": "12345",
        "license_number": "MED123456",
        "medicaid_number": "MC123456",
        "fed_tax_id": "123456789",
        "created_by_id": 1,
        "last_update_user_id": 1
    }

@pytest.fixture
def sample_provider_number_data():
    """Create sample provider number data for testing."""
    return {
        "doctor_id": 1,
        "type_id": 1,
        "number": "PRV123456",
        "expiration_date": date.today(),
        "created_by_id": 1,
        "last_update_user_id": 1
    }

class TestDoctorManagement:
    """Test doctor management functionality."""

    def test_create_doctor(self, doctor_service, sample_doctor_data):
        """Test creating a doctor."""
        doctor = doctor_service.create_doctor(DoctorCreate(**sample_doctor_data))
        assert doctor.id is not None
        assert doctor.first_name == sample_doctor_data["first_name"]
        assert doctor.last_name == sample_doctor_data["last_name"]
        assert doctor.npi == sample_doctor_data["npi"]

    def test_update_doctor(self, doctor_service, sample_doctor_data):
        """Test updating a doctor."""
        doctor = doctor_service.create_doctor(DoctorCreate(**sample_doctor_data))
        updated_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "last_update_user_id": 1
        }
        updated_doctor = doctor_service.update_doctor(doctor.id, DoctorUpdate(**updated_data))
        assert updated_doctor.first_name == "Jane"
        assert updated_doctor.last_name == "Doe"

    def test_get_doctors_with_filters(self, doctor_service, sample_doctor_data):
        """Test retrieving doctors with filters."""
        # Create test doctors
        doctor1 = doctor_service.create_doctor(DoctorCreate(**sample_doctor_data))
        doctor2 = doctor_service.create_doctor(DoctorCreate(**{
            **sample_doctor_data,
            "first_name": "Jane",
            "pecos_enrolled": True
        }))

        # Test type filter
        doctors = doctor_service.get_doctors(type_id=1)
        assert len(doctors) > 0
        assert all(d.type_id == 1 for d in doctors)

        # Test PECOS filter
        doctors = doctor_service.get_doctors(pecos_enrolled=True)
        assert len(doctors) == 1
        assert doctors[0].id == doctor2.id

    def test_verify_credentials(self, doctor_service, sample_doctor_data):
        """Test credential verification."""
        # Create doctor with expired license
        expired_data = {
            **sample_doctor_data,
            "license_expired": date(2024, 12, 31)
        }
        doctor = doctor_service.create_doctor(DoctorCreate(**expired_data))

        status = doctor_service.verify_credentials(doctor.id)
        assert status["license_active"] is False
        assert status["license_expiration"] == date(2024, 12, 31)
        assert "npi" not in status["missing_identifiers"]

class TestProviderNumbers:
    """Test provider number functionality."""

    def test_create_provider_number(self, provider_number_service, sample_provider_number_data):
        """Test creating a provider number."""
        number = provider_number_service.create_provider_number(
            ProviderNumberCreate(**sample_provider_number_data)
        )
        assert number.id is not None
        assert number.number == sample_provider_number_data["number"]
        assert number.doctor_id == sample_provider_number_data["doctor_id"]

    def test_update_provider_number(self, provider_number_service, sample_provider_number_data):
        """Test updating a provider number."""
        number = provider_number_service.create_provider_number(
            ProviderNumberCreate(**sample_provider_number_data)
        )
        updated_data = {
            "number": "NEWPRV789",
            "last_update_user_id": 1
        }
        updated_number = provider_number_service.update_provider_number(
            number.id,
            ProviderNumberUpdate(**updated_data)
        )
        assert updated_number.number == "NEWPRV789"

    def test_get_provider_numbers(self, provider_number_service, sample_provider_number_data):
        """Test retrieving provider numbers."""
        # Create test numbers
        number1 = provider_number_service.create_provider_number(
            ProviderNumberCreate(**sample_provider_number_data)
        )
        number2 = provider_number_service.create_provider_number(
            ProviderNumberCreate(**{
                **sample_provider_number_data,
                "type_id": 2,
                "is_active": False
            })
        )

        # Test type filter
        numbers = provider_number_service.get_provider_numbers(
            doctor_id=1,
            type_id=1
        )
        assert len(numbers) == 1
        assert numbers[0].id == number1.id

        # Test active filter
        numbers = provider_number_service.get_provider_numbers(
            doctor_id=1,
            active_only=True
        )
        assert len(numbers) == 1
        assert numbers[0].id == number1.id

    def test_verify_provider_numbers(self, provider_number_service, sample_provider_number_data):
        """Test provider number verification."""
        # Create expired number
        expired_data = {
            **sample_provider_number_data,
            "expiration_date": date(2024, 12, 31)
        }
        number = provider_number_service.create_provider_number(
            ProviderNumberCreate(**expired_data)
        )

        status = provider_number_service.verify_provider_numbers(number.doctor_id)
        assert len(status["expired"]) == 1
        assert status["expired"][0]["id"] == number.id
        assert status["expired"][0]["expiration"] == date(2024, 12, 31)

class TestIntegration:
    """Test doctor management integration."""

    def test_doctor_type_relationship(self, doctor_service, sample_doctor_data):
        """Test doctor-type relationship."""
        doctor = doctor_service.create_doctor(DoctorCreate(**{
            **sample_doctor_data,
            "type_id": 1
        }))
        assert doctor.doctor_type is not None
        assert doctor.doctor_type.id == 1

    def test_provider_number_relationship(
        self,
        doctor_service,
        provider_number_service,
        sample_doctor_data,
        sample_provider_number_data
    ):
        """Test doctor-provider number relationship."""
        # Create doctor
        doctor = doctor_service.create_doctor(DoctorCreate(**sample_doctor_data))

        # Create provider number
        number_data = {
            **sample_provider_number_data,
            "doctor_id": doctor.id
        }
        number = provider_number_service.create_provider_number(
            ProviderNumberCreate(**number_data)
        )

        # Verify relationship
        doctor = doctor_service.get_doctor_by_id(doctor.id)
        assert len(doctor.provider_numbers) == 1
        assert doctor.provider_numbers[0].id == number.id

    def test_credential_verification_workflow(
        self,
        doctor_service,
        provider_number_service,
        sample_doctor_data,
        sample_provider_number_data
    ):
        """Test complete credential verification workflow."""
        # Create doctor with expired license
        doctor_data = {
            **sample_doctor_data,
            "license_expired": date(2024, 12, 31)
        }
        doctor = doctor_service.create_doctor(DoctorCreate(**doctor_data))

        # Create expired provider number
        number_data = {
            **sample_provider_number_data,
            "doctor_id": doctor.id,
            "expiration_date": date(2024, 12, 31)
        }
        number = provider_number_service.create_provider_number(
            ProviderNumberCreate(**number_data)
        )

        # Verify credentials
        doctor_status = doctor_service.verify_credentials(doctor.id)
        assert doctor_status["license_active"] is False

        # Verify provider numbers
        number_status = provider_number_service.verify_provider_numbers(doctor.id)
        assert len(number_status["expired"]) == 1
