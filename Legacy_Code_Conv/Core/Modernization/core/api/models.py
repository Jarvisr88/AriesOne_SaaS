"""
API Models Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, constr


class TenantBase(BaseModel):
    """Base tenant model."""
    name: constr(min_length=1, max_length=100)
    slug: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    subscription_plan: str = "free"
    theme: Optional[str] = "default"
    timezone: str = "UTC"


class TenantCreate(TenantBase):
    """Tenant creation model."""
    pass


class TenantUpdate(TenantBase):
    """Tenant update model."""
    pass


class TenantResponse(TenantBase):
    """Tenant response model."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    max_users: int
    max_storage: int
    used_storage: int

    class Config:
        """Pydantic config."""
        from_attributes = True


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    first_name: constr(min_length=1, max_length=50)
    last_name: constr(min_length=1, max_length=50)
    phone: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"


class UserCreate(UserBase):
    """User creation model."""
    password: constr(min_length=8)
    tenant_id: UUID


class UserUpdate(UserBase):
    """User update model."""
    pass


class UserResponse(UserBase):
    """User response model."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    roles: List[str]

    class Config:
        """Pydantic config."""
        from_attributes = True


class InventoryItemBase(BaseModel):
    """Base inventory item model."""
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    sku: constr(min_length=1, max_length=50)
    category: str
    manufacturer: str
    model: Optional[str] = None
    serial_number: Optional[str] = None
    quantity: int = Field(ge=0)
    unit_price: float = Field(ge=0)
    reorder_point: int = Field(ge=0)
    location: Optional[str] = None
    status: str = "active"


class InventoryItemCreate(InventoryItemBase):
    """Inventory item creation model."""
    tenant_id: UUID


class InventoryItemUpdate(InventoryItemBase):
    """Inventory item update model."""
    pass


class InventoryItemResponse(InventoryItemBase):
    """Inventory item response model."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    tenant_id: UUID
    last_modified_by: UUID

    class Config:
        """Pydantic config."""
        from_attributes = True


class OrderBase(BaseModel):
    """Base order model."""
    customer_id: UUID
    delivery_address: str
    billing_address: str
    status: str = "pending"
    priority: str = "normal"
    notes: Optional[str] = None


class OrderItemBase(BaseModel):
    """Base order item model."""
    inventory_item_id: UUID
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    discount: float = Field(ge=0, le=100)
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation model."""
    tenant_id: UUID
    items: List[OrderItemBase]


class OrderUpdate(OrderBase):
    """Order update model."""
    items: Optional[List[OrderItemBase]] = None


class OrderItemResponse(OrderItemBase):
    """Order item response model."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    subtotal: float
    total: float

    class Config:
        """Pydantic config."""
        from_attributes = True


class OrderResponse(OrderBase):
    """Order response model."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    tenant_id: UUID
    created_by: UUID
    items: List[OrderItemResponse]
    subtotal: float
    tax: float
    total: float
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True
