from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class WeatherProvider(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50)
    api_key = fields.CharField(max_length=255)
    base_url = fields.CharField(max_length=255)
    priority = fields.IntField()
    capabilities = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "weather_providers"

class WeatherData(models.Model):
    id = fields.UUIDField(pk=True)
    provider = fields.CharField(max_length=50)
    location = fields.JSONField()  # lat, lng
    temperature = fields.FloatField()
    feels_like = fields.FloatField()
    humidity = fields.IntField()
    pressure = fields.IntField()
    wind_speed = fields.FloatField()
    wind_direction = fields.IntField()
    precipitation = fields.FloatField()
    condition = fields.CharField(max_length=50)
    visibility = fields.FloatField()
    timestamp = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "weather_data"
        indexes = (
            ("location", "timestamp"),
        )

class WeatherForecast(models.Model):
    id = fields.UUIDField(pk=True)
    provider = fields.CharField(max_length=50)
    location = fields.JSONField()
    forecast_time = fields.DatetimeField()
    temperature = fields.FloatField()
    feels_like = fields.FloatField()
    humidity = fields.IntField()
    precipitation_prob = fields.FloatField()
    precipitation_amount = fields.FloatField()
    condition = fields.CharField(max_length=50)
    wind_speed = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "weather_forecasts"

class WeatherAlert(models.Model):
    id = fields.UUIDField(pk=True)
    provider = fields.CharField(max_length=50)
    location = fields.JSONField()
    alert_type = fields.CharField(max_length=50)
    severity = fields.CharField(max_length=20)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "weather_alerts"

class WeatherImpact(models.Model):
    id = fields.UUIDField(pk=True)
    route_id = fields.CharField(max_length=100)
    schedule_time = fields.DatetimeField()
    weather_conditions = fields.JSONField()
    severe_conditions = fields.JSONField()
    delay_probability = fields.FloatField()
    recommendations = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "weather_impacts"

# Pydantic models for API
class WeatherDataCreate(BaseModel):
    provider: str
    location: Dict[str, float]
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: int
    precipitation: float
    condition: str
    visibility: float
    timestamp: datetime

class WeatherForecastCreate(BaseModel):
    provider: str
    location: Dict[str, float]
    forecast_time: datetime
    temperature: float
    feels_like: float
    humidity: int
    precipitation_prob: float
    precipitation_amount: float
    condition: str
    wind_speed: float

class WeatherAlertCreate(BaseModel):
    provider: str
    location: Dict[str, float]
    alert_type: str
    severity: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime

class WeatherImpactCreate(BaseModel):
    route_id: str
    schedule_time: datetime
    weather_conditions: Dict
    severe_conditions: List[Dict]
    delay_probability: float
    recommendations: List[str]
