from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.integration import (
    ERPIntegration,
    ERPSyncLog,
    ERPMapping
)

class ERPService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.base_url = settings.ERP_BASE_URL
        self.api_key = settings.ERP_API_KEY

    async def sync_inventory(self) -> Dict:
        """Synchronize inventory with ERP system"""
        try:
            # Fetch inventory from ERP
            erp_inventory = await self._fetch_erp_data("inventory")
            
            # Map ERP inventory to our format
            mapped_inventory = await self._map_inventory_data(erp_inventory)
            
            # Update local inventory
            updated_items = await self._update_local_inventory(mapped_inventory)
            
            # Log sync
            await self._log_sync("inventory", len(updated_items))
            
            return {
                "status": "success",
                "items_synced": len(updated_items),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"ERP inventory sync failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def sync_orders(self) -> Dict:
        """Synchronize orders with ERP system"""
        try:
            # Fetch orders from ERP
            erp_orders = await self._fetch_erp_data("orders")
            
            # Map ERP orders to our format
            mapped_orders = await self._map_order_data(erp_orders)
            
            # Update local orders
            updated_orders = await self._update_local_orders(mapped_orders)
            
            # Log sync
            await self._log_sync("orders", len(updated_orders))
            
            return {
                "status": "success",
                "orders_synced": len(updated_orders),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"ERP order sync failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def sync_financials(self) -> Dict:
        """Synchronize financial data with ERP system"""
        try:
            # Fetch financial data from ERP
            erp_financials = await self._fetch_erp_data("financials")
            
            # Map ERP financials to our format
            mapped_financials = await self._map_financial_data(erp_financials)
            
            # Update local financials
            updated_records = await self._update_local_financials(mapped_financials)
            
            # Log sync
            await self._log_sync("financials", len(updated_records))
            
            return {
                "status": "success",
                "records_synced": len(updated_records),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"ERP financial sync failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _fetch_erp_data(self, endpoint: str) -> Dict:
        """Fetch data from ERP system"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            async with session.get(
                f"{self.base_url}/{endpoint}",
                headers=headers
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="ERP API request failed"
                    )
                return await response.json()

    async def _map_inventory_data(self, erp_data: Dict) -> List[Dict]:
        """Map ERP inventory data to local format"""
        mappings = await ERPMapping.filter(
            entity_type="inventory"
        ).all()
        mapped_data = []
        
        for item in erp_data["items"]:
            mapped_item = {}
            for mapping in mappings:
                mapped_item[mapping.local_field] = item.get(
                    mapping.erp_field
                )
            mapped_data.append(mapped_item)
        
        return mapped_data

    async def _map_order_data(self, erp_data: Dict) -> List[Dict]:
        """Map ERP order data to local format"""
        mappings = await ERPMapping.filter(
            entity_type="order"
        ).all()
        mapped_data = []
        
        for order in erp_data["orders"]:
            mapped_order = {}
            for mapping in mappings:
                mapped_order[mapping.local_field] = order.get(
                    mapping.erp_field
                )
            mapped_data.append(mapped_order)
        
        return mapped_data

    async def _map_financial_data(self, erp_data: Dict) -> List[Dict]:
        """Map ERP financial data to local format"""
        mappings = await ERPMapping.filter(
            entity_type="financial"
        ).all()
        mapped_data = []
        
        for record in erp_data["records"]:
            mapped_record = {}
            for mapping in mappings:
                mapped_record[mapping.local_field] = record.get(
                    mapping.erp_field
                )
            mapped_data.append(mapped_record)
        
        return mapped_data

    async def _log_sync(
        self,
        sync_type: str,
        items_synced: int
    ) -> None:
        """Log synchronization details"""
        await ERPSyncLog.create(
            sync_type=sync_type,
            items_synced=items_synced,
            status="success",
            timestamp=datetime.now()
        )
