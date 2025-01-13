"""
Pydantic schemas for order domain.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, constr, confloat, conint

# Order schemas
class OrderBase(BaseModel):
    order_number: str
    customer_id: int
    order_type: str
    order_status: str = "Draft"
    priority: Optional[int] = 3
    
    # Dates
    order_date: date
    required_date: Optional[date] = None
    ship_date: Optional[date] = None
    delivery_date: Optional[date] = None
    pickup_date: Optional[date] = None
    
    # Locations
    location_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    
    # Medical Information
    doctor_id: Optional[int] = None
    facility_id: Optional[int] = None
    diagnosis_code: Optional[str] = None
    
    # Financial Information
    subtotal: Optional[float] = 0.0
    tax_amount: Optional[float] = 0.0
    shipping_amount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    
    # Insurance Information
    insurance_id: Optional[int] = None
    authorization_number: Optional[str] = None
    authorization_start_date: Optional[date] = None
    authorization_end_date: Optional[date] = None
    
    # Notes
    special_instructions: Optional[str] = None
    internal_notes: Optional[str] = None

class OrderCreate(OrderBase):
    created_by_id: int

class OrderUpdate(OrderBase):
    order_number: Optional[str] = None
    customer_id: Optional[int] = None
    order_type: Optional[str] = None
    order_status: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Order Detail schemas
class OrderDetailBase(BaseModel):
    item_id: int
    quantity: conint(gt=0) = 1
    unit_price: confloat(ge=0.0) = 0.0
    discount_percent: confloat(ge=0.0, le=100.0) = 0.0
    tax_rate: confloat(ge=0.0, le=100.0) = 0.0
    
    # Rental Information
    rental_frequency: Optional[str] = None
    rental_duration: Optional[int] = None
    rental_start_date: Optional[date] = None
    rental_end_date: Optional[date] = None
    
    # Status
    status: str = "Pending"
    is_completed: bool = False
    completed_date: Optional[date] = None

class OrderDetailCreate(OrderDetailBase):
    created_by_id: int

class OrderDetailUpdate(OrderDetailBase):
    item_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    status: Optional[str] = None

class OrderDetailResponse(OrderDetailBase):
    id: int
    order_id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Serial Transaction schemas
class SerialTransactionBase(BaseModel):
    order_id: int
    order_detail_id: int
    item_id: int
    serial_number: constr(min_length=1, max_length=50)
    transaction_type: str
    transaction_date: date
    previous_serial_number: Optional[str] = None
    status: str = "Active"
    is_returned: bool = False
    return_date: Optional[date] = None

class SerialTransactionCreate(SerialTransactionBase):
    created_by_id: int

class SerialTransactionUpdate(SerialTransactionBase):
    order_id: Optional[int] = None
    order_detail_id: Optional[int] = None
    item_id: Optional[int] = None
    serial_number: Optional[str] = None
    transaction_type: Optional[str] = None
    transaction_date: Optional[date] = None

class SerialTransactionResponse(SerialTransactionBase):
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Order Survey schemas
class OrderSurveyBase(BaseModel):
    survey_date: date
    satisfaction_rating: Optional[conint(ge=1, le=5)] = None
    delivery_rating: Optional[conint(ge=1, le=5)] = None
    service_rating: Optional[conint(ge=1, le=5)] = None
    comments: Optional[str] = None
    requires_followup: bool = False
    followup_notes: Optional[str] = None
    followup_date: Optional[date] = None

class OrderSurveyCreate(OrderSurveyBase):
    created_by_id: int

class OrderSurveyUpdate(OrderSurveyBase):
    survey_date: Optional[date] = None
    satisfaction_rating: Optional[int] = None
    delivery_rating: Optional[int] = None
    service_rating: Optional[int] = None

class OrderSurveyResponse(OrderSurveyBase):
    id: int
    order_id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int]
    last_update_datetime: datetime

    class Config:
        from_attributes = True
