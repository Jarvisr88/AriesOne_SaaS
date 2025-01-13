from datetime import datetime
from typing import Optional, Dict
from tortoise import fields, models
from pydantic import BaseModel

class IntegrationLog(models.Model):
    id = fields.UUIDField(pk=True)
    integration_type = fields.CharField(max_length=50)  # erp, ecommerce, supplier, edi
    action = fields.CharField(max_length=50)  # sync, process, validate
    status = fields.CharField(max_length=20)  # success, error, warning
    message = fields.TextField()
    metadata = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "integration_logs"

class ERPSync(models.Model):
    id = fields.UUIDField(pk=True)
    sync_type = fields.CharField(max_length=50)  # inventory, order, customer, etc.
    direction = fields.CharField(max_length=20)  # inbound, outbound
    status = fields.CharField(max_length=20)  # pending, in_progress, completed, failed
    data = fields.JSONField()
    response_data = fields.JSONField(null=True)
    error_message = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "erp_syncs"

class EcommerceSync(models.Model):
    id = fields.UUIDField(pk=True)
    channel = fields.CharField(max_length=50)  # amazon, shopify, etc.
    sync_type = fields.CharField(max_length=50)  # inventory, order, price
    status = fields.CharField(max_length=20)  # pending, in_progress, completed, failed
    data = fields.JSONField()
    response_data = fields.JSONField(null=True)
    error_message = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "ecommerce_syncs"

class SupplierSync(models.Model):
    id = fields.UUIDField(pk=True)
    supplier_id = fields.UUIDField()
    sync_type = fields.CharField(max_length=50)  # order, invoice, shipment
    status = fields.CharField(max_length=20)  # pending, in_progress, completed, failed
    data = fields.JSONField()
    response_data = fields.JSONField(null=True)
    error_message = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "supplier_syncs"

class EDIDocument(models.Model):
    id = fields.UUIDField(pk=True)
    document_type = fields.CharField(max_length=10)  # 850, 855, 856, 810
    raw_content = fields.TextField()
    parsed_data = fields.JSONField()
    processed_data = fields.JSONField(null=True)
    status = fields.CharField(max_length=20)  # processing, completed, failed
    error_message = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "edi_documents"

class SupplierIntegration(models.Model):
    id = fields.UUIDField(pk=True)
    supplier_id = fields.UUIDField()
    integration_type = fields.CharField(max_length=20)  # api, edi
    settings = fields.JSONField()  # API keys, endpoints, EDI settings
    status = fields.CharField(max_length=20)  # active, inactive
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "supplier_integrations"

# Pydantic models for API
class IntegrationLogCreate(BaseModel):
    integration_type: str
    action: str
    status: str
    message: str
    metadata: Optional[Dict] = None

class ERPSyncCreate(BaseModel):
    sync_type: str
    direction: str
    data: Dict

class EcommerceSyncCreate(BaseModel):
    channel: str
    sync_type: str
    data: Dict

class SupplierSyncCreate(BaseModel):
    supplier_id: str
    sync_type: str
    data: Dict

class EDIDocumentCreate(BaseModel):
    document_type: str
    raw_content: str

class SupplierIntegrationCreate(BaseModel):
    supplier_id: str
    integration_type: str
    settings: Dict
