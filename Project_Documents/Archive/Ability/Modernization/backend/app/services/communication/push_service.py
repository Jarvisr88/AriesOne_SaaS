from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.communication import (
    PushNotification,
    PushDevice,
    PushTemplate,
    PushLog
)

class PushService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.fcm_config = self._load_fcm_config()
        self.apns_config = self._load_apns_config()
        self.templates = self._load_templates()

    async def send_push(
        self,
        template_id: str,
        user_id: str,
        data: Dict,
        priority: str = "normal"
    ) -> Dict:
        """Send push notification using template"""
        try:
            # Get template
            template = await self._get_template(template_id)
            
            # Get user devices
            devices = await self._get_user_devices(user_id)
            
            if not devices:
                raise ValueError("No registered devices found")
            
            # Render template
            notification = await self._render_template(
                template,
                data
            )
            
            # Send to all devices
            results = []
            for device in devices:
                result = await self._send_to_device(
                    device,
                    notification,
                    priority
                )
                results.append(result)
            
            # Log notifications
            log = await self._log_push(
                template_id,
                user_id,
                results
            )
            
            return {
                "status": "success",
                "notification_id": log.id,
                "devices_sent": len(results),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def register_device(
        self,
        user_id: str,
        device_data: Dict
    ) -> PushDevice:
        """Register device for push notifications"""
        try:
            # Validate device data
            self._validate_device_data(device_data)
            
            # Create or update device
            device = await PushDevice.get_or_create(
                token=device_data["token"],
                defaults={
                    "user_id": user_id,
                    "platform": device_data["platform"],
                    "model": device_data.get("model"),
                    "os_version": device_data.get("os_version"),
                    "app_version": device_data.get("app_version"),
                    "created_at": datetime.now()
                }
            )
            
            return device
        except Exception as e:
            logger.error(f"Failed to register device: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_template(
        self,
        template_data: Dict
    ) -> PushTemplate:
        """Create new push notification template"""
        try:
            # Validate template
            self._validate_template(template_data)
            
            # Create template
            template = await PushTemplate.create(
                name=template_data["name"],
                title=template_data["title"],
                body=template_data["body"],
                data=template_data.get("data", {}),
                variables=template_data["variables"],
                category=template_data["category"],
                created_at=datetime.now()
            )
            
            # Update template cache
            await self._update_template_cache(template)
            
            return template
        except Exception as e:
            logger.error(f"Failed to create template: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_template(self, template_id: str) -> PushTemplate:
        """Get push template by ID"""
        template = self.templates.get(template_id)
        if not template:
            template = await PushTemplate.get(id=template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            self.templates[template_id] = template
        return template

    async def _get_user_devices(
        self,
        user_id: str
    ) -> List[PushDevice]:
        """Get user's registered devices"""
        return await PushDevice.filter(
            user_id=user_id,
            is_active=True
        ).all()

    async def _render_template(
        self,
        template: PushTemplate,
        data: Dict
    ) -> Dict:
        """Render push notification template"""
        try:
            # Replace variables in title and body
            title = template.title
            body = template.body
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                title = title.replace(placeholder, str(value))
                body = body.replace(placeholder, str(value))
            
            # Merge template data with provided data
            notification_data = {
                **template.data,
                **data
            }
            
            return {
                "title": title,
                "body": body,
                "data": notification_data
            }
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            raise

    async def _send_to_device(
        self,
        device: PushDevice,
        notification: Dict,
        priority: str
    ) -> Dict:
        """Send notification to specific device"""
        try:
            if device.platform == "android":
                return await self._send_fcm(
                    device.token,
                    notification,
                    priority
                )
            elif device.platform == "ios":
                return await self._send_apns(
                    device.token,
                    notification,
                    priority
                )
            else:
                raise ValueError(f"Unsupported platform: {device.platform}")
        except Exception as e:
            logger.error(f"Device push failed: {str(e)}")
            return {
                "status": "error",
                "device_id": device.id,
                "error": str(e)
            }

    async def _send_fcm(
        self,
        token: str,
        notification: Dict,
        priority: str
    ) -> Dict:
        """Send via Firebase Cloud Messaging"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "to": token,
                    "notification": {
                        "title": notification["title"],
                        "body": notification["body"]
                    },
                    "data": notification["data"],
                    "priority": priority
                }
                
                async with session.post(
                    self.fcm_config["api_url"],
                    json=payload,
                    headers={
                        "Authorization": f"key={self.fcm_config['api_key']}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    if response.status != 200:
                        raise ValueError("FCM request failed")
                    result = await response.json()
                
                return {
                    "status": "success",
                    "message_id": result["message_id"]
                }
        except Exception as e:
            logger.error(f"FCM send failed: {str(e)}")
            raise

    async def _send_apns(
        self,
        token: str,
        notification: Dict,
        priority: str
    ) -> Dict:
        """Send via Apple Push Notification Service"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "aps": {
                        "alert": {
                            "title": notification["title"],
                            "body": notification["body"]
                        },
                        "sound": "default",
                        "priority": 10 if priority == "high" else 5
                    },
                    "data": notification["data"]
                }
                
                async with session.post(
                    f"{self.apns_config['api_url']}/3/device/{token}",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.apns_config['api_key']}",
                        "apns-topic": self.apns_config["bundle_id"],
                        "apns-priority": "10" if priority == "high" else "5"
                    }
                ) as response:
                    if response.status != 200:
                        raise ValueError("APNS request failed")
                
                return {
                    "status": "success",
                    "apns_id": response.headers.get("apns-id")
                }
        except Exception as e:
            logger.error(f"APNS send failed: {str(e)}")
            raise

    async def _log_push(
        self,
        template_id: str,
        user_id: str,
        results: List[Dict]
    ) -> PushLog:
        """Log push notification attempts"""
        return await PushLog.create(
            template_id=template_id,
            user_id=user_id,
            devices_count=len(results),
            success_count=len([r for r in results if r["status"] == "success"]),
            error_count=len([r for r in results if r["status"] == "error"]),
            results=results,
            created_at=datetime.now()
        )
