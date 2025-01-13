from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class Notification(models.Model):
    id = fields.UUIDField(pk=True)
    customer_id = fields.CharField(max_length=100)
    type = fields.CharField(max_length=50)
    method = fields.CharField(max_length=20)  # sms, email
    content = fields.JSONField()
    status = fields.CharField(max_length=20)  # sent, failed, delivered
    provider_response = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    delivered_at = fields.DatetimeField(null=True)

    class Meta:
        table = "notifications"

class EmailTemplate(models.Model):
    id = fields.UUIDField(pk=True)
    type = fields.CharField(max_length=50)
    subject_template = fields.TextField()
    body_template = fields.TextField()
    variables = fields.JSONField()  # Required variables
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "email_templates"

class SMSTemplate(models.Model):
    id = fields.UUIDField(pk=True)
    type = fields.CharField(max_length=50)
    template = fields.TextField()
    variables = fields.JSONField()
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "sms_templates"

class DeliveryUpdate(models.Model):
    id = fields.UUIDField(pk=True)
    delivery_id = fields.CharField(max_length=100)
    status = fields.CharField(max_length=50)
    details = fields.JSONField(null=True)
    notification_sent = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "delivery_updates"

class CustomerRating(models.Model):
    id = fields.UUIDField(pk=True)
    delivery_id = fields.CharField(max_length=100)
    rating = fields.IntField()  # 1-5
    feedback = fields.TextField(null=True)
    categories = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "customer_ratings"

class NotificationPreference(models.Model):
    id = fields.UUIDField(pk=True)
    customer_id = fields.CharField(max_length=100)
    email_enabled = fields.BooleanField(default=True)
    sms_enabled = fields.BooleanField(default=True)
    email_types = fields.JSONField()  # List of notification types
    sms_types = fields.JSONField()
    quiet_hours = fields.JSONField(null=True)  # Start and end times
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_preferences"

class CommunicationMetrics(models.Model):
    id = fields.UUIDField(pk=True)
    date = fields.DateField()
    notifications_sent = fields.IntField()
    delivery_rate = fields.FloatField()
    average_rating = fields.FloatField()
    response_rate = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "communication_metrics"

# Pydantic models for API
class NotificationCreate(BaseModel):
    customer_id: str
    type: str
    method: str
    content: Dict

class EmailTemplateCreate(BaseModel):
    type: str
    subject_template: str
    body_template: str
    variables: List[str]
    is_active: Optional[bool] = True

class SMSTemplateCreate(BaseModel):
    type: str
    template: str
    variables: List[str]
    is_active: Optional[bool] = True

class DeliveryUpdateCreate(BaseModel):
    delivery_id: str
    status: str
    details: Optional[Dict]

class CustomerRatingCreate(BaseModel):
    delivery_id: str
    rating: int
    feedback: Optional[str]
    categories: Optional[List[str]]

class NotificationPreferenceCreate(BaseModel):
    customer_id: str
    email_enabled: bool
    sms_enabled: bool
    email_types: List[str]
    sms_types: List[str]
    quiet_hours: Optional[Dict]
