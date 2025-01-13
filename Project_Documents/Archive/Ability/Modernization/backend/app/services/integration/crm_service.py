from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.integration import (
    CRMIntegration,
    CRMSyncLog,
    CRMMapping
)

class CRMService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.base_url = settings.CRM_BASE_URL
        self.api_key = settings.CRM_API_KEY

    async def sync_customers(self) -> Dict:
        """Synchronize customers with CRM system"""
        try:
            # Fetch customers from CRM
            crm_customers = await self._fetch_crm_data("customers")
            
            # Map CRM customers to our format
            mapped_customers = await self._map_customer_data(crm_customers)
            
            # Update local customers
            updated_customers = await self._update_local_customers(mapped_customers)
            
            # Log sync
            await self._log_sync("customers", len(updated_customers))
            
            return {
                "status": "success",
                "customers_synced": len(updated_customers),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"CRM customer sync failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def sync_interactions(self) -> Dict:
        """Synchronize customer interactions with CRM system"""
        try:
            # Fetch interactions from CRM
            crm_interactions = await self._fetch_crm_data("interactions")
            
            # Map CRM interactions to our format
            mapped_interactions = await self._map_interaction_data(crm_interactions)
            
            # Update local interactions
            updated_interactions = await self._update_local_interactions(mapped_interactions)
            
            # Log sync
            await self._log_sync("interactions", len(updated_interactions))
            
            return {
                "status": "success",
                "interactions_synced": len(updated_interactions),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"CRM interaction sync failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def sync_opportunities(self) -> Dict:
        """Synchronize sales opportunities with CRM system"""
        try:
            # Fetch opportunities from CRM
            crm_opportunities = await self._fetch_crm_data("opportunities")
            
            # Map CRM opportunities to our format
            mapped_opportunities = await self._map_opportunity_data(crm_opportunities)
            
            # Update local opportunities
            updated_opportunities = await self._update_local_opportunities(mapped_opportunities)
            
            # Log sync
            await self._log_sync("opportunities", len(updated_opportunities))
            
            return {
                "status": "success",
                "opportunities_synced": len(updated_opportunities),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"CRM opportunity sync failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def push_delivery_updates(self, updates: List[Dict]) -> Dict:
        """Push delivery updates to CRM system"""
        try:
            # Map updates to CRM format
            mapped_updates = await self._map_delivery_updates(updates)
            
            # Push updates to CRM
            response = await self._push_crm_data("delivery_updates", mapped_updates)
            
            # Log sync
            await self._log_sync("delivery_updates", len(updates))
            
            return {
                "status": "success",
                "updates_pushed": len(updates),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"CRM delivery update push failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _fetch_crm_data(self, endpoint: str) -> Dict:
        """Fetch data from CRM system"""
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
                        detail="CRM API request failed"
                    )
                return await response.json()

    async def _push_crm_data(self, endpoint: str, data: Dict) -> Dict:
        """Push data to CRM system"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            async with session.post(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="CRM API request failed"
                    )
                return await response.json()

    async def _map_customer_data(self, crm_data: Dict) -> List[Dict]:
        """Map CRM customer data to local format"""
        mappings = await CRMMapping.filter(
            entity_type="customer"
        ).all()
        mapped_data = []
        
        for customer in crm_data["customers"]:
            mapped_customer = {}
            for mapping in mappings:
                mapped_customer[mapping.local_field] = customer.get(
                    mapping.crm_field
                )
            mapped_data.append(mapped_customer)
        
        return mapped_data

    async def _map_interaction_data(self, crm_data: Dict) -> List[Dict]:
        """Map CRM interaction data to local format"""
        mappings = await CRMMapping.filter(
            entity_type="interaction"
        ).all()
        mapped_data = []
        
        for interaction in crm_data["interactions"]:
            mapped_interaction = {}
            for mapping in mappings:
                mapped_interaction[mapping.local_field] = interaction.get(
                    mapping.crm_field
                )
            mapped_data.append(mapped_interaction)
        
        return mapped_data

    async def _map_opportunity_data(self, crm_data: Dict) -> List[Dict]:
        """Map CRM opportunity data to local format"""
        mappings = await CRMMapping.filter(
            entity_type="opportunity"
        ).all()
        mapped_data = []
        
        for opportunity in crm_data["opportunities"]:
            mapped_opportunity = {}
            for mapping in mappings:
                mapped_opportunity[mapping.local_field] = opportunity.get(
                    mapping.crm_field
                )
            mapped_data.append(mapped_opportunity)
        
        return mapped_data

    async def _log_sync(
        self,
        sync_type: str,
        items_synced: int
    ) -> None:
        """Log synchronization details"""
        await CRMSyncLog.create(
            sync_type=sync_type,
            items_synced=items_synced,
            status="success",
            timestamp=datetime.now()
        )
