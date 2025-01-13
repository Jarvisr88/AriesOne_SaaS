from typing import Dict, List, Optional, Union
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field, validator, root_validator
from app.schemas.converters import (
    BaseConverter,
    MoneyConverter,
    DateRangeConverter,
    AddressConverter,
    PhoneConverter,
    EmailConverter,
    NameConverter
)

class NPIConverter(BaseConverter):
    """NPI number converter"""
    npi: str = Field(..., min_length=10, max_length=10)
    
    @validator('npi')
    def validate_npi(cls, v: str) -> str:
        """Validate NPI checksum"""
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Invalid NPI format")
            
        # NPI checksum validation
        digits = [int(d) for d in v]
        check_digit = digits.pop()
        
        # Multiply even positions by 2
        for i in range(0, len(digits), 2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        # Calculate checksum
        checksum = (sum(digits) * 9) % 10
        if checksum != check_digit:
            raise ValueError("Invalid NPI checksum")
            
        return v

class MedicareIdConverter(BaseConverter):
    """Medicare ID converter"""
    medicare_id: str = Field(..., min_length=11, max_length=11)
    
    @validator('medicare_id')
    def validate_medicare_id(cls, v: str) -> str:
        """Validate Medicare ID format"""
        if not v[0].isdigit() or not v[1].isalpha():
            raise ValueError("Invalid Medicare ID format")
        if not v[2].isdigit() or not v[3].isalpha():
            raise ValueError("Invalid Medicare ID format")
        if not v[4].isdigit() or not v[5].isalpha():
            raise ValueError("Invalid Medicare ID format")
        if not v[6:9].isdigit():
            raise ValueError("Invalid Medicare ID format")
        if not v[9].isalpha():
            raise ValueError("Invalid Medicare ID format")
        return v

class DiagnosisCodeConverter(BaseConverter):
    """ICD-10 diagnosis code converter"""
    code: str = Field(..., regex=r'^[A-Z][0-9]{2}(\.[0-9]{1,4})?$')
    description: Optional[str] = None
    
    @validator('code')
    def validate_icd10(cls, v: str) -> str:
        """Validate ICD-10 format"""
        return v.upper()

class ProcedureCodeConverter(BaseConverter):
    """HCPCS/CPT code converter"""
    code: str
    description: Optional[str] = None
    
    @validator('code')
    def validate_procedure_code(cls, v: str) -> str:
        """Validate HCPCS/CPT format"""
        # Level I (CPT) codes: 5 digits
        if v.isdigit() and len(v) == 5:
            return v
        
        # Level II codes: Letter followed by 4 digits
        if (len(v) == 5 and 
            v[0].isalpha() and 
            v[1:].isdigit()):
            return v.upper()
        
        raise ValueError("Invalid procedure code format")

class ModifierConverter(BaseConverter):
    """Procedure modifier converter"""
    modifier: str = Field(..., min_length=2, max_length=2)
    description: Optional[str] = None
    
    @validator('modifier')
    def validate_modifier(cls, v: str) -> str:
        """Validate modifier format"""
        if not (v.isalnum() and len(v) == 2):
            raise ValueError("Invalid modifier format")
        return v.upper()

class ClaimLineConverter(BaseConverter):
    """Claim line converter"""
    procedure_code: ProcedureCodeConverter
    modifiers: List[ModifierConverter] = Field(default_factory=list)
    quantity: Decimal = Field(..., gt=0)
    charge_amount: MoneyConverter
    service_date: date
    place_of_service: str = Field(..., min_length=2, max_length=2)
    
    @validator('modifiers')
    def validate_modifiers(cls, v: List[ModifierConverter]) -> List[ModifierConverter]:
        """Validate modifier list"""
        if len(v) > 4:
            raise ValueError("Maximum 4 modifiers allowed")
        return v

class ClaimConverter(BaseConverter):
    """Claim converter"""
    claim_number: str
    patient: MedicareIdConverter
    provider: NPIConverter
    diagnosis_codes: List[DiagnosisCodeConverter]
    service_lines: List[ClaimLineConverter]
    total_charge: MoneyConverter
    service_date_range: DateRangeConverter
    submission_date: datetime = Field(default_factory=datetime.utcnow)
    
    @root_validator
    def validate_claim(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate claim totals"""
        lines = values.get('service_lines', [])
        total = values.get('total_charge')
        if lines and total:
            line_total = sum(line.charge_amount.amount for line in lines)
            if line_total != total.amount:
                raise ValueError("Claim total does not match line items")
        return values

class EligibilityConverter(BaseConverter):
    """Eligibility converter"""
    medicare_id: MedicareIdConverter
    coverage_start: date
    coverage_end: Optional[date] = None
    part_a: bool = False
    part_b: bool = False
    part_c: bool = False
    part_d: bool = False
    
    @root_validator
    def validate_coverage(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coverage dates"""
        start = values.get('coverage_start')
        end = values.get('coverage_end')
        if start and end and start > end:
            raise ValueError("Coverage end date must be after start date")
        return values
