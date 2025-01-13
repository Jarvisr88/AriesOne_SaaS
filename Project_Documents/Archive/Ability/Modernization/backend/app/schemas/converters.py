from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Generic
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.generics import GenericModel
from app.core.logging import logger

T = TypeVar('T')

class BaseConverter(BaseModel):
    """Base converter with common validation"""
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
            UUID: lambda v: str(v)
        }
        
    @classmethod
    def from_orm(cls, obj: Any) -> "BaseConverter":
        """Convert from ORM model"""
        try:
            return super().from_orm(obj)
        except Exception as e:
            logger.error(f"Error converting from ORM: {e}")
            raise ValueError(f"Invalid data for {cls.__name__}")

class DataConverter(GenericModel, Generic[T]):
    """Generic data converter"""
    data: T
    
    class Config:
        arbitrary_types_allowed = True

class PagedResponse(GenericModel, Generic[T]):
    """Paged response converter"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    @validator('pages')
    def compute_pages(cls, v: int, values: Dict[str, Any]) -> int:
        """Compute total pages"""
        if 'total' in values and 'size' in values:
            return (values['total'] + values['size'] - 1) // values['size']
        return v

class MoneyConverter(BaseConverter):
    """Money converter with validation"""
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(..., min_length=3, max_length=3)
    
    @validator('currency')
    def validate_currency(cls, v: str) -> str:
        """Validate currency code"""
        return v.upper()

class DateRangeConverter(BaseConverter):
    """Date range converter"""
    start_date: date
    end_date: date
    
    @root_validator
    def validate_dates(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate date range"""
        start = values.get('start_date')
        end = values.get('end_date')
        if start and end and start > end:
            raise ValueError("End date must be after start date")
        return values

class TimeRangeConverter(BaseConverter):
    """Time range converter"""
    start_time: time
    end_time: time
    
    @root_validator
    def validate_times(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate time range"""
        start = values.get('start_time')
        end = values.get('end_time')
        if start and end and start > end:
            raise ValueError("End time must be after start time")
        return values

class AddressConverter(BaseConverter):
    """Address converter"""
    street: str
    city: str
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., regex=r'^\d{5}(-\d{4})?$')
    country: str = Field(default="US", min_length=2, max_length=2)
    
    @validator('state', 'country')
    def uppercase_code(cls, v: str) -> str:
        """Convert state and country codes to uppercase"""
        return v.upper()

class PhoneConverter(BaseConverter):
    """Phone number converter"""
    number: str = Field(..., regex=r'^\+?1?\d{9,15}$')
    type: Optional[str] = Field(None, max_length=20)
    country_code: str = Field(default="1", regex=r'^\d{1,3}$')

class EmailConverter(BaseConverter):
    """Email converter"""
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    verified: bool = False
    primary: bool = False

class NameConverter(BaseConverter):
    """Name converter"""
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)

class ErrorConverter(BaseConverter):
    """Error converter"""
    code: str
    message: str
    details: Optional[str] = None
    field: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationErrorConverter(BaseConverter):
    """Validation error converter"""
    field: str
    message: str
    code: str
    value: Optional[Any] = None
    
    class Config:
        json_encoders = {
            **BaseConverter.Config.json_encoders,
            Exception: lambda v: str(v)
        }
