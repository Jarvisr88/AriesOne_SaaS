from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
import json
from cryptography.fernet import Fernet

from app.models.core import ConfigurationKey, Tenant, Company
from app.core.config import settings
from app.core.cache import RedisCache

class ConfigurationService:
    def __init__(self, db: Session, cache: RedisCache):
        self.db = db
        self.cache = cache
        self.crypto = Fernet(settings.ENCRYPTION_KEY.encode()) if settings.ENCRYPTION_KEY else None

    async def get_config(
        self,
        key: str,
        tenant_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Any:
        """Get configuration value with inheritance"""
        cache_key = f"config:{tenant_id or 'system'}:{company_id or 'tenant'}:{key}"
        
        # Try cache first
        cached_value = await self.cache.get(cache_key)
        if cached_value is not None:
            return json.loads(cached_value)

        # Query database with inheritance
        config = None
        
        # Try company-specific config
        if company_id:
            config = self.db.query(ConfigurationKey).filter(
                ConfigurationKey.key == key,
                ConfigurationKey.company_id == company_id
            ).first()

        # Try tenant-specific config
        if not config and tenant_id:
            config = self.db.query(ConfigurationKey).filter(
                ConfigurationKey.key == key,
                ConfigurationKey.tenant_id == tenant_id,
                ConfigurationKey.company_id.is_(None)
            ).first()

        # Try system-wide config
        if not config:
            config = self.db.query(ConfigurationKey).filter(
                ConfigurationKey.key == key,
                ConfigurationKey.tenant_id.is_(None),
                ConfigurationKey.company_id.is_(None)
            ).first()

        if not config:
            return None

        value = self._decrypt_value(config) if config.is_encrypted else config.value
        
        # Cache the value
        await self.cache.set(
            cache_key,
            json.dumps(value),
            expire=settings.CONFIG_CACHE_TTL
        )

        return value

    async def set_config(
        self,
        key: str,
        value: Any,
        description: Optional[str] = None,
        is_sensitive: bool = False,
        tenant_id: Optional[int] = None,
        company_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConfigurationKey:
        """Set configuration value"""
        # Validate tenant and company
        if tenant_id:
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")

        if company_id:
            company = self.db.query(Company).filter(
                Company.id == company_id,
                Company.tenant_id == tenant_id
            ).first()
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")

        # Check if config exists
        config = self.db.query(ConfigurationKey).filter(
            ConfigurationKey.key == key,
            ConfigurationKey.tenant_id == tenant_id,
            ConfigurationKey.company_id == company_id
        ).first()

        if config:
            # Update existing config
            config.value = self._encrypt_value(value) if is_sensitive else value
            config.description = description or config.description
            config.is_sensitive = is_sensitive
            config.is_encrypted = is_sensitive
            config.metadata = metadata or config.metadata
            config.updated_at = datetime.now(timezone.utc)
        else:
            # Create new config
            config = ConfigurationKey(
                key=key,
                value=self._encrypt_value(value) if is_sensitive else value,
                description=description,
                is_sensitive=is_sensitive,
                is_encrypted=is_sensitive,
                tenant_id=tenant_id,
                company_id=company_id,
                metadata=metadata
            )
            self.db.add(config)

        self.db.commit()
        self.db.refresh(config)

        # Invalidate cache
        await self._invalidate_config_cache(key, tenant_id, company_id)

        return config

    async def delete_config(
        self,
        key: str,
        tenant_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> bool:
        """Delete configuration"""
        config = self.db.query(ConfigurationKey).filter(
            ConfigurationKey.key == key,
            ConfigurationKey.tenant_id == tenant_id,
            ConfigurationKey.company_id == company_id
        ).first()

        if not config:
            return False

        self.db.delete(config)
        self.db.commit()

        # Invalidate cache
        await self._invalidate_config_cache(key, tenant_id, company_id)

        return True

    async def get_all_configs(
        self,
        tenant_id: Optional[int] = None,
        company_id: Optional[int] = None,
        include_sensitive: bool = False
    ) -> List[ConfigurationKey]:
        """Get all configurations for tenant/company"""
        query = self.db.query(ConfigurationKey)

        if tenant_id:
            query = query.filter(ConfigurationKey.tenant_id == tenant_id)
        if company_id:
            query = query.filter(ConfigurationKey.company_id == company_id)
        if not include_sensitive:
            query = query.filter(ConfigurationKey.is_sensitive == False)

        configs = query.all()

        # Decrypt sensitive values if included
        if include_sensitive:
            for config in configs:
                if config.is_encrypted:
                    config.value = self._decrypt_value(config)

        return configs

    async def get_tenant_features(
        self,
        tenant_id: int
    ) -> Dict[str, Any]:
        """Get tenant feature flags"""
        cache_key = f"tenant_features:{tenant_id}"
        
        # Try cache first
        cached_features = await self.cache.get(cache_key)
        if cached_features:
            return json.loads(cached_features)

        # Get tenant features
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        features = tenant.features or {}
        
        # Cache features
        await self.cache.set(
            cache_key,
            json.dumps(features),
            expire=settings.FEATURES_CACHE_TTL
        )

        return features

    async def update_tenant_features(
        self,
        tenant_id: int,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update tenant feature flags"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant.features = features
        self.db.commit()

        # Invalidate cache
        await self.cache.delete(f"tenant_features:{tenant_id}")

        return features

    def _encrypt_value(self, value: Any) -> str:
        """Encrypt sensitive configuration value"""
        if not self.crypto:
            raise HTTPException(
                status_code=500,
                detail="Encryption key not configured"
            )

        try:
            value_str = json.dumps(value)
            encrypted = self.crypto.encrypt(value_str.encode())
            return encrypted.decode()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Encryption failed: {str(e)}"
            )

    def _decrypt_value(self, config: ConfigurationKey) -> Any:
        """Decrypt sensitive configuration value"""
        if not self.crypto:
            raise HTTPException(
                status_code=500,
                detail="Encryption key not configured"
            )

        if not config.is_encrypted:
            return config.value

        try:
            decrypted = self.crypto.decrypt(config.value.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Decryption failed: {str(e)}"
            )

    async def _invalidate_config_cache(
        self,
        key: str,
        tenant_id: Optional[int],
        company_id: Optional[int]
    ) -> None:
        """Invalidate configuration cache"""
        cache_key = f"config:{tenant_id or 'system'}:{company_id or 'tenant'}:{key}"
        await self.cache.delete(cache_key)
