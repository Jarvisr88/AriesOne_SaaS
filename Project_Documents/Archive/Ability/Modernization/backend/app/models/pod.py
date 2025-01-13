from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class ProofOfDelivery(models.Model):
    id = fields.UUIDField(pk=True)
    delivery_id = fields.CharField(max_length=100)
    signature_id = fields.UUIDField(null=True)
    photo_ids = fields.JSONField()  # List of photo IDs
    location = fields.JSONField()  # lat, lng, accuracy
    timestamp = fields.DatetimeField()
    status = fields.CharField(max_length=20)  # completed, pending, failed
    verification_hash = fields.CharField(max_length=64)
    offline_captured = fields.BooleanField(default=False)
    sync_status = fields.CharField(max_length=20, null=True)  # synced, pending
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "proof_of_delivery"
        indexes = (
            ("delivery_id", "status"),
        )

class Signature(models.Model):
    id = fields.UUIDField(pk=True)
    delivery_id = fields.CharField(max_length=100)
    signer_name = fields.CharField(max_length=100)
    signature_path = fields.CharField(max_length=255)
    timestamp = fields.DatetimeField()
    verification_status = fields.CharField(max_length=20, default='pending')
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "signatures"

class DeliveryPhoto(models.Model):
    id = fields.UUIDField(pk=True)
    delivery_id = fields.CharField(max_length=100)
    photo_path = fields.CharField(max_length=255)
    photo_type = fields.CharField(max_length=50)  # package, location, damage
    timestamp = fields.DatetimeField()
    location = fields.JSONField(null=True)  # lat, lng where photo was taken
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "delivery_photos"

class CustomerFeedback(models.Model):
    id = fields.UUIDField(pk=True)
    pod_id = fields.UUIDField()
    rating = fields.IntField()  # 1-5 rating
    comments = fields.TextField(null=True)
    categories = fields.JSONField(null=True)  # List of feedback categories
    timestamp = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "customer_feedback"

class DeliveryException(models.Model):
    id = fields.UUIDField(pk=True)
    delivery_id = fields.CharField(max_length=100)
    exception_type = fields.CharField(max_length=50)  # damaged, refused, inaccessible
    description = fields.TextField()
    photos = fields.JSONField(null=True)  # List of photo IDs
    location = fields.JSONField()
    timestamp = fields.DatetimeField()
    status = fields.CharField(max_length=20)  # pending, resolved
    resolution = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    resolved_at = fields.DatetimeField(null=True)

    class Meta:
        table = "delivery_exceptions"

class DigitalReceipt(models.Model):
    id = fields.UUIDField(pk=True)
    pod_id = fields.UUIDField()
    delivery_id = fields.CharField(max_length=100)
    receipt_number = fields.CharField(max_length=50, unique=True)
    receipt_path = fields.CharField(max_length=255, null=True)
    delivery_details = fields.JSONField()
    verification_code = fields.CharField(max_length=12)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "digital_receipts"

class PODMetrics(models.Model):
    id = fields.UUIDField(pk=True)
    date = fields.DateField()
    total_deliveries = fields.IntField()
    completed_pods = fields.IntField()
    exception_rate = fields.FloatField()
    average_rating = fields.FloatField()
    offline_captures = fields.IntField()
    sync_success_rate = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "pod_metrics"

# Pydantic models for API
class ProofOfDeliveryCreate(BaseModel):
    delivery_id: str
    signature: Optional[Dict]
    photos: Optional[List[str]]
    location: Dict
    timestamp: datetime

class SignatureCreate(BaseModel):
    delivery_id: str
    signer_name: str
    signature_data: Dict

class DeliveryPhotoCreate(BaseModel):
    delivery_id: str
    photo_type: str
    location: Optional[Dict]

class CustomerFeedbackCreate(BaseModel):
    pod_id: str
    rating: int
    comments: Optional[str]
    categories: Optional[List[str]]

class DeliveryExceptionCreate(BaseModel):
    delivery_id: str
    exception_type: str
    description: str
    photos: Optional[List[str]]
    location: Dict

class DigitalReceiptCreate(BaseModel):
    pod_id: str
    delivery_id: str
    delivery_details: Dict
