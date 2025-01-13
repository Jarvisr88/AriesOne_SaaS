"""
Pydantic schemas for medical domain.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr

# CMN Form schemas
class CMNFormBase(BaseModel):
    customer_id: int
    doctor_id: int
    form_type: str
    initial_date: Optional[date] = None
    revised_date: Optional[date] = None
    recertification_date: Optional[date] = None
    pos_type_id: Optional[int] = None
    answering_name: Optional[str] = None
    signature_name: Optional[str] = None
    signature_date: Optional[date] = None
    status: str = "Draft"
    is_active: bool = True

class CMNFormCreate(CMNFormBase):
    created_by_id: int

class CMNFormUpdate(CMNFormBase):
    customer_id: Optional[int] = None
    doctor_id: Optional[int] = None
    form_type: Optional[str] = None

class CMNFormResponse(CMNFormBase):
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Doctor schemas
class DoctorBase(BaseModel):
    npi: Optional[str] = None
    upin: Optional[str] = None
    license_number: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    credentials: Optional[str] = None
    specialty: Optional[str] = None
    address1: str
    address2: Optional[str] = None
    city: str
    state: constr(min_length=2, max_length=2)
    zip_code: str
    phone: str
    fax: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool = True
    inactive_date: Optional[date] = None

class DoctorCreate(DoctorBase):
    created_by_id: int

class DoctorUpdate(DoctorBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None

class DoctorResponse(DoctorBase):
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Facility schemas
class FacilityBase(BaseModel):
    facility_code: str
    name: str
    type: Optional[str] = None
    address1: str
    address2: Optional[str] = None
    city: str
    state: constr(min_length=2, max_length=2)
    zip_code: str
    phone: str
    fax: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool = True
    inactive_date: Optional[date] = None

class FacilityCreate(FacilityBase):
    created_by_id: int

class FacilityUpdate(FacilityBase):
    facility_code: Optional[str] = None
    name: Optional[str] = None
    address1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None

class FacilityResponse(FacilityBase):
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# ICD-10 Code schemas
class ICD10CodeBase(BaseModel):
    code: str
    description: str
    category: Optional[str] = None
    is_active: bool = True

class ICD10CodeCreate(ICD10CodeBase):
    created_by_id: int

class ICD10CodeResponse(ICD10CodeBase):
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# ICD-9 Code schemas
class ICD9CodeBase(BaseModel):
    code: str
    description: str
    category: Optional[str] = None
    icd10_mapping: Optional[str] = None
    is_active: bool = True

class ICD9CodeCreate(ICD9CodeBase):
    created_by_id: int

class ICD9CodeResponse(ICD9CodeBase):
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Doctor-Facility Association schemas
class DoctorFacilityBase(BaseModel):
    doctor_id: int
    facility_id: int
    is_primary: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class DoctorFacilityCreate(DoctorFacilityBase):
    created_by_id: int

class DoctorFacilityResponse(DoctorFacilityBase):
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True
