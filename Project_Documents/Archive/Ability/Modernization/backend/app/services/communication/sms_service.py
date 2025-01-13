from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.communication import (
    SMSTemplate,
    SMSLog,
    PhoneNumber
)

class SMSService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.sms_config = self._load_sms_config()
        self.templates = self._load_templates()

    async def send_sms(
        self,
        template_id: str,
        recipient: Dict,
        data: Dict
    ) -> Dict:
        """Send SMS using template"""
        try:
            # Get template
            template = await self._get_template(template_id)
            
            # Render template
            message_content = await self._render_template(
                template,
                data
            )
            
            # Validate phone number
            phone_number = await self._validate_phone_number(
                recipient["phone"]
            )
            
            # Send SMS
            result = await self._send_via_provider(
                phone_number,
                message_content
            )
            
            # Log SMS
            log = await self._log_sms(
                template_id,
                recipient,
                result
            )
            
            return {
                "status": "success",
                "sms_id": log.id,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_template(
        self,
        template_data: Dict
    ) -> SMSTemplate:
        """Create new SMS template"""
        try:
            # Validate template
            self._validate_template(template_data)
            
            # Create template
            template = await SMSTemplate.create(
                name=template_data["name"],
                content=template_data["content"],
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

    async def update_template(
        self,
        template_id: str,
        template_data: Dict
    ) -> SMSTemplate:
        """Update existing SMS template"""
        try:
            # Get template
            template = await SMSTemplate.get(id=template_id)
            
            # Update fields
            for key, value in template_data.items():
                setattr(template, key, value)
            
            template.updated_at = datetime.now()
            await template.save()
            
            # Update template cache
            await self._update_template_cache(template)
            
            return template
        except Exception as e:
            logger.error(f"Failed to update template: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_template_preview(
        self,
        template_id: str,
        preview_data: Dict
    ) -> Dict:
        """Get preview of rendered template"""
        try:
            # Get template
            template = await self._get_template(template_id)
            
            # Render template
            message_content = await self._render_template(
                template,
                preview_data
            )
            
            return {
                "content": message_content
            }
        except Exception as e:
            logger.error(f"Failed to get template preview: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_template(self, template_id: str) -> SMSTemplate:
        """Get SMS template by ID"""
        template = self.templates.get(template_id)
        if not template:
            template = await SMSTemplate.get(id=template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            self.templates[template_id] = template
        return template

    async def _render_template(
        self,
        template: SMSTemplate,
        data: Dict
    ) -> str:
        """Render SMS template with data"""
        try:
            # Replace variables in content
            content = template.content
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                content = content.replace(placeholder, str(value))
            
            return content
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            raise

    async def _validate_phone_number(
        self,
        phone_number: str
    ) -> PhoneNumber:
        """Validate and format phone number"""
        try:
            # Clean phone number
            cleaned = self._clean_phone_number(phone_number)
            
            # Validate format
            if not self._is_valid_phone_number(cleaned):
                raise ValueError("Invalid phone number format")
            
            # Get or create phone record
            phone_record = await PhoneNumber.get_or_create(
                number=cleaned
            )
            
            return phone_record
        except Exception as e:
            logger.error(f"Phone validation failed: {str(e)}")
            raise

    async def _send_via_provider(
        self,
        phone_number: PhoneNumber,
        content: str
    ) -> Dict:
        """Send SMS via provider"""
        try:
            # Configure SMS provider connection
            sms = aiohttp.ClientSession()
            
            # Prepare SMS data
            sms_data = {
                "from": self.sms_config["from_number"],
                "to": phone_number.number,
                "message": content
            }
            
            # Send SMS
            async with sms.post(
                self.sms_config["api_url"],
                json=sms_data,
                headers={
                    "Authorization": f"Bearer {self.sms_config['api_key']}"
                }
            ) as response:
                if response.status != 200:
                    raise ValueError("SMS API request failed")
                result = await response.json()
            
            return result
        except Exception as e:
            logger.error(f"SMS provider send failed: {str(e)}")
            raise
        finally:
            await sms.close()

    async def _log_sms(
        self,
        template_id: str,
        recipient: Dict,
        result: Dict
    ) -> SMSLog:
        """Log SMS send attempt"""
        return await SMSLog.create(
            template_id=template_id,
            recipient_phone=recipient["phone"],
            recipient_name=recipient.get("name"),
            status=result["status"],
            message_id=result.get("message_id"),
            error=result.get("error"),
            created_at=datetime.now()
        )

    def _validate_template(self, template_data: Dict) -> None:
        """Validate SMS template data"""
        required_fields = [
            "name",
            "content",
            "variables",
            "category"
        ]
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Missing required field: {field}")
            
        # Validate template variables
        self._validate_template_variables(
            template_data["content"],
            template_data["variables"]
        )

    def _clean_phone_number(self, phone_number: str) -> str:
        """Clean phone number format"""
        return ''.join(filter(str.isdigit, phone_number))

    def _is_valid_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format"""
        return len(phone_number) >= 10
