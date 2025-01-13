"""
CMN Forms Pydantic schemas for AriesOne SaaS application.
Defines data validation and serialization for CMN forms.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field

from ..models.cmn_forms import CMNFormType, CMNStatus, AnswerType

class CMNFormBase(BaseModel):
    """Base schema for all CMN forms."""
    form_type: CMNFormType
    form_status: CMNStatus = CMNStatus.DRAFT
    customer_id: int
    doctor_id: int
    order_id: Optional[int] = None
    initial_date: Optional[date] = None
    revised_date: Optional[date] = None
    expiration_date: Optional[date] = None
    signed_date: Optional[date] = None
    icd10_codes: Optional[str] = None
    is_active: bool = True

class CMNFormCreate(CMNFormBase):
    """Schema for creating a new CMN form."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class CMNFormUpdate(BaseModel):
    """Schema for updating an existing CMN form."""
    form_status: Optional[CMNStatus] = None
    doctor_id: Optional[int] = None
    order_id: Optional[int] = None
    initial_date: Optional[date] = None
    revised_date: Optional[date] = None
    expiration_date: Optional[date] = None
    signed_date: Optional[date] = None
    icd10_codes: Optional[str] = None
    is_active: Optional[bool] = None
    last_update_user_id: Optional[int] = None

class CMNForm0102ABase(BaseModel):
    """Base schema for DMERC 01.02A form."""
    answer1: AnswerType = AnswerType.DEFAULT
    answer2: AnswerType = AnswerType.DEFAULT
    answer3: AnswerType = AnswerType.DEFAULT
    answer4: AnswerType = AnswerType.DEFAULT
    answer5: AnswerType = AnswerType.DEFAULT
    test_condition: Optional[str] = None
    test_date: Optional[date] = None
    o2_saturation: Optional[int] = Field(None, ge=0, le=100)
    arterial_po2: Optional[int] = None

class CMNForm0102ACreate(CMNFormBase, CMNForm0102ABase):
    """Schema for creating a DMERC 01.02A form."""
    form_type: CMNFormType = CMNFormType.DMERC_0102A

class CMNForm0102BBase(BaseModel):
    """Base schema for DMERC 01.02B form."""
    answer1: AnswerType = AnswerType.DEFAULT
    answer2: AnswerType = AnswerType.DEFAULT
    answer3: AnswerType = AnswerType.DEFAULT
    answer4: Optional[date] = None
    answer5: Optional[str] = None

class CMNForm0102BCreate(CMNFormBase, CMNForm0102BBase):
    """Schema for creating a DMERC 01.02B form."""
    form_type: CMNFormType = CMNFormType.DMERC_0102B

class CMNForm48403Base(BaseModel):
    """Base schema for DME 484.03 form."""
    answer1a: Optional[int] = Field(None, ge=0)
    answer1b: Optional[int] = Field(None, ge=0)
    answer1c: Optional[date] = None
    answer2a: AnswerType = AnswerType.DEFAULT
    answer2b: AnswerType = AnswerType.DEFAULT
    answer3: AnswerType = AnswerType.DEFAULT
    answer4: AnswerType = AnswerType.DEFAULT
    answer5: Optional[str] = None

class CMNForm48403Create(CMNFormBase, CMNForm48403Base):
    """Schema for creating a DME 484.03 form."""
    form_type: CMNFormType = CMNFormType.DME_48403

class CMNFormDROrderBase(BaseModel):
    """Base schema for DMERC DRORDER form."""
    order_details: Optional[str] = None
    prescription: Optional[str] = None
    special_instructions: Optional[str] = None

class CMNFormDROrderCreate(CMNFormBase, CMNFormDROrderBase):
    """Schema for creating a DMERC DRORDER form."""
    form_type: CMNFormType = CMNFormType.DMERC_DRORDER

class UserRef(BaseModel):
    """Reference to a user."""
    id: int
    username: str

    class Config:
        orm_mode = True

class CustomerRef(BaseModel):
    """Reference to a customer."""
    id: int
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

class DoctorRef(BaseModel):
    """Reference to a doctor."""
    id: int
    first_name: str
    last_name: str
    npi: str

    class Config:
        orm_mode = True

class OrderRef(BaseModel):
    """Reference to an order."""
    id: int
    order_number: str

    class Config:
        orm_mode = True

class CMNFormResponse(CMNFormBase):
    """Schema for CMN form responses."""
    id: int
    created_datetime: datetime
    last_update_datetime: datetime
    customer: CustomerRef
    doctor: DoctorRef
    order: Optional[OrderRef] = None
    created_by: UserRef
    last_update_user: UserRef

    # Form type specific fields will be included based on the form_type
    # These are handled by the FastAPI response model
    class Config:
        orm_mode = True
