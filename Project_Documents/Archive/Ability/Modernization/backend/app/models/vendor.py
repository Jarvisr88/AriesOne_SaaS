from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class Vendor(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    code = fields.CharField(max_length=20, unique=True)
    status = fields.CharField(max_length=20)  # active, inactive, suspended, blacklisted
    contact_info = fields.JSONField()
    payment_terms = fields.JSONField()
    tax_info = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "vendors"

class Contract(models.Model):
    id = fields.UUIDField(pk=True)
    vendor = fields.ForeignKeyField('models.Vendor', related_name='contracts')
    contract_number = fields.CharField(max_length=50, unique=True)
    type = fields.CharField(max_length=50)  # standard, preferred, exclusive
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    terms = fields.JSONField()
    status = fields.CharField(max_length=20)  # draft, negotiating, active, expired, terminated
    termination_date = fields.DatetimeField(null=True)
    termination_reason = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "vendor_contracts"

class PriceHistory(models.Model):
    id = fields.UUIDField(pk=True)
    vendor = fields.ForeignKeyField('models.Vendor', related_name='price_history')
    item = fields.ForeignKeyField('models.InventoryItem', related_name='vendor_prices')
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    previous_price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    currency = fields.CharField(max_length=3)
    effective_date = fields.DatetimeField()
    expiry_date = fields.DatetimeField(null=True)
    volume_threshold = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "vendor_price_history"

class QualityReport(models.Model):
    id = fields.UUIDField(pk=True)
    vendor = fields.ForeignKeyField('models.Vendor', related_name='quality_reports')
    inspection_date = fields.DatetimeField()
    inspector = fields.CharField(max_length=100)
    inspection_type = fields.CharField(max_length=50)
    inspection_quantity = fields.IntField()
    defect_count = fields.IntField()
    return_count = fields.IntField()
    severity = fields.CharField(max_length=20)  # minor, major, critical
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "vendor_quality_reports"

class DeliveryPerformance(models.Model):
    id = fields.UUIDField(pk=True)
    vendor = fields.ForeignKeyField('models.Vendor', related_name='deliveries')
    order = fields.ForeignKeyField('models.PurchaseOrder', related_name='delivery_performance')
    expected_date = fields.DatetimeField()
    actual_date = fields.DatetimeField()
    quantity_ordered = fields.IntField()
    quantity_received = fields.IntField()
    on_time = fields.BooleanField()
    delay_days = fields.IntField(default=0)
    reason_code = fields.CharField(max_length=50, null=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "vendor_delivery_performance"

class Payment(models.Model):
    id = fields.UUIDField(pk=True)
    vendor = fields.ForeignKeyField('models.Vendor', related_name='payments')
    invoice = fields.ForeignKeyField('models.Invoice', related_name='vendor_payments')
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    currency = fields.CharField(max_length=3)
    payment_method = fields.CharField(max_length=50)
    status = fields.CharField(max_length=20)  # pending, processing, completed, failed
    due_date = fields.DatetimeField()
    payment_date = fields.DatetimeField(null=True)
    processing_time = fields.IntField(null=True)
    expected_processing_time = fields.IntField()
    transaction_reference = fields.CharField(max_length=100, null=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "vendor_payments"

class VendorRating(models.Model):
    id = fields.UUIDField(pk=True)
    vendor = fields.ForeignKeyField('models.Vendor', related_name='ratings')
    score = fields.FloatField()
    rating = fields.CharField(max_length=1)  # A, B, C, D, F
    period_start = fields.DatetimeField()
    period_end = fields.DatetimeField()
    metrics = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)
    last_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "vendor_ratings"

class Communication(models.Model):
    id = fields.UUIDField(pk=True)
    vendor = fields.ForeignKeyField('models.Vendor', related_name='communications')
    type = fields.CharField(max_length=50)  # email, phone, meeting, portal
    direction = fields.CharField(max_length=20)  # incoming, outgoing
    subject = fields.CharField(max_length=200)
    content = fields.TextField()
    priority = fields.CharField(max_length=20)  # low, medium, high, urgent
    status = fields.CharField(max_length=20)  # new, read, responded, closed
    reference_type = fields.CharField(max_length=50, null=True)  # order, contract, quality, delivery
    reference_id = fields.UUIDField(null=True)
    attachments = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "vendor_communications"

# Pydantic models for API
class VendorCreate(BaseModel):
    name: str
    code: str
    contact_info: Dict
    payment_terms: Dict
    tax_info: Dict

class ContractCreate(BaseModel):
    vendor_id: str
    contract_number: str
    type: str
    start_date: datetime
    end_date: datetime
    terms: Dict

class QualityReportCreate(BaseModel):
    vendor_id: str
    inspection_date: datetime
    inspector: str
    inspection_type: str
    inspection_quantity: int
    defect_count: int
    return_count: int
    severity: str
    notes: Optional[str]

class DeliveryPerformanceCreate(BaseModel):
    vendor_id: str
    order_id: str
    expected_date: datetime
    actual_date: datetime
    quantity_ordered: int
    quantity_received: int
    reason_code: Optional[str]
    notes: Optional[str]

class PaymentCreate(BaseModel):
    vendor_id: str
    invoice_id: str
    amount: float
    currency: str
    payment_method: str
    due_date: datetime
    expected_processing_time: int
    notes: Optional[str]

class CommunicationCreate(BaseModel):
    vendor_id: str
    type: str
    direction: str
    subject: str
    content: str
    priority: str
    reference_type: Optional[str]
    reference_id: Optional[str]
    attachments: Optional[Dict]
