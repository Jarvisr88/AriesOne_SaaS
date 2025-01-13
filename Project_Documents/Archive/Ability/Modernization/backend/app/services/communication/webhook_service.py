from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
import hmac
import hashlib
import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.communication import (
    Webhook,
    WebhookEvent,
    WebhookDelivery
)

class WebhookService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.secret_key = settings.WEBHOOK_SECRET_KEY
        self.max_retries = 3
        self.retry_delays = [60, 300, 900]  # 1min, 5min, 15min

    async def register_webhook(
        self,
        webhook_data: Dict
    ) -> Webhook:
        """Register new webhook endpoint"""
        try:
            # Validate webhook data
            self._validate_webhook_data(webhook_data)
            
            # Create webhook
            webhook = await Webhook.create(
                url=webhook_data["url"],
                events=webhook_data["events"],
                description=webhook_data.get("description"),
                headers=webhook_data.get("headers", {}),
                is_active=True,
                created_at=datetime.now()
            )
            
            # Generate secret
            secret = self._generate_secret()
            webhook.secret = secret
            await webhook.save()
            
            return webhook
        except Exception as e:
            logger.error(f"Failed to register webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def trigger_event(
        self,
        event_type: str,
        payload: Dict
    ) -> List[Dict]:
        """Trigger webhook event"""
        try:
            # Find relevant webhooks
            webhooks = await Webhook.filter(
                events__contains=[event_type],
                is_active=True
            ).all()
            
            if not webhooks:
                return []
            
            # Create event record
            event = await WebhookEvent.create(
                event_type=event_type,
                payload=payload,
                created_at=datetime.now()
            )
            
            # Deliver to all webhooks
            results = []
            for webhook in webhooks:
                delivery = await self._deliver_event(
                    webhook,
                    event,
                    payload
                )
                results.append(delivery)
            
            return results
        except Exception as e:
            logger.error(f"Failed to trigger webhook event: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def retry_delivery(
        self,
        delivery_id: str
    ) -> Dict:
        """Retry failed webhook delivery"""
        try:
            # Get delivery record
            delivery = await WebhookDelivery.get(id=delivery_id)
            
            if delivery.status == "success":
                return {
                    "status": "skipped",
                    "message": "Delivery already successful"
                }
            
            if delivery.retry_count >= self.max_retries:
                return {
                    "status": "failed",
                    "message": "Max retries exceeded"
                }
            
            # Get webhook and event
            webhook = await Webhook.get(id=delivery.webhook_id)
            event = await WebhookEvent.get(id=delivery.event_id)
            
            # Retry delivery
            result = await self._deliver_event(
                webhook,
                event,
                event.payload,
                delivery
            )
            
            return result
        except Exception as e:
            logger.error(f"Failed to retry webhook delivery: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _deliver_event(
        self,
        webhook: Webhook,
        event: WebhookEvent,
        payload: Dict,
        existing_delivery: Optional[WebhookDelivery] = None
    ) -> Dict:
        """Deliver event to webhook endpoint"""
        try:
            # Prepare delivery record
            delivery = existing_delivery or await WebhookDelivery.create(
                webhook_id=webhook.id,
                event_id=event.id,
                payload=payload,
                retry_count=0,
                created_at=datetime.now()
            )
            
            # Prepare request
            headers = {
                **webhook.headers,
                "Content-Type": "application/json",
                "User-Agent": "AriesOne-Webhook/1.0",
                "X-Webhook-ID": str(webhook.id),
                "X-Event-Type": event.event_type,
                "X-Delivery-ID": str(delivery.id)
            }
            
            # Add signature
            signature = self._generate_signature(
                webhook.secret,
                payload
            )
            headers["X-Webhook-Signature"] = signature
            
            # Send request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    response_body = await response.text()
                    
                    delivery.status = (
                        "success"
                        if 200 <= response.status < 300
                        else "failed"
                    )
                    delivery.response_code = response.status
                    delivery.response_body = response_body
                    delivery.completed_at = datetime.now()
                    
                    if existing_delivery:
                        delivery.retry_count += 1
                    
                    await delivery.save()
                    
                    return {
                        "status": delivery.status,
                        "delivery_id": str(delivery.id),
                        "response_code": delivery.response_code
                    }
        except Exception as e:
            logger.error(f"Webhook delivery failed: {str(e)}")
            
            if delivery:
                delivery.status = "failed"
                delivery.error = str(e)
                delivery.completed_at = datetime.now()
                if existing_delivery:
                    delivery.retry_count += 1
                await delivery.save()
            
            return {
                "status": "failed",
                "delivery_id": str(delivery.id) if delivery else None,
                "error": str(e)
            }

    def _validate_webhook_data(self, webhook_data: Dict) -> None:
        """Validate webhook registration data"""
        required_fields = ["url", "events"]
        for field in required_fields:
            if field not in webhook_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(webhook_data["events"], list):
            raise ValueError("Events must be a list")
        
        if not webhook_data["events"]:
            raise ValueError("At least one event must be specified")

    def _generate_secret(self) -> str:
        """Generate webhook secret"""
        return hashlib.sha256(
            str(datetime.now().timestamp()).encode()
        ).hexdigest()

    def _generate_signature(
        self,
        secret: str,
        payload: Dict
    ) -> str:
        """Generate webhook signature"""
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
