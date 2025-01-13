"""
Pydantic schemas for customer domain.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, constr

# Customer schemas
class CustomerBase(BaseModel):
    account_number: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    courtesy: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    
    address1: str
    address2: Optional[str] = None
    city: str
    state: constr(min_length=2, max_length=2)
    zip_code: str
    phone: str
    phone2: Optional[str] = None
    delivery_directions: Optional[str] = None
    
    employment_status: str
    marital_status: str
    military_status: str
    student_status: str
    
    billing_type_id: Optional[int] = None
    customer_class_code: Optional[str] = None
    customer_type_id: Optional[int] = None
    
    bill_active: bool = False
    bill_name: Optional[str] = None
    bill_address1: Optional[str] = None
    bill_address2: Optional[str] = None
    bill_city: Optional[str] = None
    bill_state: Optional[str] = None
    bill_zip: Optional[str] = None
    
    ship_active: bool = False
    ship_name: Optional[str] = None
    ship_address1: Optional[str] = None
    ship_address2: Optional[str] = None
    ship_city: Optional[str] = None
    ship_state: Optional[str] = None
    ship_zip: Optional[str] = None
    
    commercial_account: Optional[bool] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    account_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    customer_balance: Optional[float] = None
    total_balance: Optional[float] = None
    deceased_date: Optional[date] = None
    setup_date: Optional[date] = None
    inactive_date: Optional[date] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Insurance schemas
class CustomerInsuranceBase(BaseModel):
    insurance_id: int
    policy_number: str
    group_number: Optional[str] = None
    priority: int
    effective_date: Optional[date] = None
    termination_date: Optional[date] = None
    verification_date: Optional[date] = None
    copay_amount: Optional[float] = None
    copay_percent: Optional[float] = None

class CustomerInsuranceCreate(CustomerInsuranceBase):
    pass

class CustomerInsuranceUpdate(CustomerInsuranceBase):
    insurance_id: Optional[int] = None
    policy_number: Optional[str] = None
    priority: Optional[int] = None

class CustomerInsuranceResponse(CustomerInsuranceBase):
    id: int
    customer_id: int
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Note schemas
class CustomerNoteBase(BaseModel):
    note_type_id: int
    note_text: str

class CustomerNoteCreate(CustomerNoteBase):
    pass

class CustomerNoteResponse(CustomerNoteBase):
    id: int
    customer_id: int
    note_date: datetime
    created_by_id: int
    created_datetime: datetime
    last_update_datetime: datetime

    class Config:
        from_attributes = True
