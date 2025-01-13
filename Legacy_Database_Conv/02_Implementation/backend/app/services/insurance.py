"""
Insurance service layer for AriesOne SaaS application.
Implements business logic for insurance processing, eligibility verification,
and policy management.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.insurance import (
    InsuranceCompany, InsuranceCompanyGroup, CustomerInsurance,
    EligibilityRequest, InsuranceType, EligibilityStatus
)

class InsuranceService:
    """Service for managing insurance companies and groups."""

    def __init__(self, db: Session):
        self.db = db

    def get_company_by_id(self, company_id: int) -> Optional[InsuranceCompany]:
        """Retrieve an insurance company by ID."""
        return self.db.query(InsuranceCompany).filter(InsuranceCompany.id == company_id).first()

    def get_active_companies(self) -> List[InsuranceCompany]:
        """Get all active insurance companies."""
        return self.db.query(InsuranceCompany).filter(
            InsuranceCompany.is_active == True
        ).order_by(InsuranceCompany.name).all()

    def create_company(self, data: Dict[str, Any]) -> InsuranceCompany:
        """Create a new insurance company."""
        company = InsuranceCompany(**data)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update_company(self, company_id: int, data: Dict[str, Any]) -> Optional[InsuranceCompany]:
        """Update an existing insurance company."""
        company = self.get_company_by_id(company_id)
        if not company:
            return None

        for key, value in data.items():
            setattr(company, key, value)

        self.db.commit()
        self.db.refresh(company)
        return company

    def get_company_group_by_id(self, group_id: int) -> Optional[InsuranceCompanyGroup]:
        """Retrieve an insurance company group by ID."""
        return self.db.query(InsuranceCompanyGroup).filter(InsuranceCompanyGroup.id == group_id).first()

    def create_company_group(self, data: Dict[str, Any]) -> InsuranceCompanyGroup:
        """Create a new insurance company group."""
        group = InsuranceCompanyGroup(**data)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

class CustomerInsuranceService:
    """Service for managing customer insurance policies."""

    def __init__(self, db: Session):
        self.db = db

    def get_insurance_by_id(self, insurance_id: int) -> Optional[CustomerInsurance]:
        """Retrieve a customer insurance policy by ID."""
        return self.db.query(CustomerInsurance).filter(CustomerInsurance.id == insurance_id).first()

    def get_customer_insurances(self, customer_id: int) -> List[CustomerInsurance]:
        """Get all insurance policies for a customer."""
        return self.db.query(CustomerInsurance).filter(
            and_(
                CustomerInsurance.customer_id == customer_id,
                CustomerInsurance.is_active == True
            )
        ).order_by(CustomerInsurance.priority).all()

    def create_insurance(self, data: Dict[str, Any]) -> CustomerInsurance:
        """Create a new customer insurance policy."""
        insurance = CustomerInsurance(**data)
        self.db.add(insurance)
        self.db.commit()
        self.db.refresh(insurance)
        return insurance

    def update_insurance(self, insurance_id: int, data: Dict[str, Any]) -> Optional[CustomerInsurance]:
        """Update an existing customer insurance policy."""
        insurance = self.get_insurance_by_id(insurance_id)
        if not insurance:
            return None

        for key, value in data.items():
            setattr(insurance, key, value)

        self.db.commit()
        self.db.refresh(insurance)
        return insurance

    def verify_coverage(self, insurance_id: int, verification_data: Dict[str, Any]) -> CustomerInsurance:
        """Update insurance verification status and information."""
        insurance = self.get_insurance_by_id(insurance_id)
        if not insurance:
            return None

        insurance.last_verified_date = date.today()
        insurance.verification_status = verification_data.get('status', EligibilityStatus.VERIFIED)
        insurance.verification_notes = verification_data.get('notes')

        self.db.commit()
        self.db.refresh(insurance)
        return insurance

class EligibilityService:
    """Service for managing insurance eligibility verification."""

    def __init__(self, db: Session):
        self.db = db

    def create_request(self, data: Dict[str, Any]) -> EligibilityRequest:
        """Create a new eligibility verification request."""
        request = EligibilityRequest(**data)
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def update_request(self, request_id: int, data: Dict[str, Any]) -> Optional[EligibilityRequest]:
        """Update an eligibility verification request with response data."""
        request = self.get_request_by_id(request_id)
        if not request:
            return None

        for key, value in data.items():
            setattr(request, key, value)

        self.db.commit()
        self.db.refresh(request)
        return request

    def get_request_by_id(self, request_id: int) -> Optional[EligibilityRequest]:
        """Retrieve an eligibility request by ID."""
        return self.db.query(EligibilityRequest).filter(EligibilityRequest.id == request_id).first()

    def get_requests_by_insurance(self, insurance_id: int) -> List[EligibilityRequest]:
        """Get all eligibility requests for a customer insurance policy."""
        return self.db.query(EligibilityRequest).filter(
            EligibilityRequest.customer_insurance_id == insurance_id
        ).order_by(EligibilityRequest.request_date.desc()).all()

    def process_eligibility_request(self, request_id: int) -> EligibilityRequest:
        """Process an eligibility request through the clearinghouse."""
        request = self.get_request_by_id(request_id)
        if not request:
            return None

        # TODO: Implement clearinghouse integration
        # This would involve:
        # 1. Preparing the request payload
        # 2. Sending to clearinghouse
        # 3. Processing response
        # 4. Updating request and insurance status

        return request

    def check_eligibility(self, insurance_id: int, service_type: str, service_date: date) -> Dict[str, Any]:
        """Check eligibility for a specific service and date."""
        insurance = self.db.query(CustomerInsurance).filter(CustomerInsurance.id == insurance_id).first()
        if not insurance:
            return {"error": "Insurance not found"}

        # Create eligibility request
        request_data = {
            "customer_insurance_id": insurance_id,
            "request_type": "RealTime",
            "service_type": service_type,
            "service_date": service_date,
            "created_by_id": insurance.last_update_user_id
        }
        request = self.create_request(request_data)

        # Process the request
        processed_request = self.process_eligibility_request(request.id)
        if not processed_request:
            return {"error": "Failed to process eligibility request"}

        return {
            "status": processed_request.response_status,
            "coverage_status": processed_request.coverage_status,
            "coverage_start_date": processed_request.coverage_start_date,
            "coverage_end_date": processed_request.coverage_end_date,
            "deductible_amount": processed_request.deductible_amount,
            "deductible_met": processed_request.deductible_met,
            "out_of_pocket_amount": processed_request.out_of_pocket_amount,
            "out_of_pocket_met": processed_request.out_of_pocket_met,
            "message": processed_request.response_message
        }
