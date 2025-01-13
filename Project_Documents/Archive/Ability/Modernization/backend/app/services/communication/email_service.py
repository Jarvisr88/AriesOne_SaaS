from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException
from jinja2 import Template
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.communication import (
    EmailTemplate,
    EmailLog,
    EmailAttachment
)

class EmailService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.smtp_config = self._load_smtp_config()
        self.templates = self._load_templates()

    async def send_email(
        self,
        template_id: str,
        recipient: Dict,
        data: Dict,
        attachments: Optional[List[Dict]] = None
    ) -> Dict:
        """Send email using template"""
        try:
            # Get template
            template = await self._get_template(template_id)
            
            # Render template
            email_content = await self._render_template(
                template,
                data
            )
            
            # Process attachments
            processed_attachments = await self._process_attachments(
                attachments
            ) if attachments else []
            
            # Send email
            result = await self._send_via_smtp(
                recipient,
                email_content,
                processed_attachments
            )
            
            # Log email
            log = await self._log_email(
                template_id,
                recipient,
                result
            )
            
            return {
                "status": "success",
                "email_id": log.id,
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_template(
        self,
        template_data: Dict
    ) -> EmailTemplate:
        """Create new email template"""
        try:
            # Validate template
            self._validate_template(template_data)
            
            # Create template
            template = await EmailTemplate.create(
                name=template_data["name"],
                subject=template_data["subject"],
                body_html=template_data["body_html"],
                body_text=template_data["body_text"],
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
    ) -> EmailTemplate:
        """Update existing email template"""
        try:
            # Get template
            template = await EmailTemplate.get(id=template_id)
            
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
            email_content = await self._render_template(
                template,
                preview_data
            )
            
            return {
                "subject": email_content["subject"],
                "body_html": email_content["body_html"],
                "body_text": email_content["body_text"]
            }
        except Exception as e:
            logger.error(f"Failed to get template preview: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_template(self, template_id: str) -> EmailTemplate:
        """Get email template by ID"""
        template = self.templates.get(template_id)
        if not template:
            template = await EmailTemplate.get(id=template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            self.templates[template_id] = template
        return template

    async def _render_template(
        self,
        template: EmailTemplate,
        data: Dict
    ) -> Dict:
        """Render email template with data"""
        try:
            # Render subject
            subject_template = Template(template.subject)
            subject = subject_template.render(**data)
            
            # Render HTML body
            html_template = Template(template.body_html)
            body_html = html_template.render(**data)
            
            # Render text body
            text_template = Template(template.body_text)
            body_text = text_template.render(**data)
            
            return {
                "subject": subject,
                "body_html": body_html,
                "body_text": body_text
            }
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            raise

    async def _process_attachments(
        self,
        attachments: List[Dict]
    ) -> List[EmailAttachment]:
        """Process email attachments"""
        processed = []
        for attachment in attachments:
            processed_attachment = await EmailAttachment.create(
                filename=attachment["filename"],
                content_type=attachment["content_type"],
                content=attachment["content"],
                created_at=datetime.now()
            )
            processed.append(processed_attachment)
        return processed

    async def _send_via_smtp(
        self,
        recipient: Dict,
        content: Dict,
        attachments: List[EmailAttachment]
    ) -> Dict:
        """Send email via SMTP"""
        try:
            # Configure SMTP connection
            smtp = aiohttp.ClientSession()
            
            # Prepare email data
            email_data = {
                "from": self.smtp_config["from_address"],
                "to": recipient["email"],
                "subject": content["subject"],
                "html": content["body_html"],
                "text": content["body_text"],
                "attachments": [
                    {
                        "filename": att.filename,
                        "content": att.content,
                        "content_type": att.content_type
                    }
                    for att in attachments
                ]
            }
            
            # Send email
            async with smtp.post(
                self.smtp_config["api_url"],
                json=email_data,
                headers={
                    "Authorization": f"Bearer {self.smtp_config['api_key']}"
                }
            ) as response:
                if response.status != 200:
                    raise ValueError("SMTP API request failed")
                result = await response.json()
            
            return result
        except Exception as e:
            logger.error(f"SMTP send failed: {str(e)}")
            raise
        finally:
            await smtp.close()

    async def _log_email(
        self,
        template_id: str,
        recipient: Dict,
        result: Dict
    ) -> EmailLog:
        """Log email send attempt"""
        return await EmailLog.create(
            template_id=template_id,
            recipient_email=recipient["email"],
            recipient_name=recipient.get("name"),
            status=result["status"],
            message_id=result.get("message_id"),
            error=result.get("error"),
            created_at=datetime.now()
        )

    def _validate_template(self, template_data: Dict) -> None:
        """Validate email template data"""
        required_fields = [
            "name",
            "subject",
            "body_html",
            "body_text",
            "variables",
            "category"
        ]
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Missing required field: {field}")
            
        # Validate template variables
        self._validate_template_variables(
            template_data["subject"],
            template_data["variables"]
        )
        self._validate_template_variables(
            template_data["body_html"],
            template_data["variables"]
        )
        self._validate_template_variables(
            template_data["body_text"],
            template_data["variables"]
        )
