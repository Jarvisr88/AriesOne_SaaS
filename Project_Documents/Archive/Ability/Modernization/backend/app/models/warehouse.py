from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class Warehouse(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    code = fields.CharField(max_length=20, unique=True)
    address = fields.JSONField()
    dimensions = fields.JSONField()  # length, width, height
    zones = fields.JSONField()  # zone configurations
    dock_doors = fields.JSONField()  # door configurations
    status = fields.CharField(max_length=20)  # active, inactive, maintenance
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "warehouses"

class BinLocation(models.Model):
    id = fields.UUIDField(pk=True)
    warehouse = fields.ForeignKeyField('models.Warehouse', related_name='bin_locations')
    zone = fields.ForeignKeyField('models.StorageZone', related_name='bin_locations')
    bin_code = fields.CharField(max_length=20)
    coordinates = fields.JSONField()  # x, y, z coordinates
    dimensions = fields.JSONField()  # length, width, height
    capacity = fields.JSONField()  # weight and volume capacity
    current_utilization = fields.JSONField()  # current weight and volume
    status = fields.CharField(max_length=20)  # empty, partial, full, reserved
    last_counted = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "bin_locations"
        unique_together = ("warehouse", "bin_code")

class PickPath(models.Model):
    id = fields.UUIDField(pk=True)
    warehouse = fields.ForeignKeyField('models.Warehouse', related_name='pick_paths')
    order = fields.ForeignKeyField('models.Order', related_name='pick_paths')
    picker = fields.CharField(max_length=100)
    status = fields.CharField(max_length=20)  # pending, in_progress, completed
    start_time = fields.DatetimeField(null=True)
    end_time = fields.DatetimeField(null=True)
    sequence = fields.JSONField()  # ordered list of bin locations
    metrics = fields.JSONField(null=True)  # distance, time, efficiency
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "pick_paths"

class StorageZone(models.Model):
    id = fields.UUIDField(pk=True)
    warehouse = fields.ForeignKeyField('models.Warehouse', related_name='storage_zones')
    name = fields.CharField(max_length=100)
    zone_type = fields.CharField(max_length=50)  # standard, cold, hazmat, high_value, bulk
    dimensions = fields.JSONField()  # length, width, height
    temperature_range = fields.JSONField(null=True)  # min, max temperature
    special_requirements = fields.JSONField(null=True)  # special handling requirements
    status = fields.CharField(max_length=20)  # active, inactive, maintenance
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "storage_zones"

class ReturnItem(models.Model):
    id = fields.UUIDField(pk=True)
    warehouse = fields.ForeignKeyField('models.Warehouse', related_name='returns')
    order = fields.ForeignKeyField('models.Order', related_name='returned_items')
    item = fields.ForeignKeyField('models.InventoryItem', related_name='returns')
    quantity = fields.IntField()
    condition = fields.CharField(max_length=50)  # new, like_new, damaged, unsellable
    reason_code = fields.CharField(max_length=50)
    inspection_notes = fields.TextField(null=True)
    disposition = fields.CharField(max_length=50)  # restock, repair, dispose
    processed_by = fields.CharField(max_length=100)
    processed_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "return_items"

class QualityCheck(models.Model):
    id = fields.UUIDField(pk=True)
    warehouse = fields.ForeignKeyField('models.Warehouse', related_name='quality_checks')
    item = fields.ForeignKeyField('models.InventoryItem', related_name='quality_checks')
    batch_number = fields.CharField(max_length=50, null=True)
    check_type = fields.CharField(max_length=50)  # receiving, periodic, complaint
    inspector = fields.CharField(max_length=100)
    status = fields.CharField(max_length=20)  # pending, in_progress, completed, failed
    results = fields.JSONField(null=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "quality_checks"

class CycleCount(models.Model):
    id = fields.UUIDField(pk=True)
    warehouse = fields.ForeignKeyField('models.Warehouse', related_name='cycle_counts')
    zone = fields.ForeignKeyField('models.StorageZone', related_name='cycle_counts', null=True)
    item = fields.ForeignKeyField('models.InventoryItem', related_name='cycle_counts')
    bin_location = fields.ForeignKeyField('models.BinLocation', related_name='cycle_counts')
    counter = fields.CharField(max_length=100, null=True)
    scheduled_date = fields.DatetimeField()
    count_date = fields.DatetimeField(null=True)
    system_quantity = fields.IntField()
    counted_quantity = fields.IntField(null=True)
    variance = fields.IntField(null=True)
    status = fields.CharField(max_length=20)  # scheduled, in_progress, completed
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "cycle_counts"

class InventoryAge(models.Model):
    id = fields.UUIDField(pk=True)
    warehouse = fields.ForeignKeyField('models.Warehouse', related_name='inventory_age')
    item = fields.ForeignKeyField('models.InventoryItem', related_name='age_tracking')
    bin_location = fields.ForeignKeyField('models.BinLocation', related_name='inventory_age')
    batch_number = fields.CharField(max_length=50, null=True)
    quantity = fields.IntField()
    receipt_date = fields.DatetimeField()
    expiry_date = fields.DatetimeField(null=True)
    last_movement = fields.DatetimeField()
    status = fields.CharField(max_length=20)  # active, quarantine, expired
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "inventory_age"

# Pydantic models for API
class WarehouseCreate(BaseModel):
    name: str
    code: str
    address: Dict
    dimensions: Dict
    zones: Dict
    dock_doors: Dict

class BinLocationCreate(BaseModel):
    warehouse_id: str
    zone_id: str
    bin_code: str
    coordinates: Dict
    dimensions: Dict
    capacity: Dict

class PickPathCreate(BaseModel):
    warehouse_id: str
    order_id: str
    picker: str
    sequence: List[Dict]

class ReturnItemCreate(BaseModel):
    warehouse_id: str
    order_id: str
    item_id: str
    quantity: int
    condition: str
    reason_code: str
    inspection_notes: Optional[str]

class QualityCheckCreate(BaseModel):
    warehouse_id: str
    item_id: str
    batch_number: Optional[str]
    check_type: str
    inspector: str
    notes: Optional[str]

class CycleCountCreate(BaseModel):
    warehouse_id: str
    zone_id: Optional[str]
    item_id: str
    bin_location_id: str
    scheduled_date: datetime
    system_quantity: int
    notes: Optional[str]
