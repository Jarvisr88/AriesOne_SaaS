"""Properties models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    LargeBinary
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field, validator
import re

from ...Core.Modernization.models.base import Base


class ResourceType(str, Enum):
    """Resource type."""
    STRING = "string"
    IMAGE = "image"
    BINARY = "binary"


class Resource(Base):
    """Resource model."""
    __tablename__ = "resources"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[ResourceType] = mapped_column(SQLEnum(ResourceType))
    culture: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    string_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    binary_value: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )
    metadata: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
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


class ResourceHistory(Base):
    """Resource history model."""
    __tablename__ = "resource_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))
    type: Mapped[ResourceType] = mapped_column(SQLEnum(ResourceType))
    culture: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    string_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    binary_value: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )
    metadata: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)


class Setting(Base):
    """Setting model."""
    __tablename__ = "settings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100))
    value: Mapped[Any] = mapped_column(JSONB)
    type: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    validation: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
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


class SettingHistory(Base):
    """Setting history model."""
    __tablename__ = "setting_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    setting_id: Mapped[int] = mapped_column(ForeignKey("settings.id"))
    value: Mapped[Any] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)


# Pydantic models for API
class ResourceBase(BaseModel):
    """Base resource model."""
    name: str = Field(..., min_length=1, max_length=100)
    type: ResourceType
    culture: Optional[str] = Field(None, min_length=2, max_length=10)
    metadata: Optional[Dict] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Validate resource name."""
        if not re.match(r'^[A-Za-z0-9_]+$', v):
            raise ValueError("Invalid resource name")
        return v
    
    @validator('culture')
    def validate_culture(cls, v):
        """Validate culture code."""
        if v and not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', v):
            raise ValueError("Invalid culture code")
        return v


class ResourceCreate(ResourceBase):
    """Resource create model."""
    value: Union[str, bytes]


class ResourceUpdate(ResourceBase):
    """Resource update model."""
    value: Union[str, bytes]
    reason: Optional[str] = Field(None, max_length=200)


class ResourceResponse(ResourceBase):
    """Resource response model."""
    id: int
    value: Union[str, str]  # Base64 for binary
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class SettingBase(BaseModel):
    """Base setting model."""
    key: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    validation: Optional[str] = Field(None, max_length=200)
    
    @validator('key')
    def validate_key(cls, v):
        """Validate setting key."""
        if not re.match(r'^[A-Za-z0-9_.]+$', v):
            raise ValueError("Invalid setting key")
        return v


class SettingCreate(SettingBase):
    """Setting create model."""
    value: Any


class SettingUpdate(BaseModel):
    """Setting update model."""
    value: Any
    description: Optional[str] = Field(None, max_length=200)
    validation: Optional[str] = Field(None, max_length=200)
    reason: Optional[str] = Field(None, max_length=200)


class SettingResponse(SettingBase):
    """Setting response model."""
    id: int
    value: Any
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class CultureUpdate(BaseModel):
    """Culture update model."""
    culture: str = Field(..., min_length=2, max_length=10)
    
    @validator('culture')
    def validate_culture(cls, v):
        """Validate culture code."""
        if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', v):
            raise ValueError("Invalid culture code")
        return v


class ResourceHistoryResponse(BaseModel):
    """Resource history response model."""
    id: int
    type: ResourceType
    culture: Optional[str]
    value: Union[str, str]  # Base64 for binary
    metadata: Optional[Dict]
    created_at: datetime
    created_by: int
    reason: Optional[str]
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class SettingHistoryResponse(BaseModel):
    """Setting history response model."""
    id: int
    value: Any
    created_at: datetime
    created_by: int
    reason: Optional[str]
    
    class Config:
        """Pydantic config."""
        orm_mode = True
