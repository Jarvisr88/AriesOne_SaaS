from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class MapProvider(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50)
    api_key = fields.CharField(max_length=255)
    base_url = fields.CharField(max_length=255)
    priority = fields.IntField()  # Lower number = higher priority
    rate_limit = fields.JSONField()  # Requests per second/minute/day
    capabilities = fields.JSONField()  # Supported features
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "map_providers"

class GeocodingResult(models.Model):
    id = fields.UUIDField(pk=True)
    provider = fields.CharField(max_length=50)
    query = fields.CharField(max_length=255)
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    formatted_address = fields.CharField(max_length=255)
    confidence = fields.FloatField()
    raw_response = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "geocoding_results"
        indexes = (
            ("query", "provider"),
        )

class TrafficData(models.Model):
    id = fields.UUIDField(pk=True)
    provider = fields.CharField(max_length=50)
    bounds = fields.JSONField()  # Geographic bounds
    traffic_data = fields.JSONField()  # Traffic information
    timestamp = fields.DatetimeField()
    validity_period = fields.IntField()  # Seconds
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "traffic_data"
        indexes = (
            ("bounds", "timestamp"),
        )

class MapStyle(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50)
    provider = fields.CharField(max_length=50)
    style_json = fields.JSONField()
    is_default = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "map_styles"
        unique_together = ("name", "provider")

class ProviderStatus(models.Model):
    id = fields.UUIDField(pk=True)
    provider = fields.CharField(max_length=50)
    status = fields.CharField(max_length=20)  # active, down, degraded
    response_time = fields.FloatField(null=True)  # milliseconds
    error_count = fields.IntField(default=0)
    last_check = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "provider_status"

class MapCache(models.Model):
    id = fields.UUIDField(pk=True)
    provider = fields.CharField(max_length=50)
    cache_key = fields.CharField(max_length=255)
    cache_type = fields.CharField(max_length=50)  # tile, geocode, traffic
    data = fields.JSONField()
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "map_cache"
        indexes = (
            ("cache_key", "cache_type"),
        )

class MapMetrics(models.Model):
    id = fields.UUIDField(pk=True)
    provider = fields.CharField(max_length=50)
    date = fields.DateField()
    requests_count = fields.IntField()
    error_count = fields.IntField()
    average_response_time = fields.FloatField()
    cache_hit_rate = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "map_metrics"
        unique_together = ("provider", "date")

# Pydantic models for API
class MapProviderCreate(BaseModel):
    name: str
    api_key: str
    base_url: str
    priority: int
    rate_limit: Dict
    capabilities: Dict

class GeocodingRequest(BaseModel):
    address: str
    provider: Optional[str]

class TrafficRequest(BaseModel):
    bounds: Dict[str, float]
    provider: Optional[str]

class MapStyleCreate(BaseModel):
    name: str
    provider: str
    style_json: Dict
    is_default: Optional[bool]

class ProviderStatusUpdate(BaseModel):
    provider: str
    status: str
    response_time: Optional[float]
    error_count: Optional[int]

class MapCacheCreate(BaseModel):
    provider: str
    cache_key: str
    cache_type: str
    data: Dict
    expires_at: datetime

class MapMetricsCreate(BaseModel):
    provider: str
    date: datetime
    requests_count: int
    error_count: int
    average_response_time: float
    cache_hit_rate: float
