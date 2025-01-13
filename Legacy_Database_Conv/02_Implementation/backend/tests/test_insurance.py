"""
Unit tests for Insurance Processing implementation.
"""
import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.insurance import (
    InsuranceCompany, InsuranceCompanyGroup, CustomerInsurance,
    EligibilityRequest, InsuranceType, EligibilityStatus
)
from app.services.insurance import InsuranceService, CustomerInsuranceService, EligibilityService
from app.schemas.insurance import (
    InsuranceCompanyCreate, CustomerInsuranceCreate,
    EligibilityRequestCreate, EligibilityCheckRequest
)

@pytest.fixture
def db_session():
    """Create a test database session."""
    # This would be implemented based on your test database configuration
    pass

@pytest.fixture
def insurance_service(db_session):
    """Create an InsuranceService instance for testing."""
    return InsuranceService(db_session)

@pytest.fixture
def customer_insurance_service(db_session):
    """Create a CustomerInsuranceService instance for testing."""
    return CustomerInsuranceService(db_session)

@pytest.fixture
def eligibility_service(db_session):
    """Create an EligibilityService instance for testing."""
    return EligibilityService(db_session)

@pytest.fixture
def sample_company_data():
    """Create sample insurance company data for testing."""
    return {
        "name": "Test Insurance Co",
        "insurance_type": InsuranceType.COMMERCIAL,
        "address1": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "phone": "555-1234",
        "created_by_id": 1,
        "last_update_user_id": 1
    }

@pytest.fixture
def sample_policy_data():
    """Create sample customer insurance policy data for testing."""
    return {
        "customer_id": 1,
        "company_id": 1,
        "policy_number": "POL123",
        "group_number": "GRP456",
        "effective_date": date.today(),
        "created_by_id": 1,
        "last_update_user_id": 1
    }

class TestInsuranceCompany:
    """Test insurance company functionality."""

    def test_create_company(self, insurance_service, sample_company_data):
        """Test creating an insurance company."""
        company = insurance_service.create_company(sample_company_data)
        assert company.id is not None
        assert company.name == sample_company_data["name"]
        assert company.insurance_type == sample_company_data["insurance_type"]

    def test_update_company(self, insurance_service, sample_company_data):
        """Test updating an insurance company."""
        company = insurance_service.create_company(sample_company_data)
        updated_data = {"name": "Updated Insurance Co"}
        updated_company = insurance_service.update_company(company.id, updated_data)
        assert updated_company.name == "Updated Insurance Co"

    def test_get_active_companies(self, insurance_service, sample_company_data):
        """Test retrieving active insurance companies."""
        company = insurance_service.create_company(sample_company_data)
        companies = insurance_service.get_active_companies()
        assert len(companies) > 0
        assert company.id in [c.id for c in companies]

class TestCustomerInsurance:
    """Test customer insurance policy functionality."""

    def test_create_policy(self, customer_insurance_service, sample_policy_data):
        """Test creating a customer insurance policy."""
        policy = customer_insurance_service.create_insurance(sample_policy_data)
        assert policy.id is not None
        assert policy.policy_number == sample_policy_data["policy_number"]
        assert policy.effective_date == sample_policy_data["effective_date"]

    def test_update_policy(self, customer_insurance_service, sample_policy_data):
        """Test updating a customer insurance policy."""
        policy = customer_insurance_service.create_insurance(sample_policy_data)
        updated_data = {"policy_number": "NEWPOL789"}
        updated_policy = customer_insurance_service.update_insurance(policy.id, updated_data)
        assert updated_policy.policy_number == "NEWPOL789"

    def test_verify_coverage(self, customer_insurance_service, sample_policy_data):
        """Test verifying insurance coverage."""
        policy = customer_insurance_service.create_insurance(sample_policy_data)
        verification_data = {
            "status": EligibilityStatus.VERIFIED,
            "notes": "Coverage verified via clearinghouse"
        }
        verified_policy = customer_insurance_service.verify_coverage(policy.id, verification_data)
        assert verified_policy.verification_status == EligibilityStatus.VERIFIED
        assert verified_policy.verification_notes == verification_data["notes"]
        assert verified_policy.last_verified_date is not None

class TestEligibilityVerification:
    """Test eligibility verification functionality."""

    def test_create_eligibility_request(self, eligibility_service):
        """Test creating an eligibility verification request."""
        request_data = {
            "customer_insurance_id": 1,
            "request_type": "RealTime",
            "service_type": "DME",
            "service_date": date.today(),
            "created_by_id": 1
        }
        request = eligibility_service.create_request(request_data)
        assert request.id is not None
        assert request.request_type == request_data["request_type"]
        assert request.service_type == request_data["service_type"]

    def test_update_eligibility_request(self, eligibility_service):
        """Test updating an eligibility request with response data."""
        request_data = {
            "customer_insurance_id": 1,
            "request_type": "RealTime",
            "created_by_id": 1
        }
        request = eligibility_service.create_request(request_data)
        
        response_data = {
            "response_status": EligibilityStatus.VERIFIED,
            "coverage_status": "Active",
            "deductible_amount": Decimal("1000.00"),
            "deductible_met": Decimal("500.00")
        }
        updated_request = eligibility_service.update_request(request.id, response_data)
        assert updated_request.response_status == EligibilityStatus.VERIFIED
        assert updated_request.coverage_status == "Active"
        assert updated_request.deductible_amount == Decimal("1000.00")

    def test_check_eligibility(self, eligibility_service):
        """Test checking eligibility for a service."""
        result = eligibility_service.check_eligibility(
            insurance_id=1,
            service_type="DME",
            service_date=date.today()
        )
        assert "status" in result
        assert result.get("coverage_status") is not None

class TestInsuranceIntegration:
    """Test insurance integration with other modules."""

    def test_customer_policy_integration(self, customer_insurance_service, sample_policy_data):
        """Test policy integration with customer records."""
        policy = customer_insurance_service.create_insurance(sample_policy_data)
        assert policy.customer_id == sample_policy_data["customer_id"]
        assert policy.customer is not None

    def test_eligibility_policy_integration(self, eligibility_service):
        """Test eligibility integration with policies."""
        request_data = {
            "customer_insurance_id": 1,
            "request_type": "RealTime",
            "created_by_id": 1
        }
        request = eligibility_service.create_request(request_data)
        assert request.customer_insurance_id == request_data["customer_insurance_id"]
        assert request.customer_insurance is not None

    def test_verification_workflow(self, customer_insurance_service, eligibility_service, sample_policy_data):
        """Test complete verification workflow."""
        # Create policy
        policy = customer_insurance_service.create_insurance(sample_policy_data)
        
        # Create eligibility request
        request_data = {
            "customer_insurance_id": policy.id,
            "request_type": "RealTime",
            "service_type": "DME",
            "service_date": date.today(),
            "created_by_id": 1
        }
        request = eligibility_service.create_request(request_data)
        
        # Process request
        processed_request = eligibility_service.process_eligibility_request(request.id)
        assert processed_request is not None
        
        # Verify policy updated
        updated_policy = customer_insurance_service.get_insurance_by_id(policy.id)
        assert updated_policy.last_verified_date is not None
