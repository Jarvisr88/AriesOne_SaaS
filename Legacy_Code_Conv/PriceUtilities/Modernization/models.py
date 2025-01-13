"""
Models for the Price Utilities module.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, validator, condecimal

class PriceType(str, Enum):
    """Price type enumeration."""
    RENTAL = "rental"
    SALE = "sale"
    BOTH = "both"

class PriceCategory(str, Enum):
    """Price category enumeration."""
    ALLOWABLE = "allowable"
    BILLABLE = "billable"
    COST = "cost"

class ICDCodeType(str, Enum):
    """ICD code type enumeration."""
    ICD9 = "icd9"
    ICD10 = "icd10"

class PriceListItem(BaseModel):
    """Price list item model."""
    id: Optional[str] = Field(None)
    company_id: str
    item_code: str
    description: str
    price_type: PriceType
    rental_price: condecimal(max_digits=10, decimal_places=2) = Field(0)
    sale_price: condecimal(max_digits=10, decimal_places=2) = Field(0)
    allowable_price: condecimal(max_digits=10, decimal_places=2) = Field(0)
    billable_price: condecimal(max_digits=10, decimal_places=2) = Field(0)
    cost_price: condecimal(max_digits=10, decimal_places=2) = Field(0)
    effective_date: datetime
    expiration_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: str
    is_active: bool = True
    metadata: Dict[str, Any] = {}

    class Config:
        """Pydantic config."""
        json_encoders = {
            Decimal: str
        }

class PriceUpdate(BaseModel):
    """Price update model."""
    item_codes: List[str]
    price_type: PriceType
    price_category: PriceCategory
    update_type: str = Field(..., regex="^(fixed|percentage)$")
    update_value: Decimal
    effective_date: datetime
    reason: str
    metadata: Dict[str, Any] = {}

class ICDCode(BaseModel):
    """ICD code model."""
    code: str
    type: ICDCodeType
    description: str
    is_active: bool = True
    effective_date: datetime
    deactivation_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

    @validator('code')
    def validate_code(cls, v, values):
        """Validate ICD code format."""
        if 'type' in values:
            if values['type'] == ICDCodeType.ICD9 and not v.match(r'^\d{3}(\.\d{1,2})?$'):
                raise ValueError('Invalid ICD-9 code format')
            elif values['type'] == ICDCodeType.ICD10 and not v.match(r'^[A-Z]\d{2}(\.\d{1,2})?$'):
                raise ValueError('Invalid ICD-10 code format')
        return v

class PriceParameter(BaseModel):
    """Price parameter model."""
    id: Optional[str] = Field(None)
    company_id: str
    parameter_key: str
    parameter_value: str
    description: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: str
    metadata: Dict[str, Any] = {}

class PriceCalculationRule(BaseModel):
    """Price calculation rule model."""
    id: Optional[str] = Field(None)
    company_id: str
    rule_name: str
    description: str
    price_type: PriceType
    price_category: PriceCategory
    calculation_formula: str
    parameters: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: str
    metadata: Dict[str, Any] = {}

class AuditLog(BaseModel):
    """Audit log model."""
    id: Optional[str] = Field(None)
    company_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    metadata: Dict[str, Any] = {}
