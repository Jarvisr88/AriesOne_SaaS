"""
API routes for inventory domain.
Implements RESTful endpoints for inventory management.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..dependencies import get_db, get_current_user
from ..services.inventory import (
    InventoryService, KitService, SerialNumberService,
    MaintenanceService, WarehouseService, StockLevelService
)
from ..schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    KitCreate, KitUpdate, KitResponse,
    SerialNumberCreate, SerialNumberUpdate, SerialNumberResponse,
    MaintenanceRecordCreate, MaintenanceRecordUpdate, MaintenanceRecordResponse,
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    StockLevelCreate, StockLevelUpdate, StockLevelResponse
)
from ..models.inventory import ItemType, ItemStatus

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

# Inventory Item Routes
@router.post("/items/", response_model=InventoryItemResponse)
async def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new inventory item."""
    return await InventoryService.create_item(db, item, current_user["id"])

@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get an inventory item by ID."""
    return await InventoryService.get_item(db, item_id)

@router.get("/items/", response_model=List[InventoryItemResponse])
async def list_inventory_items(
    skip: int = 0,
    limit: int = 100,
    item_type: Optional[ItemType] = None,
    status: Optional[ItemStatus] = None,
    category: Optional[str] = None,
    manufacturer: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List inventory items with filtering and pagination."""
    filters = {
        "item_type": item_type,
        "status": status,
        "category": category,
        "manufacturer": manufacturer
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    items, _ = await InventoryService.get_items(db, skip, limit, filters)
    return items

@router.put("/items/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    item: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an inventory item."""
    return await InventoryService.update_item(db, item_id, item, current_user["id"])

@router.delete("/items/{item_id}")
async def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an inventory item."""
    await InventoryService.delete_item(db, item_id)
    return {"message": "Item deleted successfully"}

# Kit Routes
@router.post("/kits/", response_model=KitResponse)
async def create_kit(
    kit: KitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new kit with components."""
    return await KitService.create_kit(db, kit, current_user["id"])

@router.get("/kits/{kit_id}", response_model=KitResponse)
async def get_kit(
    kit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a kit by ID."""
    return await KitService.get_kit(db, kit_id)

@router.put("/kits/{kit_id}", response_model=KitResponse)
async def update_kit(
    kit_id: int,
    kit: KitUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a kit and its components."""
    return await KitService.update_kit(db, kit_id, kit, current_user["id"])

# Serial Number Routes
@router.post("/serials/", response_model=SerialNumberResponse)
async def create_serial_number(
    serial: SerialNumberCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new serial number."""
    return await SerialNumberService.create_serial_number(db, serial, current_user["id"])

@router.get("/serials/{serial_id}", response_model=SerialNumberResponse)
async def get_serial_number(
    serial_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a serial number by ID."""
    return await SerialNumberService.get_serial_number(db, serial_id)

@router.get("/serials/", response_model=List[SerialNumberResponse])
async def list_serial_numbers(
    item_id: Optional[int] = None,
    status: Optional[str] = None,
    location_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List serial numbers with filtering and pagination."""
    serials, _ = await SerialNumberService.get_serial_numbers(
        db, item_id, status, location_id, skip, limit
    )
    return serials

@router.put("/serials/{serial_id}", response_model=SerialNumberResponse)
async def update_serial_number(
    serial_id: int,
    serial: SerialNumberUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a serial number."""
    return await SerialNumberService.update_serial_number(
        db, serial_id, serial, current_user["id"]
    )

# Maintenance Record Routes
@router.post("/maintenance/", response_model=MaintenanceRecordResponse)
async def create_maintenance_record(
    record: MaintenanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new maintenance record."""
    return await MaintenanceService.create_maintenance_record(
        db, record, current_user["id"]
    )

@router.get("/maintenance/", response_model=List[MaintenanceRecordResponse])
async def list_maintenance_records(
    serial_number_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List maintenance records for a serial number."""
    records, _ = await MaintenanceService.get_maintenance_records(
        db, serial_number_id, skip, limit
    )
    return records

# Warehouse Routes
@router.post("/warehouses/", response_model=WarehouseResponse)
async def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new warehouse."""
    return await WarehouseService.create_warehouse(db, warehouse, current_user["id"])

@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a warehouse by ID."""
    return await WarehouseService.get_warehouse(db, warehouse_id)

@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: int,
    warehouse: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a warehouse."""
    return await WarehouseService.update_warehouse(
        db, warehouse_id, warehouse, current_user["id"]
    )

# Stock Level Routes
@router.get("/stock/{item_id}/{warehouse_id}", response_model=StockLevelResponse)
async def get_stock_level(
    item_id: int,
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get stock level for an item in a warehouse."""
    return await StockLevelService.get_stock_level(db, item_id, warehouse_id)

@router.put("/stock/{item_id}/{warehouse_id}", response_model=StockLevelResponse)
async def update_stock_level(
    item_id: int,
    warehouse_id: int,
    stock: StockLevelUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update stock level for an item in a warehouse."""
    return await StockLevelService.update_stock_level(
        db, item_id, warehouse_id, stock, current_user["id"]
    )

@router.post("/stock/{item_id}/{warehouse_id}/adjust", response_model=StockLevelResponse)
async def adjust_stock_level(
    item_id: int,
    warehouse_id: int,
    adjustment: int = Query(..., description="Amount to adjust (positive or negative)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Adjust stock level by a given amount."""
    return await StockLevelService.adjust_stock(
        db, item_id, warehouse_id, adjustment, current_user["id"]
    )
