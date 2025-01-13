"""
Configuration Module

Handles application configuration with environment variables and Azure Key Vault integration.
"""
from functools import lru_cache
from typing import Optional
from pydantic import BaseSettings, Field

class CmnSettings(BaseSettings):
    """CMN module settings."""
    
    # Network Settings
    POOL_SIZE: int = Field(10, description="Connection pool size")
    CONNECTION_TIMEOUT: float = Field(30.0, description="Connection timeout in seconds")
    RETRY_ATTEMPTS: int = Field(3, description="Number of retry attempts")
    MAX_CONCURRENT_REQUESTS: int = Field(1000, description="Maximum concurrent requests")
    
    # Database Settings
    POSTGRES_USER: str = Field(..., description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL password")
    POSTGRES_HOST: str = Field(..., description="PostgreSQL host")
    POSTGRES_PORT: int = Field(5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(..., description="PostgreSQL database name")
    
    # Redis Settings
    REDIS_HOST: str = Field(..., description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password")
    
    # Azure Key Vault Settings
    AZURE_VAULT_URL: str = Field(..., description="Azure Key Vault URL")
    AZURE_CLIENT_ID: str = Field(..., description="Azure client ID")
    AZURE_CLIENT_SECRET: str = Field(..., description="Azure client secret")
    AZURE_TENANT_ID: str = Field(..., description="Azure tenant ID")
    
    # Certificate Settings
    CERTIFICATE_POLICY: dict = Field(
        default={
            "issuer": {"name": "Self"},
            "key_properties": {
                "exportable": True,
                "key_type": "RSA",
                "key_size": 2048,
                "reuse_key": False
            },
            "lifetime_actions": [{
                "action": {"action_type": "AutoRenew"},
                "trigger": {"days_before_expiry": 30}
            }],
            "secret_properties": {
                "content_type": "application/x-pkcs12"
            },
            "x509_properties": {
                "key_usage": [
                    "digitalSignature",
                    "keyEncipherment"
                ],
                "subject": "CN=ariesone.com",
                "validity_in_months": 12
            }
        },
        description="Certificate policy for Azure Key Vault"
    )
    
    # Monitoring Settings
    OTLP_ENDPOINT: str = Field(
        "http://localhost:4317",
        description="OpenTelemetry collector endpoint"
    )
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    ENABLE_METRICS: bool = Field(True, description="Enable metrics collection")
    METRICS_PORT: int = Field(9090, description="Prometheus metrics port")
    
    # Medicare Integration Settings
    MEDICARE_API_URL: str = Field(..., description="Medicare API URL")
    MEDICARE_API_TIMEOUT: int = Field(30, description="API timeout in seconds")
    MEDICARE_MAX_RETRIES: int = Field(3, description="Maximum API retries")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> CmnSettings:
    """Get cached settings instance."""
    return CmnSettings()
