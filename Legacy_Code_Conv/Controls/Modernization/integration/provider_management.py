from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import httpx
import logging
from fastapi import HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class ProviderName(Base):
    __tablename__ = 'provider_names'

    id = Column(Integer, primary_key=True)
    provider_id = Column(String, ForeignKey('providers.id'))
    name_type = Column(String)  # legal, preferred, credential, etc.
    prefix = Column(String, nullable=True)
    first_name = Column(String)
    middle_name = Column(String, nullable=True)
    last_name = Column(String)
    suffix = Column(String, nullable=True)
    credentials = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NameUpdate(BaseModel):
    name_type: str
    prefix: Optional[str]
    first_name: str
    middle_name: Optional[str]
    last_name: str
    suffix: Optional[str]
    credentials: Optional[str]

class ProviderManagementIntegration:
    def __init__(self, db_url: str, api_base_url: str, api_key: str):
        # Database setup
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # API configuration
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def update_provider_name(
        self,
        provider_id: str,
        name_update: NameUpdate,
        validate: bool = True
    ) -> Dict:
        """Update provider name with validation"""
        session = self.Session()
        try:
            # Validate name if requested
            if validate:
                from validation.validation_framework import validator
                validation_errors = validator.validate_name(
                    f"{name_update.prefix or ''} {name_update.first_name} "
                    f"{name_update.middle_name or ''} {name_update.last_name} "
                    f"{name_update.suffix or ''}"
                )
                if validation_errors:
                    raise HTTPException(
                        status_code=400,
                        detail={"errors": validation_errors}
                    )

            # Update local database
            name = session.query(ProviderName).filter_by(
                provider_id=provider_id,
                name_type=name_update.name_type
            ).first()

            if not name:
                name = ProviderName(provider_id=provider_id)

            # Update name fields
            name.name_type = name_update.name_type
            name.prefix = name_update.prefix
            name.first_name = name_update.first_name
            name.middle_name = name_update.middle_name
            name.last_name = name_update.last_name
            name.suffix = name_update.suffix
            name.credentials = name_update.credentials
            name.updated_at = datetime.utcnow()

            session.add(name)
            session.commit()

            # Update external provider management system
            await self._update_external_system(provider_id, name)

            return {
                "status": "success",
                "message": "Name updated successfully",
                "name_id": name.id
            }

        except HTTPException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update provider name: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update provider name: {str(e)}"
            )
        finally:
            session.close()

    async def _update_external_system(self, provider_id: str, name: ProviderName):
        """Update name in external provider management system"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.api_base_url}/providers/{provider_id}/names",
                    headers=self.headers,
                    json={
                        "name_type": name.name_type,
                        "prefix": name.prefix,
                        "first_name": name.first_name,
                        "middle_name": name.middle_name,
                        "last_name": name.last_name,
                        "suffix": name.suffix,
                        "credentials": name.credentials,
                        "updated_at": name.updated_at.isoformat()
                    }
                )
                response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to update external system: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update external system: {str(e)}"
            )

    async def get_provider_names(self, provider_id: str) -> List[Dict]:
        """Get all names for a provider"""
        session = self.Session()
        try:
            names = session.query(ProviderName).filter_by(
                provider_id=provider_id
            ).all()

            return [{
                "id": name.id,
                "name_type": name.name_type,
                "prefix": name.prefix,
                "first_name": name.first_name,
                "middle_name": name.middle_name,
                "last_name": name.last_name,
                "suffix": name.suffix,
                "credentials": name.credentials,
                "created_at": name.created_at.isoformat(),
                "updated_at": name.updated_at.isoformat()
            } for name in names]

        except Exception as e:
            logger.error(f"Failed to get provider names: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get provider names: {str(e)}"
            )
        finally:
            session.close()

    async def sync_names(self, provider_id: str):
        """Sync names between local and external system"""
        try:
            # Get names from external system
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/providers/{provider_id}/names",
                    headers=self.headers
                )
                response.raise_for_status()
                external_names = response.json()

            # Get local names
            local_names = await self.get_provider_names(provider_id)

            # Update local names that don't match external
            for ext_name in external_names:
                matching_local = next(
                    (name for name in local_names if name["name_type"] == ext_name["name_type"]),
                    None
                )

                if not matching_local or self._names_differ(ext_name, matching_local):
                    await self.update_provider_name(
                        provider_id,
                        NameUpdate(**ext_name),
                        validate=False
                    )

            return {
                "status": "success",
                "message": "Names synchronized successfully"
            }

        except Exception as e:
            logger.error(f"Failed to sync names: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to sync names: {str(e)}"
            )

    def _names_differ(self, name1: Dict, name2: Dict) -> bool:
        """Compare two names for differences"""
        fields = ["prefix", "first_name", "middle_name", "last_name", "suffix", "credentials"]
        return any(name1.get(field) != name2.get(field) for field in fields)

# Initialize global integration service
provider_management = ProviderManagementIntegration(
    db_url="postgresql://user:password@localhost/provider_db",
    api_base_url="https://api.providermanagement.com/v1",
    api_key="your-api-key"
)
