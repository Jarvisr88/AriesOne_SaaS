from typing import Dict, List, Optional
from datetime import datetime
import json
import jwt
import re
from urllib.parse import urlparse, parse_qs
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.mobile import (
    DeepLink,
    AppLink,
    LinkAnalytics,
    LinkTemplate
)

class DeepLinkingService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.app_scheme = settings.APP_SCHEME
        self.web_domain = settings.WEB_DOMAIN
        self.link_ttl = 86400  # 24 hours
        self.supported_platforms = ["ios", "android", "web"]

    async def create_deep_link(
        self,
        link_data: Dict,
        user_id: Optional[str] = None
    ) -> Dict:
        """Create deep link"""
        try:
            # Validate link data
            self._validate_link_data(link_data)
            
            # Get or create template
            template = await self._get_template(
                link_data["type"],
                link_data.get("template_id")
            )
            
            # Generate link token
            token = self._generate_token(link_data)
            
            # Create link record
            deep_link = await DeepLink.create(
                user_id=user_id,
                type=link_data["type"],
                template_id=template.id if template else None,
                data=link_data["data"],
                token=token,
                expires_at=datetime.now().timestamp() + self.link_ttl,
                is_active=True,
                created_at=datetime.now()
            )
            
            # Generate platform-specific links
            links = await self._generate_platform_links(
                deep_link,
                template
            )
            
            return {
                "status": "created",
                "link_id": str(deep_link.id),
                "links": links,
                "expires_at": deep_link.expires_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Deep link creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def resolve_link(
        self,
        token: str,
        platform: str,
        device_info: Optional[Dict] = None
    ) -> Dict:
        """Resolve deep link"""
        try:
            # Validate platform
            if platform not in self.supported_platforms:
                raise ValueError(f"Unsupported platform: {platform}")
            
            # Decode token
            try:
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=["HS256"]
                )
            except jwt.ExpiredSignatureError:
                raise ValueError("Link expired")
            except jwt.InvalidTokenError:
                raise ValueError("Invalid link")
            
            # Get link
            link = await DeepLink.get(id=payload["link_id"])
            if not link or not link.is_active:
                raise ValueError("Link not found or inactive")
            
            # Log analytics
            await self._log_analytics(
                link.id,
                platform,
                device_info
            )
            
            # Get template
            template = None
            if link.template_id:
                template = await LinkTemplate.get(id=link.template_id)
            
            # Generate response
            response = await self._generate_response(
                link,
                template,
                platform
            )
            
            return response
        except Exception as e:
            logger.error(f"Link resolution failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    async def create_template(
        self,
        template_data: Dict
    ) -> Dict:
        """Create link template"""
        try:
            # Validate template data
            self._validate_template_data(template_data)
            
            # Create template
            template = await LinkTemplate.create(
                name=template_data["name"],
                type=template_data["type"],
                patterns=template_data["patterns"],
                fallback_url=template_data.get("fallback_url"),
                metadata=template_data.get("metadata", {}),
                created_at=datetime.now()
            )
            
            return {
                "status": "created",
                "template_id": str(template.id)
            }
        except Exception as e:
            logger.error(f"Template creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_analytics(
        self,
        link_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get link analytics"""
        try:
            # Get link
            link = await DeepLink.get(id=link_id)
            if not link:
                raise ValueError("Link not found")
            
            # Build query
            query = LinkAnalytics.filter(link_id=link_id)
            if start_date:
                query = query.filter(created_at__gte=start_date)
            if end_date:
                query = query.filter(created_at__lte=end_date)
            
            # Get analytics
            analytics = await query.all()
            
            # Process analytics
            result = {
                "total_clicks": len(analytics),
                "platforms": {},
                "devices": {},
                "timeline": []
            }
            
            for record in analytics:
                # Platform stats
                platform = record.platform
                result["platforms"][platform] = result["platforms"].get(
                    platform,
                    0
                ) + 1
                
                # Device stats
                if record.device_info:
                    device = record.device_info.get("model", "unknown")
                    result["devices"][device] = result["devices"].get(
                        device,
                        0
                    ) + 1
                
                # Timeline
                result["timeline"].append({
                    "timestamp": record.created_at.isoformat(),
                    "platform": platform,
                    "device_info": record.device_info
                })
            
            return result
        except Exception as e:
            logger.error(f"Analytics retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _validate_link_data(self, link_data: Dict) -> None:
        """Validate deep link data"""
        required_fields = ["type", "data"]
        for field in required_fields:
            if field not in link_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(link_data["data"], dict):
            raise ValueError("Link data must be a dictionary")

    def _validate_template_data(self, template_data: Dict) -> None:
        """Validate template data"""
        required_fields = ["name", "type", "patterns"]
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(template_data["patterns"], dict):
            raise ValueError("Template patterns must be a dictionary")
        
        for platform, pattern in template_data["patterns"].items():
            if platform not in self.supported_platforms:
                raise ValueError(f"Unsupported platform: {platform}")
            if not isinstance(pattern, str):
                raise ValueError("Pattern must be a string")

    def _generate_token(self, link_data: Dict) -> str:
        """Generate link token"""
        payload = {
            "type": link_data["type"],
            "data": link_data["data"],
            "exp": datetime.now().timestamp() + self.link_ttl
        }
        return jwt.encode(
            payload,
            self.jwt_secret,
            algorithm="HS256"
        )

    async def _get_template(
        self,
        link_type: str,
        template_id: Optional[str] = None
    ) -> Optional[LinkTemplate]:
        """Get link template"""
        if template_id:
            template = await LinkTemplate.get(id=template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            return template
        
        # Find default template for type
        return await LinkTemplate.filter(
            type=link_type,
            is_default=True
        ).first()

    async def _generate_platform_links(
        self,
        link: DeepLink,
        template: Optional[LinkTemplate]
    ) -> Dict:
        """Generate platform-specific links"""
        links = {}
        
        for platform in self.supported_platforms:
            if template and platform in template.patterns:
                # Use template pattern
                pattern = template.patterns[platform]
                links[platform] = self._apply_pattern(
                    pattern,
                    link.data,
                    link.token
                )
            else:
                # Use default pattern
                if platform == "web":
                    links[platform] = f"https://{self.web_domain}/link/{link.token}"
                else:
                    links[platform] = f"{self.app_scheme}://{platform}/link/{link.token}"
        
        return links

    def _apply_pattern(
        self,
        pattern: str,
        data: Dict,
        token: str
    ) -> str:
        """Apply template pattern"""
        result = pattern
        
        # Replace data placeholders
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        # Add token
        result = result.replace("{token}", token)
        
        return result

    async def _generate_response(
        self,
        link: DeepLink,
        template: Optional[LinkTemplate],
        platform: str
    ) -> Dict:
        """Generate link resolution response"""
        response = {
            "type": link.type,
            "data": link.data
        }
        
        # Add template-specific data
        if template and template.metadata:
            response["metadata"] = template.metadata
        
        # Add fallback URL
        if template and template.fallback_url:
            response["fallback_url"] = template.fallback_url
        
        return response

    async def _log_analytics(
        self,
        link_id: str,
        platform: str,
        device_info: Optional[Dict]
    ) -> None:
        """Log link analytics"""
        await LinkAnalytics.create(
            link_id=link_id,
            platform=platform,
            device_info=device_info or {},
            created_at=datetime.now()
        )
