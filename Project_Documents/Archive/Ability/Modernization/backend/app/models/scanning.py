from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel
from uuid import UUID

class ScannedItem(models.Model):
    id = fields.UUIDField(pk=True)
    scan_type = fields.CharField(max_length=20)  # barcode, rfid
    scan_data = fields.JSONField()
    scanned_at = fields.DatetimeField()
    location = fields.JSONField(null=True)
    device_id = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "scanned_items"

class RFIDTag(models.Model):
    id = fields.UUIDField(pk=True)
    item = fields.ForeignKeyField('models.InventoryItem', related_name='rfid_tags')
    epc = fields.CharField(max_length=24, unique=True)
    metadata = fields.JSONField(null=True)
    status = fields.CharField(max_length=20)  # active, inactive
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "rfid_tags"

class SerialNumber(models.Model):
    id = fields.UUIDField(pk=True)
    item = fields.ForeignKeyField('models.InventoryItem', related_name='serial_numbers')
    serial_number = fields.CharField(max_length=100, unique=True)
    expiration_date = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=20)  # active, inactive, expired
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "serial_numbers"

class BatchScan(models.Model):
    id = fields.UUIDField(pk=True)
    started_at = fields.DatetimeField()
    completed_at = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=20)  # processing, completed, failed
    total_scans = fields.IntField(default=0)
    error_count = fields.IntField(default=0)
    metadata = fields.JSONField(null=True)

    class Meta:
        table = "batch_scans"

# Pydantic models for API
class ScannedItemCreate(BaseModel):
    scan_type: str
    scan_data: Dict
    scanned_at: datetime
    location: Optional[Dict]
    device_id: Optional[str]

class RFIDTagCreate(BaseModel):
    item_id: UUID
    epc: str
    metadata: Optional[Dict]

class RFIDTagUpdate(BaseModel):
    metadata: Optional[Dict]
    status: Optional[str]

class SerialNumberCreate(BaseModel):
    item_id: UUID
    serial_number: str
    expiration_date: Optional[datetime]

class SerialNumberUpdate(BaseModel):
    expiration_date: Optional[datetime]
    status: Optional[str]

class BatchScanCreate(BaseModel):
    metadata: Optional[Dict]

class BatchScanUpdate(BaseModel):
    status: str
    total_scans: int
    error_count: int
    metadata: Optional[Dict]

class OfflineScanData(BaseModel):
    type: str  # barcode, rfid
    image: Optional[str]  # base64 encoded image for barcode
    epc: Optional[str]  # for RFID
    timestamp: str
    location: Optional[Dict]
    device_id: Optional[str]

class OfflineScanBatch(BaseModel):
    scans: List[OfflineScanData]
