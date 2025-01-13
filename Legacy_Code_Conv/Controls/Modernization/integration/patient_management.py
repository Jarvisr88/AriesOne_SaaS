from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import httpx
import logging
from fastapi import HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class PatientAddress(Base):
    __tablename__ = 'patient_addresses'

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, ForeignKey('patients.id'))
    address_type = Column(String)  # home, work, billing, etc.
    street_address = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AddressUpdate(BaseModel):
    address_type: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"

class PatientManagementIntegration:
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

    async def update_patient_address(
        self,
        patient_id: str,
        address_update: AddressUpdate,
        verify: bool = True
    ) -> Dict:
        """Update patient address with verification"""
        session = self.Session()
        try:
            # Verify address if requested
            verified_address = None
            if verify:
                from services.address_verification_service import address_verification_service
                verified_address = await address_verification_service.verify_address(
                    f"{address_update.street_address}, {address_update.city}, "
                    f"{address_update.state} {address_update.postal_code}"
                )

            # Update local database
            address = session.query(PatientAddress).filter_by(
                patient_id=patient_id,
                address_type=address_update.address_type
            ).first()

            if not address:
                address = PatientAddress(patient_id=patient_id)

            # Update address fields
            if verified_address:
                address.street_address = verified_address.components.street_number + " " + verified_address.components.street_name
                address.city = verified_address.components.city
                address.state = verified_address.components.state
                address.postal_code = verified_address.components.postal_code
                address.verified = True
                address.verification_date = datetime.utcnow()
            else:
                address.street_address = address_update.street_address
                address.city = address_update.city
                address.state = address_update.state
                address.postal_code = address_update.postal_code
                address.verified = False

            address.address_type = address_update.address_type
            address.country = address_update.country
            address.updated_at = datetime.utcnow()

            session.add(address)
            session.commit()

            # Update external patient management system
            await self._update_external_system(patient_id, address)

            return {
                "status": "success",
                "message": "Address updated successfully",
                "verified": address.verified,
                "address_id": address.id
            }

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update patient address: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update patient address: {str(e)}"
            )
        finally:
            session.close()

    async def _update_external_system(self, patient_id: str, address: PatientAddress):
        """Update address in external patient management system"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.api_base_url}/patients/{patient_id}/addresses",
                    headers=self.headers,
                    json={
                        "address_type": address.address_type,
                        "street_address": address.street_address,
                        "city": address.city,
                        "state": address.state,
                        "postal_code": address.postal_code,
                        "country": address.country,
                        "verified": address.verified,
                        "verification_date": address.verification_date.isoformat() if address.verification_date else None
                    }
                )
                response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to update external system: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update external system: {str(e)}"
            )

    async def get_patient_addresses(self, patient_id: str) -> List[Dict]:
        """Get all addresses for a patient"""
        session = self.Session()
        try:
            addresses = session.query(PatientAddress).filter_by(
                patient_id=patient_id
            ).all()

            return [{
                "id": addr.id,
                "address_type": addr.address_type,
                "street_address": addr.street_address,
                "city": addr.city,
                "state": addr.state,
                "postal_code": addr.postal_code,
                "country": addr.country,
                "verified": addr.verified,
                "verification_date": addr.verification_date.isoformat() if addr.verification_date else None,
                "created_at": addr.created_at.isoformat(),
                "updated_at": addr.updated_at.isoformat()
            } for addr in addresses]

        except Exception as e:
            logger.error(f"Failed to get patient addresses: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get patient addresses: {str(e)}"
            )
        finally:
            session.close()

    async def sync_addresses(self, patient_id: str):
        """Sync addresses between local and external system"""
        try:
            # Get addresses from external system
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/patients/{patient_id}/addresses",
                    headers=self.headers
                )
                response.raise_for_status()
                external_addresses = response.json()

            # Get local addresses
            local_addresses = await self.get_patient_addresses(patient_id)

            # Update local addresses that don't match external
            for ext_addr in external_addresses:
                matching_local = next(
                    (addr for addr in local_addresses if addr["address_type"] == ext_addr["address_type"]),
                    None
                )

                if not matching_local or self._addresses_differ(ext_addr, matching_local):
                    await self.update_patient_address(
                        patient_id,
                        AddressUpdate(**ext_addr),
                        verify=False
                    )

            return {
                "status": "success",
                "message": "Addresses synchronized successfully"
            }

        except Exception as e:
            logger.error(f"Failed to sync addresses: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to sync addresses: {str(e)}"
            )

    def _addresses_differ(self, addr1: Dict, addr2: Dict) -> bool:
        """Compare two addresses for differences"""
        fields = ["street_address", "city", "state", "postal_code", "country"]
        return any(addr1.get(field) != addr2.get(field) for field in fields)

# Initialize global integration service
patient_management = PatientManagementIntegration(
    db_url="postgresql://user:password@localhost/patient_db",
    api_base_url="https://api.patientmanagement.com/v1",
    api_key="your-api-key"
)
