from datetime import datetime
from typing import Optional
from uuid import UUID
from tortoise import fields, models
from pydantic import BaseModel

class InventoryItem(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    sku = fields.CharField(max_length=50, unique=True)
    description = fields.TextField()
    unit_price = fields.DecimalField(max_digits=10, decimal_places=2)
    current_stock = fields.IntField()
    reorder_point = fields.IntField()
    minimum_stock = fields.IntField()
    maximum_stock = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "inventory_items"

class OrderHistory(models.Model):
    id = fields.UUIDField(pk=True)
    item = fields.ForeignKeyField('models.InventoryItem', related_name='order_history')
    quantity = fields.IntField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    promotion_active = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "order_history"

class SupplierPerformance(models.Model):
    id = fields.UUIDField(pk=True)
    item = fields.ForeignKeyField('models.InventoryItem', related_name='supplier_performance')
    supplier = fields.ForeignKeyField('models.Supplier', related_name='performance')
    average_lead_time = fields.FloatField()
    lead_time_std = fields.FloatField()
    average_daily_demand = fields.FloatField()
    fill_rate = fields.FloatField()
    quality_rating = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "supplier_performance"

class PurchaseOrder(models.Model):
    id = fields.UUIDField(pk=True)
    item = fields.ForeignKeyField('models.InventoryItem', related_name='purchase_orders')
    supplier = fields.ForeignKeyField('models.Supplier', related_name='purchase_orders')
    quantity = fields.IntField()
    unit_price = fields.DecimalField(max_digits=10, decimal_places=2)
    expected_delivery = fields.DatetimeField()
    actual_delivery = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=20)  # pending, approved, shipped, delivered, cancelled
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    forecast_demand = fields.FloatField()
    safety_stock = fields.FloatField()
    optimal_quantity = fields.FloatField()

    class Meta:
        table = "purchase_orders"

class SafetyStock(models.Model):
    id = fields.UUIDField(pk=True)
    item = fields.ForeignKeyField('models.InventoryItem', related_name='safety_stock')
    level = fields.FloatField()
    service_level = fields.FloatField()
    calculated_at = fields.DatetimeField()

    class Meta:
        table = "safety_stock"

# Pydantic models for API
class InventoryItemCreate(BaseModel):
    name: str
    sku: str
    description: str
    unit_price: float
    current_stock: int
    reorder_point: int
    minimum_stock: int
    maximum_stock: int

class InventoryItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    unit_price: Optional[float]
    current_stock: Optional[int]
    reorder_point: Optional[int]
    minimum_stock: Optional[int]
    maximum_stock: Optional[int]

class PurchaseOrderCreate(BaseModel):
    item_id: UUID
    supplier_id: UUID
    quantity: int
    unit_price: float
    expected_delivery: datetime

class PurchaseOrderUpdate(BaseModel):
    quantity: Optional[int]
    unit_price: Optional[float]
    expected_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    status: Optional[str]

class SafetyStockCreate(BaseModel):
    item_id: UUID
    level: float
    service_level: float

class OrderHistoryCreate(BaseModel):
    item_id: UUID
    quantity: int
    price: float
    promotion_active: bool = False
