from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.integration import (
    Marketplace,
    MarketplaceProduct,
    MarketplaceOrder,
    MarketplaceSync
)

class MarketplaceService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.marketplaces = self._load_marketplaces()

    async def sync_products(
        self,
        marketplace_id: Optional[str] = None
    ) -> Dict:
        """Sync products with marketplace(s)"""
        try:
            results = []
            marketplaces = (
                [self.marketplaces[marketplace_id]]
                if marketplace_id
                else self.marketplaces.values()
            )
            
            for marketplace in marketplaces:
                result = await self._sync_marketplace_products(marketplace)
                results.append(result)
            
            return {
                "status": "success",
                "results": results,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to sync products: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def sync_orders(
        self,
        marketplace_id: Optional[str] = None
    ) -> Dict:
        """Sync orders with marketplace(s)"""
        try:
            results = []
            marketplaces = (
                [self.marketplaces[marketplace_id]]
                if marketplace_id
                else self.marketplaces.values()
            )
            
            for marketplace in marketplaces:
                result = await self._sync_marketplace_orders(marketplace)
                results.append(result)
            
            return {
                "status": "success",
                "results": results,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to sync orders: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_inventory(
        self,
        product_updates: List[Dict]
    ) -> Dict:
        """Update inventory levels across marketplaces"""
        try:
            results = []
            for marketplace in self.marketplaces.values():
                result = await self._update_marketplace_inventory(
                    marketplace,
                    product_updates
                )
                results.append(result)
            
            return {
                "status": "success",
                "results": results,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to update inventory: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_order_status(
        self,
        order_updates: List[Dict]
    ) -> Dict:
        """Update order status across marketplaces"""
        try:
            results = []
            for update in order_updates:
                order = await MarketplaceOrder.get(
                    marketplace_order_id=update["marketplace_order_id"]
                )
                marketplace = self.marketplaces[order.marketplace_id]
                
                result = await self._update_marketplace_order(
                    marketplace,
                    update
                )
                results.append(result)
            
            return {
                "status": "success",
                "results": results,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to update order status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _sync_marketplace_products(
        self,
        marketplace: Marketplace
    ) -> Dict:
        """Sync products with specific marketplace"""
        try:
            # Get products from marketplace
            products = await marketplace.get_products()
            
            # Map products to local format
            mapped_products = await self._map_products(
                marketplace.id,
                products
            )
            
            # Update local products
            updated = await self._update_products(mapped_products)
            
            # Log sync
            await self._log_sync(
                marketplace.id,
                "products",
                len(updated)
            )
            
            return {
                "marketplace": marketplace.name,
                "products_synced": len(updated)
            }
        except Exception as e:
            logger.error(
                f"Failed to sync products for {marketplace.name}: {str(e)}"
            )
            return {
                "marketplace": marketplace.name,
                "error": str(e)
            }

    async def _sync_marketplace_orders(
        self,
        marketplace: Marketplace
    ) -> Dict:
        """Sync orders with specific marketplace"""
        try:
            # Get orders from marketplace
            orders = await marketplace.get_orders()
            
            # Map orders to local format
            mapped_orders = await self._map_orders(
                marketplace.id,
                orders
            )
            
            # Update local orders
            updated = await self._update_orders(mapped_orders)
            
            # Log sync
            await self._log_sync(
                marketplace.id,
                "orders",
                len(updated)
            )
            
            return {
                "marketplace": marketplace.name,
                "orders_synced": len(updated)
            }
        except Exception as e:
            logger.error(
                f"Failed to sync orders for {marketplace.name}: {str(e)}"
            )
            return {
                "marketplace": marketplace.name,
                "error": str(e)
            }

    async def _update_marketplace_inventory(
        self,
        marketplace: Marketplace,
        updates: List[Dict]
    ) -> Dict:
        """Update inventory for specific marketplace"""
        try:
            # Map updates to marketplace format
            mapped_updates = await self._map_inventory_updates(
                marketplace.id,
                updates
            )
            
            # Update marketplace
            result = await marketplace.update_inventory(mapped_updates)
            
            # Log update
            await self._log_sync(
                marketplace.id,
                "inventory",
                len(updates)
            )
            
            return {
                "marketplace": marketplace.name,
                "updates_processed": len(updates)
            }
        except Exception as e:
            logger.error(
                f"Failed to update inventory for {marketplace.name}: {str(e)}"
            )
            return {
                "marketplace": marketplace.name,
                "error": str(e)
            }

    async def _update_marketplace_order(
        self,
        marketplace: Marketplace,
        update: Dict
    ) -> Dict:
        """Update order in specific marketplace"""
        try:
            # Map update to marketplace format
            mapped_update = await self._map_order_update(
                marketplace.id,
                update
            )
            
            # Update marketplace
            result = await marketplace.update_order(mapped_update)
            
            # Log update
            await self._log_sync(
                marketplace.id,
                "order_status",
                1
            )
            
            return {
                "marketplace": marketplace.name,
                "order_id": update["marketplace_order_id"],
                "status": "updated"
            }
        except Exception as e:
            logger.error(
                f"Failed to update order in {marketplace.name}: {str(e)}"
            )
            return {
                "marketplace": marketplace.name,
                "order_id": update["marketplace_order_id"],
                "error": str(e)
            }

    async def _log_sync(
        self,
        marketplace_id: str,
        sync_type: str,
        items_synced: int
    ) -> None:
        """Log marketplace sync"""
        await MarketplaceSync.create(
            marketplace_id=marketplace_id,
            sync_type=sync_type,
            items_synced=items_synced,
            status="success",
            timestamp=datetime.now()
        )
