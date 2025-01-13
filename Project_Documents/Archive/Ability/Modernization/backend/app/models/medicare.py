from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import Field, validator, constr
from sqlalchemy import Column, String, Date, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.models.base import (
    Base,
    AuditMixin,
    VersionMixin,
    CacheMixin,
    AuditLogMixin,
    BaseSchema,
    BaseCreateSchema,
    BaseUpdateSchema,
    BaseInDBSchema,
)
from app.core.validators import MedicareValidators

class ClaimStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    APPEALED = "APPEALED"

class ClaimType(str, Enum):
    INITIAL = "INITIAL"
    ADJUSTMENT = "ADJUSTMENT"
    VOID = "VOID"
    APPEAL = "APPEAL"

class BeneficiaryType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"

class Coverage(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "coverages"

    id = Column(String, primary_key=True)
    part_a = Column(Integer, nullable=False)
    part_b = Column(Integer, nullable=False)
    part_c = Column(Integer, nullable=False)
    part_d = Column(Integer, nullable=False)
    effective_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    beneficiary_id = Column(String, ForeignKey("beneficiaries.id"), nullable=False)

    beneficiary = relationship("Beneficiary", backref="coverages")

class CoverageSchema(BaseSchema):
    part_a: int = Field(..., ge=0)
    part_b: int = Field(..., ge=0)
    part_c: int = Field(..., ge=0)
    part_d: int = Field(..., ge=0)
    effective_date: date
    end_date: Optional[date] = None
    beneficiary_id: str

class Beneficiary(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "beneficiaries"

    id = Column(String, primary_key=True)
    medicare_id = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String)
    address = Column(JSON)
    contact = Column(JSON)
    eligibility = Column(JSON)
    metadata = Column(JSON)

class BeneficiarySchema(BaseSchema):
    medicare_id: str = Field(..., min_length=11, max_length=11)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    date_of_birth: date
    gender: Optional[str] = None
    address: Dict[str, Any]
    contact: Dict[str, Any]
    eligibility: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("medicare_id")
    def validate_medicare_id(cls, v):
        if not MedicareValidators.medicare_id()(v):
            raise ValueError("Invalid Medicare ID")
        return v

class ServiceCode(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "service_codes"

    id = Column(String, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=False)
    fee_schedule = Column(Integer, nullable=False)
    coverage_percentage = Column(Integer, nullable=False)
    metadata = Column(JSON)

class ServiceCodeSchema(BaseSchema):
    code: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    fee_schedule: int = Field(..., ge=0)
    coverage_percentage: int = Field(..., ge=0, le=100)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ClaimLine(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "claim_lines"

    id = Column(String, primary_key=True)
    service_code_id = Column(String, ForeignKey("service_codes.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    charge_amount = Column(Integer, nullable=False)
    allowed_amount = Column(Integer, nullable=True)
    paid_amount = Column(Integer, nullable=True)
    adjustment_codes = Column(JSON)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)

    service_code = relationship("ServiceCode", backref="claim_lines")
    claim = relationship("Claim", backref="claim_lines")

class ClaimLineSchema(BaseSchema):
    service_code_id: str
    quantity: int = Field(..., ge=0)
    charge_amount: int = Field(..., ge=0)
    allowed_amount: Optional[int] = None
    paid_amount: Optional[int] = None
    adjustment_codes: List[str]
    claim_id: str

class Claim(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "claims"

    id = Column(String, primary_key=True)
    claim_number = Column(String, unique=True, nullable=False, index=True)
    provider_id = Column(String, ForeignKey("providers.id"), nullable=False)
    beneficiary_id = Column(String, ForeignKey("beneficiaries.id"), nullable=False)
    type = Column(SQLEnum(ClaimType), nullable=False)
    status = Column(SQLEnum(ClaimStatus), nullable=False, default=ClaimStatus.PENDING)
    service_date = Column(Date, nullable=False)
    submission_date = Column(DateTime, nullable=False)
    diagnosis_codes = Column(JSON)
    procedure_codes = Column(JSON)
    charges = Column(JSON)
    attachments = Column(JSON)
    metadata = Column(JSON)

    provider = relationship("Provider", backref="claims")
    beneficiary = relationship("Beneficiary", backref="claims")

class ClaimSchema(BaseSchema):
    claim_number: str = Field(..., min_length=1)
    provider_id: str
    beneficiary_id: str
    type: ClaimType
    status: ClaimStatus = ClaimStatus.PENDING
    service_date: date
    submission_date: datetime
    diagnosis_codes: List[str]
    procedure_codes: List[str]
    charges: Dict[str, Any]
    attachments: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("diagnosis_codes")
    def validate_diagnosis_codes(cls, v):
        for code in v:
            if not MedicareValidators.diagnosis_code()(code):
                raise ValueError(f"Invalid diagnosis code: {code}")
        return v

    @validator("procedure_codes")
    def validate_procedure_codes(cls, v):
        for code in v:
            if not MedicareValidators.hcpcs_code()(code):
                raise ValueError(f"Invalid procedure code: {code}")
        return v

class Provider(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "providers"

    id = Column(String, primary_key=True)
    npi = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String)
    taxonomy = Column(String)
    address = Column(JSON)
    contact = Column(JSON)
    credentials = Column(JSON)
    status = Column(String)
    metadata = Column(JSON)

class ProviderSchema(BaseSchema):
    npi: str = Field(..., min_length=10, max_length=10)
    name: str = Field(..., min_length=1)
    specialty: Optional[str] = None
    taxonomy: Optional[str] = None
    address: Dict[str, Any]
    contact: Dict[str, Any]
    credentials: Dict[str, Any]
    status: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("npi")
    def validate_npi(cls, v):
        if not MedicareValidators.npi()(v):
            raise ValueError("Invalid NPI number")
        return v

class EligibilityCheck(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "eligibility_checks"

    id = Column(String, primary_key=True)
    beneficiary_id = Column(String, ForeignKey("beneficiaries.id"), nullable=False)
    provider_id = Column(String, ForeignKey("providers.id"), nullable=False)
    check_date = Column(DateTime, nullable=False)
    service_type = Column(String, nullable=False)
    coverage_status = Column(JSON)
    benefits = Column(JSON)
    limitations = Column(JSON)
    metadata = Column(JSON)

    beneficiary = relationship("Beneficiary", backref="eligibility_checks")
    provider = relationship("Provider", backref="eligibility_checks")

class EligibilityCheckSchema(BaseSchema):
    beneficiary_id: str
    provider_id: str
    check_date: datetime
    service_type: str
    coverage_status: Dict[str, Any]
    benefits: Dict[str, Any]
    limitations: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MainframeError(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "mainframe_errors"

    id = Column(String, primary_key=True)
    code = Column(String, nullable=False)
    message = Column(String, nullable=False)
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    transaction_id = Column(String, nullable=True)

class MainframeErrorSchema(BaseSchema):
    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    details: Optional[str] = None
    timestamp: datetime
    transaction_id: Optional[str] = None

class MainframeResponse(Base, AuditMixin, VersionMixin, CacheMixin, AuditLogMixin):
    __tablename__ = "mainframe_responses"

    id = Column(String, primary_key=True)
    success = Column(Integer, nullable=False)
    data = Column(JSON, nullable=True)
    error_id = Column(String, ForeignKey("mainframe_errors.id"), nullable=True)
    response_time = Column(Integer, nullable=False)
    transaction_id = Column(String, nullable=False)

    error = relationship("MainframeError", backref="mainframe_responses")

class MainframeResponseSchema(BaseSchema):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_id: Optional[str] = None
    response_time: int = Field(..., ge=0)
    transaction_id: str
