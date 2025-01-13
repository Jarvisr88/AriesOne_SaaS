"""
Pydantic schemas for inventory domain.
Provides request and response validation for inventory-related operations.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, constr, confloat, conint, Field

from ..models.inventory import ItemType, ItemStatus, PricingModel

# Base schemas
class InventoryItemBase(BaseModel):
    """Base schema for inventory items."""
    item_number: constr(min_length=1, max_length=50)
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    item_type: ItemType
    status: ItemStatus = ItemStatus.ACTIVE
    
    # Classification
    category: Optional[str] = None
    subcategory: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    
    # Pricing
    pricing_model: PricingModel
    sale_price: Optional[confloat(ge=0)] = None
    rental_price: Optional[confloat(ge=0)] = None
    cost: Optional[confloat(ge=0)] = None
    
    # Tracking
    requires_serial: bool = False
    requires_lot: bool = False
    is_billable: bool = True

class InventoryItemCreate(InventoryItemBase):
    """Schema for creating inventory items."""
    hcpcs_code: Optional[str] = None
    upc_code: Optional[str] = None
    warranty_months: Optional[conint(ge=0)] = None
    reorder_point: Optional[conint(ge=0)] = None
    reorder_quantity: Optional[conint(ge=0)] = None
    minimum_stock: Optional[conint(ge=0)] = None
    maximum_stock: Optional[conint(ge=0)] = None

class InventoryItemUpdate(BaseModel):
    """Schema for updating inventory items."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    status: Optional[ItemStatus] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    pricing_model: Optional[PricingModel] = None
    sale_price: Optional[confloat(ge=0)] = None
    rental_price: Optional[confloat(ge=0)] = None
    cost: Optional[confloat(ge=0)] = None
    requires_serial: Optional[bool] = None
    requires_lot: Optional[bool] = None
    is_billable: Optional[bool] = None
    hcpcs_code: Optional[str] = None
    upc_code: Optional[str] = None
    warranty_months: Optional[conint(ge=0)] = None
    reorder_point: Optional[conint(ge=0)] = None
    reorder_quantity: Optional[conint(ge=0)] = None
    minimum_stock: Optional[conint(ge=0)] = None
    maximum_stock: Optional[conint(ge=0)] = None

class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item responses."""
    id: int
    hcpcs_code: Optional[str] = None
    upc_code: Optional[str] = None
    warranty_months: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    minimum_stock: Optional[int] = None
    maximum_stock: Optional[int] = None
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Kit schemas
class KitComponentBase(BaseModel):
    """Base schema for kit components."""
    component_id: int
    quantity: conint(gt=0) = 1
    is_required: bool = True
    sequence: Optional[int] = None
    notes: Optional[str] = None

class KitComponentCreate(KitComponentBase):
    """Schema for creating kit components."""
    pass

class KitComponentUpdate(BaseModel):
    """Schema for updating kit components."""
    quantity: Optional[conint(gt=0)] = None
    is_required: Optional[bool] = None
    sequence: Optional[int] = None
    notes: Optional[str] = None

class KitComponentResponse(KitComponentBase):
    """Schema for kit component responses."""
    id: int
    kit_id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

class KitBase(InventoryItemBase):
    """Base schema for kits."""
    assembly_instructions: Optional[str] = None
    is_customizable: bool = False

class KitCreate(KitBase):
    """Schema for creating kits."""
    components: List[KitComponentCreate]

class KitUpdate(BaseModel):
    """Schema for updating kits."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    status: Optional[ItemStatus] = None
    assembly_instructions: Optional[str] = None
    is_customizable: Optional[bool] = None
    components: Optional[List[KitComponentCreate]] = None

class KitResponse(KitBase):
    """Schema for kit responses."""
    id: int
    components: List[KitComponentResponse]
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Serial number schemas
class SerialNumberBase(BaseModel):
    """Base schema for serial numbers."""
    item_id: int
    serial_number: constr(min_length=1, max_length=50)
    manufacturer_serial: Optional[str] = None
    manufacture_date: Optional[date] = None
    purchase_date: Optional[date] = None
    warranty_start: Optional[date] = None
    warranty_end: Optional[date] = None
    status: str = 'Available'
    condition: Optional[str] = None
    location_id: Optional[int] = None
    last_inspection_date: Optional[date] = None
    next_inspection_date: Optional[date] = None

class SerialNumberCreate(SerialNumberBase):
    """Schema for creating serial numbers."""
    pass

class SerialNumberUpdate(BaseModel):
    """Schema for updating serial numbers."""
    manufacturer_serial: Optional[str] = None
    manufacture_date: Optional[date] = None
    purchase_date: Optional[date] = None
    warranty_start: Optional[date] = None
    warranty_end: Optional[date] = None
    status: Optional[str] = None
    condition: Optional[str] = None
    location_id: Optional[int] = None
    last_inspection_date: Optional[date] = None
    next_inspection_date: Optional[date] = None

class SerialNumberResponse(SerialNumberBase):
    """Schema for serial number responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Maintenance record schemas
class MaintenanceRecordBase(BaseModel):
    """Base schema for maintenance records."""
    serial_number_id: int
    maintenance_type: str
    maintenance_date: date
    performed_by: Optional[str] = None
    cost: Optional[confloat(ge=0)] = None
    description: Optional[str] = None
    resolution: Optional[str] = None
    next_maintenance_date: Optional[date] = None

class MaintenanceRecordCreate(MaintenanceRecordBase):
    """Schema for creating maintenance records."""
    pass

class MaintenanceRecordUpdate(BaseModel):
    """Schema for updating maintenance records."""
    maintenance_type: Optional[str] = None
    maintenance_date: Optional[date] = None
    performed_by: Optional[str] = None
    cost: Optional[confloat(ge=0)] = None
    description: Optional[str] = None
    resolution: Optional[str] = None
    next_maintenance_date: Optional[date] = None

class MaintenanceRecordResponse(MaintenanceRecordBase):
    """Schema for maintenance record responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Warehouse schemas
class WarehouseBase(BaseModel):
    """Base schema for warehouses."""
    code: constr(min_length=1, max_length=20)
    name: constr(min_length=1, max_length=100)
    address1: constr(min_length=1, max_length=100)
    address2: Optional[str] = None
    city: constr(min_length=1, max_length=50)
    state: constr(min_length=2, max_length=2)
    zip_code: constr(min_length=5, max_length=10)
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    """Schema for creating warehouses."""
    pass

class WarehouseUpdate(BaseModel):
    """Schema for updating warehouses."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    address1: Optional[constr(min_length=1, max_length=100)] = None
    address2: Optional[str] = None
    city: Optional[constr(min_length=1, max_length=50)] = None
    state: Optional[constr(min_length=2, max_length=2)] = None
    zip_code: Optional[constr(min_length=5, max_length=10)] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase):
    """Schema for warehouse responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Stock level schemas
class StockLevelBase(BaseModel):
    """Base schema for stock levels."""
    item_id: int
    warehouse_id: int
    quantity_on_hand: conint(ge=0) = 0
    quantity_allocated: conint(ge=0) = 0
    quantity_available: conint(ge=0) = 0
    quantity_on_order: conint(ge=0) = 0
    bin_location: Optional[str] = None

class StockLevelCreate(StockLevelBase):
    """Schema for creating stock levels."""
    pass

class StockLevelUpdate(BaseModel):
    """Schema for updating stock levels."""
    quantity_on_hand: Optional[conint(ge=0)] = None
    quantity_allocated: Optional[conint(ge=0)] = None
    quantity_available: Optional[conint(ge=0)] = None
    quantity_on_order: Optional[conint(ge=0)] = None
    bin_location: Optional[str] = None

class StockLevelResponse(StockLevelBase):
    """Schema for stock level responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True
