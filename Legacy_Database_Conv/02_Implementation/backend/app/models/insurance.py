"""
Insurance domain models for AriesOne SaaS application.
This module implements insurance-related entities including companies,
eligibility verification, and customer insurance information.
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class InsuranceType(str, Enum):
    """Insurance types."""
    MEDICARE = "Medicare"
    MEDICAID = "Medicaid"
    COMMERCIAL = "Commercial"
    WORKERS_COMP = "WorkersComp"
    AUTO = "Auto"
    OTHER = "Other"

class EligibilityStatus(str, Enum):
    """Eligibility verification status types."""
    PENDING = "Pending"
    VERIFIED = "Verified"
    INACTIVE = "Inactive"
    EXPIRED = "Expired"
    ERROR = "Error"

class InsuranceCompanyGroup(Base):
    """Insurance company group information."""
    __tablename__ = 'insurance_company_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    companies = relationship("InsuranceCompany", back_populates="group")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

class InsuranceCompany(Base):
    """Insurance company information."""
    __tablename__ = 'insurance_companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey('insurance_company_groups.id'))
    insurance_type = Column(SQLEnum(InsuranceType), nullable=False)
    
    # Contact Information
    address1 = Column(String(100))
    address2 = Column(String(100))
    city = Column(String(50))
    state = Column(String(2))
    zip_code = Column(String(10))
    phone = Column(String(20))
    fax = Column(String(20))
    contact_name = Column(String(100))
    contact_title = Column(String(50))
    
    # Payer IDs
    medicare_number = Column(String(20))
    medicaid_number = Column(String(20))
    office_ally_number = Column(String(20))
    zirmed_number = Column(String(20))
    availity_number = Column(String(20))
    ability_number = Column(String(20))
    ability_eligibility_payer_id = Column(String(20))
    
    # Billing Settings
    expected_percent = Column(Numeric(5, 2))
    price_code_id = Column(Integer, ForeignKey('price_codes.id'))
    print_hao_on_invoice = Column(Boolean, default=False)
    print_inv_on_invoice = Column(Boolean, default=False)
    invoice_form_id = Column(Integer, ForeignKey('invoice_forms.id'))
    
    # Tracking
    is_active = Column(Boolean, nullable=False, default=True)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    group = relationship("InsuranceCompanyGroup", back_populates="companies")
    customer_insurances = relationship("CustomerInsurance", back_populates="company")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

class CustomerInsurance(Base):
    """Customer insurance policy information."""
    __tablename__ = 'customer_insurances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('insurance_companies.id'), nullable=False)
    priority = Column(Integer, nullable=False, default=1)
    
    # Policy Information
    policy_number = Column(String(50), nullable=False)
    group_number = Column(String(50))
    subscriber_id = Column(String(50))
    relationship_to_subscriber = Column(String(20))
    
    # Coverage Period
    effective_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    
    # Verification
    last_verified_date = Column(Date)
    verification_status = Column(SQLEnum(EligibilityStatus), nullable=False, default=EligibilityStatus.PENDING)
    verification_notes = Column(String(500))
    
    # Authorization
    authorization_required = Column(Boolean, default=False)
    authorization_number = Column(String(50))
    authorization_start_date = Column(Date)
    authorization_end_date = Column(Date)
    authorization_notes = Column(String(500))
    
    # Tracking
    is_active = Column(Boolean, nullable=False, default=True)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="insurances")
    company = relationship("InsuranceCompany", back_populates="customer_insurances")
    eligibility_requests = relationship("EligibilityRequest", back_populates="customer_insurance")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

class EligibilityRequest(Base):
    """Insurance eligibility verification request."""
    __tablename__ = 'eligibility_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_insurance_id = Column(Integer, ForeignKey('customer_insurances.id'), nullable=False)
    request_date = Column(Date, nullable=False, default=func.current_date())
    request_type = Column(String(20), nullable=False)
    
    # Request Details
    service_type = Column(String(20))
    service_date = Column(Date)
    provider_npi = Column(String(10))
    
    # Response
    response_date = Column(DateTime)
    response_status = Column(SQLEnum(EligibilityStatus))
    response_code = Column(String(20))
    response_message = Column(String(500))
    
    # Coverage Information
    coverage_status = Column(String(20))
    coverage_start_date = Column(Date)
    coverage_end_date = Column(Date)
    deductible_amount = Column(Numeric(10, 2))
    deductible_met = Column(Numeric(10, 2))
    out_of_pocket_amount = Column(Numeric(10, 2))
    out_of_pocket_met = Column(Numeric(10, 2))
    
    # Raw Data
    request_payload = Column(String(2000))
    response_payload = Column(String(2000))
    
    # Tracking
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    customer_insurance = relationship("CustomerInsurance", back_populates="eligibility_requests")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])
