"""
Service layer for inventory domain.
Implements business logic for inventory management operations.
"""
from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
from fastapi import HTTPException

from ..models.inventory import (
    InventoryItem, Kit, KitComponent, SerialNumber,
    MaintenanceRecord, Warehouse, StockLevel
)
from ..schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate,
    KitCreate, KitUpdate,
    KitComponentCreate, KitComponentUpdate,
    SerialNumberCreate, SerialNumberUpdate,
    MaintenanceRecordCreate, MaintenanceRecordUpdate,
    WarehouseCreate, WarehouseUpdate,
    StockLevelCreate, StockLevelUpdate
)

class InventoryService:
    """Service for inventory operations."""

    @staticmethod
    async def create_item(db: Session, item: InventoryItemCreate, user_id: int) -> InventoryItem:
        """Create a new inventory item."""
        db_item = InventoryItem(
            **item.model_dump(),
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_item)
        await db.flush()
        return db_item

    @staticmethod
    async def get_item(db: Session, item_id: int) -> InventoryItem:
        """Get an inventory item by ID."""
        item = await db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    @staticmethod
    async def get_items(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> Tuple[List[InventoryItem], int]:
        """Get inventory items with filtering and pagination."""
        query = db.query(InventoryItem)
        
        if filters:
            if filters.get("item_type"):
                query = query.filter(InventoryItem.item_type == filters["item_type"])
            if filters.get("status"):
                query = query.filter(InventoryItem.status == filters["status"])
            if filters.get("category"):
                query = query.filter(InventoryItem.category == filters["category"])
            if filters.get("manufacturer"):
                query = query.filter(InventoryItem.manufacturer == filters["manufacturer"])

        total = await query.count()
        items = await query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    async def update_item(
        db: Session,
        item_id: int,
        item_update: InventoryItemUpdate,
        user_id: int
    ) -> InventoryItem:
        """Update an inventory item."""
        db_item = await InventoryService.get_item(db, item_id)
        update_data = item_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db_item.last_update_user_id = user_id
        db_item.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_item

    @staticmethod
    async def delete_item(db: Session, item_id: int) -> None:
        """Delete an inventory item."""
        db_item = await InventoryService.get_item(db, item_id)
        await db.delete(db_item)
        await db.flush()

class KitService:
    """Service for kit operations."""

    @staticmethod
    async def create_kit(db: Session, kit: KitCreate, user_id: int) -> Kit:
        """Create a new kit with components."""
        db_kit = Kit(
            **kit.model_dump(exclude={'components'}),
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_kit)
        await db.flush()

        for component in kit.components:
            db_component = KitComponent(
                kit_id=db_kit.id,
                **component.model_dump(),
                created_by_id=user_id,
                last_update_user_id=user_id
            )
            db.add(db_component)
        
        await db.flush()
        return db_kit

    @staticmethod
    async def get_kit(db: Session, kit_id: int) -> Kit:
        """Get a kit by ID."""
        kit = await db.query(Kit).filter(Kit.id == kit_id).first()
        if not kit:
            raise HTTPException(status_code=404, detail="Kit not found")
        return kit

    @staticmethod
    async def update_kit(
        db: Session,
        kit_id: int,
        kit_update: KitUpdate,
        user_id: int
    ) -> Kit:
        """Update a kit and its components."""
        db_kit = await KitService.get_kit(db, kit_id)
        update_data = kit_update.model_dump(exclude_unset=True, exclude={'components'})
        
        for field, value in update_data.items():
            setattr(db_kit, field, value)
        
        if kit_update.components:
            # Remove existing components
            await db.query(KitComponent).filter(KitComponent.kit_id == kit_id).delete()
            
            # Add new components
            for component in kit_update.components:
                db_component = KitComponent(
                    kit_id=kit_id,
                    **component.model_dump(),
                    created_by_id=user_id,
                    last_update_user_id=user_id
                )
                db.add(db_component)
        
        db_kit.last_update_user_id = user_id
        db_kit.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_kit

class SerialNumberService:
    """Service for serial number operations."""

    @staticmethod
    async def create_serial_number(
        db: Session,
        serial: SerialNumberCreate,
        user_id: int
    ) -> SerialNumber:
        """Create a new serial number."""
        db_serial = SerialNumber(
            **serial.model_dump(),
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_serial)
        await db.flush()
        return db_serial

    @staticmethod
    async def get_serial_number(db: Session, serial_id: int) -> SerialNumber:
        """Get a serial number by ID."""
        serial = await db.query(SerialNumber).filter(SerialNumber.id == serial_id).first()
        if not serial:
            raise HTTPException(status_code=404, detail="Serial number not found")
        return serial

    @staticmethod
    async def get_serial_numbers(
        db: Session,
        item_id: Optional[int] = None,
        status: Optional[str] = None,
        location_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[SerialNumber], int]:
        """Get serial numbers with filtering and pagination."""
        query = db.query(SerialNumber)
        
        if item_id:
            query = query.filter(SerialNumber.item_id == item_id)
        if status:
            query = query.filter(SerialNumber.status == status)
        if location_id:
            query = query.filter(SerialNumber.location_id == location_id)

        total = await query.count()
        serials = await query.offset(skip).limit(limit).all()
        return serials, total

    @staticmethod
    async def update_serial_number(
        db: Session,
        serial_id: int,
        serial_update: SerialNumberUpdate,
        user_id: int
    ) -> SerialNumber:
        """Update a serial number."""
        db_serial = await SerialNumberService.get_serial_number(db, serial_id)
        update_data = serial_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_serial, field, value)
        
        db_serial.last_update_user_id = user_id
        db_serial.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_serial

class MaintenanceService:
    """Service for maintenance record operations."""

    @staticmethod
    async def create_maintenance_record(
        db: Session,
        record: MaintenanceRecordCreate,
        user_id: int
    ) -> MaintenanceRecord:
        """Create a new maintenance record."""
        db_record = MaintenanceRecord(
            **record.model_dump(),
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_record)
        await db.flush()
        return db_record

    @staticmethod
    async def get_maintenance_records(
        db: Session,
        serial_number_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[MaintenanceRecord], int]:
        """Get maintenance records for a serial number."""
        query = db.query(MaintenanceRecord).filter(
            MaintenanceRecord.serial_number_id == serial_number_id
        )
        total = await query.count()
        records = await query.offset(skip).limit(limit).all()
        return records, total

class WarehouseService:
    """Service for warehouse operations."""

    @staticmethod
    async def create_warehouse(
        db: Session,
        warehouse: WarehouseCreate,
        user_id: int
    ) -> Warehouse:
        """Create a new warehouse."""
        db_warehouse = Warehouse(
            **warehouse.model_dump(),
            created_by_id=user_id,
            last_update_user_id=user_id
        )
        db.add(db_warehouse)
        await db.flush()
        return db_warehouse

    @staticmethod
    async def get_warehouse(db: Session, warehouse_id: int) -> Warehouse:
        """Get a warehouse by ID."""
        warehouse = await db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        return warehouse

    @staticmethod
    async def update_warehouse(
        db: Session,
        warehouse_id: int,
        warehouse_update: WarehouseUpdate,
        user_id: int
    ) -> Warehouse:
        """Update a warehouse."""
        db_warehouse = await WarehouseService.get_warehouse(db, warehouse_id)
        update_data = warehouse_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_warehouse, field, value)
        
        db_warehouse.last_update_user_id = user_id
        db_warehouse.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_warehouse

class StockLevelService:
    """Service for stock level operations."""

    @staticmethod
    async def get_stock_level(
        db: Session,
        item_id: int,
        warehouse_id: int
    ) -> StockLevel:
        """Get stock level for an item in a warehouse."""
        stock = await db.query(StockLevel).filter(
            and_(
                StockLevel.item_id == item_id,
                StockLevel.warehouse_id == warehouse_id
            )
        ).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock level not found")
        return stock

    @staticmethod
    async def update_stock_level(
        db: Session,
        item_id: int,
        warehouse_id: int,
        update: StockLevelUpdate,
        user_id: int
    ) -> StockLevel:
        """Update stock level for an item in a warehouse."""
        db_stock = await StockLevelService.get_stock_level(db, item_id, warehouse_id)
        update_data = update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_stock, field, value)
        
        db_stock.last_update_user_id = user_id
        db_stock.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_stock

    @staticmethod
    async def adjust_stock(
        db: Session,
        item_id: int,
        warehouse_id: int,
        adjustment: int,
        user_id: int
    ) -> StockLevel:
        """Adjust stock level by a given amount."""
        db_stock = await StockLevelService.get_stock_level(db, item_id, warehouse_id)
        
        # Update quantities
        db_stock.quantity_on_hand += adjustment
        db_stock.quantity_available = (
            db_stock.quantity_on_hand - db_stock.quantity_allocated
        )
        
        db_stock.last_update_user_id = user_id
        db_stock.last_update_datetime = datetime.utcnow()
        await db.flush()
        return db_stock
