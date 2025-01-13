"""Price utilities models."""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from sqlalchemy import (
    Column,
    DateTime,
    Date,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field, validator
import re

from ...Core.Modernization.models.base import Base


class PriceListType(str, Enum):
    """Price list type."""
    DEFAULT = "default"
    CUSTOM = "custom"
    TEMPORARY = "temporary"


class PriceList(Base):
    """Price list model."""
    __tablename__ = "price_lists"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[PriceListType] = mapped_column(SQLEnum(PriceListType))
    effective_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    items: Mapped[List["PriceItem"]] = relationship(
        back_populates="price_list",
        cascade="all, delete-orphan"
    )


class PriceItem(Base):
    """Price item model."""
    __tablename__ = "price_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    price_list_id: Mapped[int] = mapped_column(ForeignKey("price_lists.id"))
    billing_code: Mapped[str] = mapped_column(String(20))
    rent_allowable: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    rent_billable: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    sale_allowable: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    sale_billable: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    effective_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    price_list: Mapped[PriceList] = relationship(back_populates="items")


class PriceHistory(Base):
    """Price history model."""
    __tablename__ = "price_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    price_item_id: Mapped[int] = mapped_column(ForeignKey("price_items.id"))
    rent_allowable: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    rent_billable: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    sale_allowable: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    sale_billable: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    effective_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)


class ICD9Code(Base):
    """ICD-9 code model."""
    __tablename__ = "icd9_codes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10))
    description: Mapped[str] = mapped_column(String(200))
    effective_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    replaced_by: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))


# Pydantic models for API
class PriceListBase(BaseModel):
    """Base price list model."""
    name: str = Field(..., min_length=1, max_length=100)
    type: PriceListType
    effective_date: date
    end_date: Optional[date] = None
    is_active: bool = True


class PriceListCreate(PriceListBase):
    """Price list create model."""
    pass


class PriceListUpdate(PriceListBase):
    """Price list update model."""
    pass


class PriceListResponse(PriceListBase):
    """Price list response model."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class PriceItemBase(BaseModel):
    """Base price item model."""
    billing_code: str = Field(..., min_length=5, max_length=20)
    rent_allowable: Decimal = Field(..., ge=0, decimal_places=2)
    rent_billable: Decimal = Field(..., ge=0, decimal_places=2)
    sale_allowable: Decimal = Field(..., ge=0, decimal_places=2)
    sale_billable: Decimal = Field(..., ge=0, decimal_places=2)
    effective_date: date
    end_date: Optional[date] = None
    
    @validator('billing_code')
    def validate_code(cls, v):
        """Validate billing code."""
        if not re.match(r'^[A-Z0-9]{5,20}$', v):
            raise ValueError("Invalid billing code format")
        return v
    
    @validator('rent_billable')
    def validate_rent_billable(cls, v, values):
        """Validate rent billable price."""
        if 'rent_allowable' in values and v > values['rent_allowable']:
            raise ValueError("Rent billable cannot exceed allowable")
        return v
    
    @validator('sale_billable')
    def validate_sale_billable(cls, v, values):
        """Validate sale billable price."""
        if 'sale_allowable' in values and v > values['sale_allowable']:
            raise ValueError("Sale billable cannot exceed allowable")
        return v


class PriceItemCreate(PriceItemBase):
    """Price item create model."""
    price_list_id: int


class PriceItemUpdate(PriceItemBase):
    """Price item update model."""
    reason: Optional[str] = Field(None, max_length=200)


class PriceItemResponse(PriceItemBase):
    """Price item response model."""
    id: int
    price_list_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class ICD9CodeBase(BaseModel):
    """Base ICD-9 code model."""
    code: str = Field(..., min_length=3, max_length=10)
    description: str = Field(..., min_length=1, max_length=200)
    effective_date: date
    end_date: Optional[date] = None
    replaced_by: Optional[str] = Field(None, min_length=3, max_length=10)
    
    @validator('code')
    def validate_code(cls, v):
        """Validate ICD-9 code."""
        if not re.match(r'^\d{3}(\.\d{1,2})?$', v):
            raise ValueError("Invalid ICD-9 code format")
        return v
    
    @validator('replaced_by')
    def validate_replaced_by(cls, v):
        """Validate replacement code."""
        if v and not re.match(r'^\d{3}(\.\d{1,2})?$', v):
            raise ValueError("Invalid replacement code format")
        return v


class ICD9CodeCreate(ICD9CodeBase):
    """ICD-9 code create model."""
    pass


class ICD9CodeUpdate(ICD9CodeBase):
    """ICD-9 code update model."""
    pass


class ICD9CodeResponse(ICD9CodeBase):
    """ICD-9 code response model."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class BulkUpdateRequest(BaseModel):
    """Bulk update request model."""
    items: List[PriceItemUpdate]
    update_orders: bool = False


class BulkUpdateResponse(BaseModel):
    """Bulk update response model."""
    total_items: int
    updated_items: int
    errors: List[str]
    warnings: List[str]


class FileUploadResponse(BaseModel):
    """File upload response model."""
    filename: str
    total_rows: int
    valid_rows: int
    errors: List[str]
    warnings: List[str]
