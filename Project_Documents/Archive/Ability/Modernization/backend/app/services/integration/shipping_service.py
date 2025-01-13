from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.integration import (
    ShippingCarrier,
    ShipmentTracking,
    ShippingRate,
    ShippingLabel
)

class ShippingService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.carriers = self._load_carriers()

    async def get_shipping_rates(
        self,
        origin: Dict,
        destination: Dict,
        package_details: List[Dict]
    ) -> List[Dict]:
        """Get shipping rates from multiple carriers"""
        try:
            rates = []
            for carrier in self.carriers.values():
                carrier_rates = await self._get_carrier_rates(
                    carrier,
                    origin,
                    destination,
                    package_details
                )
                rates.extend(carrier_rates)
            
            # Store rates
            await self._store_rates(rates)
            
            return rates
        except Exception as e:
            logger.error(f"Failed to get shipping rates: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_shipment(
        self,
        carrier_id: str,
        rate_id: str,
        shipment_details: Dict
    ) -> Dict:
        """Create shipment with carrier"""
        try:
            # Get carrier
            carrier = await self._get_carrier(carrier_id)
            
            # Get rate
            rate = await ShippingRate.get(id=rate_id)
            
            # Create shipment
            shipment = await carrier.create_shipment(
                rate,
                shipment_details
            )
            
            # Generate label
            label = await self._generate_label(
                carrier,
                shipment
            )
            
            # Store tracking
            tracking = await self._create_tracking(
                carrier_id,
                shipment
            )
            
            return {
                "status": "success",
                "shipment_id": shipment["id"],
                "tracking_number": tracking.tracking_number,
                "label_url": label.url,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to create shipment: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def track_shipment(
        self,
        tracking_number: str
    ) -> Dict:
        """Track shipment status"""
        try:
            # Get tracking record
            tracking = await ShipmentTracking.get(
                tracking_number=tracking_number
            )
            
            # Get carrier
            carrier = await self._get_carrier(tracking.carrier_id)
            
            # Get tracking update
            status = await carrier.track_shipment(tracking_number)
            
            # Update tracking
            await self._update_tracking(tracking, status)
            
            return {
                "status": "success",
                "tracking_status": status,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to track shipment: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def void_shipment(
        self,
        shipment_id: str
    ) -> Dict:
        """Void shipment with carrier"""
        try:
            # Get tracking record
            tracking = await ShipmentTracking.get(
                shipment_id=shipment_id
            )
            
            # Get carrier
            carrier = await self._get_carrier(tracking.carrier_id)
            
            # Void shipment
            result = await carrier.void_shipment(shipment_id)
            
            # Update tracking
            await self._void_tracking(tracking)
            
            return {
                "status": "success",
                "void_status": result,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to void shipment: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_carrier_rates(
        self,
        carrier: ShippingCarrier,
        origin: Dict,
        destination: Dict,
        package_details: List[Dict]
    ) -> List[Dict]:
        """Get rates from specific carrier"""
        try:
            rates = await carrier.get_rates(
                origin,
                destination,
                package_details
            )
            
            return [{
                "carrier_id": carrier.id,
                "carrier_name": carrier.name,
                "service_code": rate["service_code"],
                "service_name": rate["service_name"],
                "rate": rate["rate"],
                "currency": rate["currency"],
                "delivery_days": rate["delivery_days"],
                "timestamp": datetime.now()
            } for rate in rates]
        except Exception as e:
            logger.error(
                f"Failed to get rates from carrier {carrier.name}: {str(e)}"
            )
            return []

    async def _store_rates(self, rates: List[Dict]) -> None:
        """Store shipping rates"""
        for rate in rates:
            await ShippingRate.create(**rate)

    async def _generate_label(
        self,
        carrier: ShippingCarrier,
        shipment: Dict
    ) -> ShippingLabel:
        """Generate shipping label"""
        label_data = await carrier.generate_label(shipment)
        
        return await ShippingLabel.create(
            carrier_id=carrier.id,
            shipment_id=shipment["id"],
            url=label_data["url"],
            format=label_data["format"],
            created_at=datetime.now()
        )

    async def _create_tracking(
        self,
        carrier_id: str,
        shipment: Dict
    ) -> ShipmentTracking:
        """Create tracking record"""
        return await ShipmentTracking.create(
            carrier_id=carrier_id,
            shipment_id=shipment["id"],
            tracking_number=shipment["tracking_number"],
            status="created",
            created_at=datetime.now()
        )

    async def _update_tracking(
        self,
        tracking: ShipmentTracking,
        status: Dict
    ) -> None:
        """Update tracking status"""
        tracking.status = status["status"]
        tracking.location = status.get("location")
        tracking.updated_at = datetime.now()
        await tracking.save()

    async def _void_tracking(
        self,
        tracking: ShipmentTracking
    ) -> None:
        """Void tracking record"""
        tracking.status = "voided"
        tracking.updated_at = datetime.now()
        await tracking.save()

    async def _get_carrier(
        self,
        carrier_id: str
    ) -> ShippingCarrier:
        """Get carrier by ID"""
        carrier = self.carriers.get(carrier_id)
        if not carrier:
            raise ValueError(f"No carrier found with ID {carrier_id}")
        return carrier
