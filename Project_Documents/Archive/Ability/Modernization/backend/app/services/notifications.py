from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger

class NotificationChannel:
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"

class NotificationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.email_config = settings.notifications.email
        self.sms_config = settings.notifications.sms
        self.push_config = settings.notifications.push
        self.slack_config = settings.notifications.slack
        self.teams_config = settings.notifications.teams

    async def send_alert(
        self,
        alert_type: str,
        priority: str,
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        Send alert through configured channels
        """
        try:
            # Get notification rules for alert type and priority
            rules = self.get_notification_rules(alert_type, priority)
            
            # Send through each configured channel
            tasks = []
            for channel in rules['channels']:
                if channel == NotificationChannel.EMAIL:
                    tasks.append(self.send_email_alert(
                        rules['recipients']['email'],
                        message,
                        metadata
                    ))
                elif channel == NotificationChannel.SMS:
                    tasks.append(self.send_sms_alert(
                        rules['recipients']['sms'],
                        message,
                        metadata
                    ))
                elif channel == NotificationChannel.PUSH:
                    tasks.append(self.send_push_notification(
                        rules['recipients']['push'],
                        message,
                        metadata
                    ))
                elif channel == NotificationChannel.SLACK:
                    tasks.append(self.send_slack_alert(
                        rules['recipients']['slack'],
                        message,
                        metadata
                    ))
                elif channel == NotificationChannel.TEAMS:
                    tasks.append(self.send_teams_alert(
                        rules['recipients']['teams'],
                        message,
                        metadata
                    ))

            # Wait for all notifications to be sent
            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error sending alert: {str(e)}"
            )

    def get_notification_rules(
        self,
        alert_type: str,
        priority: str
    ) -> Dict:
        """
        Get notification rules based on alert type and priority
        """
        # Get base rules
        rules = self.settings.notifications.rules.get(alert_type, {})
        
        # Override with priority-specific rules
        priority_rules = rules.get(priority, {})
        
        # Merge with default rules
        default_rules = self.settings.notifications.default_rules
        
        return {
            'channels': priority_rules.get('channels', rules.get('channels', default_rules['channels'])),
            'recipients': {
                'email': priority_rules.get('email_recipients', rules.get('email_recipients', default_rules['email_recipients'])),
                'sms': priority_rules.get('sms_recipients', rules.get('sms_recipients', default_rules['sms_recipients'])),
                'push': priority_rules.get('push_recipients', rules.get('push_recipients', default_rules['push_recipients'])),
                'slack': priority_rules.get('slack_channels', rules.get('slack_channels', default_rules['slack_channels'])),
                'teams': priority_rules.get('teams_channels', rules.get('teams_channels', default_rules['teams_channels']))
            }
        }

    async def send_email_alert(
        self,
        recipients: List[str],
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        Send email alert
        """
        try:
            async with aiohttp.ClientSession() as session:
                for recipient in recipients:
                    payload = {
                        'to': recipient,
                        'subject': f"Inventory Alert: {message[:50]}...",
                        'body': self.format_email_body(message, metadata),
                        'api_key': self.email_config.api_key
                    }
                    
                    async with session.post(
                        self.email_config.api_url,
                        json=payload
                    ) as response:
                        if response.status != 200:
                            logger.error(f"Error sending email to {recipient}")

        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")

    async def send_sms_alert(
        self,
        recipients: List[str],
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        Send SMS alert
        """
        try:
            async with aiohttp.ClientSession() as session:
                for recipient in recipients:
                    payload = {
                        'to': recipient,
                        'message': self.format_sms_message(message, metadata),
                        'api_key': self.sms_config.api_key
                    }
                    
                    async with session.post(
                        self.sms_config.api_url,
                        json=payload
                    ) as response:
                        if response.status != 200:
                            logger.error(f"Error sending SMS to {recipient}")

        except Exception as e:
            logger.error(f"Error sending SMS alert: {str(e)}")

    async def send_push_notification(
        self,
        recipients: List[str],
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        Send push notification
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'recipients': recipients,
                    'message': message,
                    'data': metadata,
                    'api_key': self.push_config.api_key
                }
                
                async with session.post(
                    self.push_config.api_url,
                    json=payload
                ) as response:
                    if response.status != 200:
                        logger.error("Error sending push notification")

        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")

    async def send_slack_alert(
        self,
        channels: List[str],
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        Send Slack alert
        """
        try:
            async with aiohttp.ClientSession() as session:
                for channel in channels:
                    payload = {
                        'channel': channel,
                        'text': self.format_slack_message(message, metadata),
                        'token': self.slack_config.token
                    }
                    
                    async with session.post(
                        self.slack_config.webhook_url,
                        json=payload
                    ) as response:
                        if response.status != 200:
                            logger.error(f"Error sending Slack alert to {channel}")

        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")

    async def send_teams_alert(
        self,
        channels: List[str],
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        Send Microsoft Teams alert
        """
        try:
            async with aiohttp.ClientSession() as session:
                for channel in channels:
                    payload = {
                        'channel': channel,
                        'text': self.format_teams_message(message, metadata),
                        'token': self.teams_config.token
                    }
                    
                    async with session.post(
                        self.teams_config.webhook_url,
                        json=payload
                    ) as response:
                        if response.status != 200:
                            logger.error(f"Error sending Teams alert to {channel}")

        except Exception as e:
            logger.error(f"Error sending Teams alert: {str(e)}")

    def format_email_body(
        self,
        message: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Format email body with HTML
        """
        body = f"<h2>{message}</h2>"
        
        if metadata:
            body += "<h3>Additional Information:</h3>"
            body += "<ul>"
            for key, value in metadata.items():
                body += f"<li><strong>{key}:</strong> {value}</li>"
            body += "</ul>"
            
        return body

    def format_sms_message(
        self,
        message: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Format SMS message (limited length)
        """
        sms = f"Alert: {message}"
        
        if metadata:
            important_keys = ['alert_id', 'item_id']
            for key in important_keys:
                if key in metadata:
                    sms += f"\n{key}: {metadata[key]}"
                    
        return sms[:160]  # SMS length limit

    def format_slack_message(
        self,
        message: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Format Slack message with blocks
        """
        blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Alert:* {message}"
            }
        }]
        
        if metadata:
            fields = []
            for key, value in metadata.items():
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*{key}:* {value}"
                })
            
            blocks.append({
                "type": "section",
                "fields": fields
            })
            
        return {"blocks": blocks}

    def format_teams_message(
        self,
        message: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Format Teams message with adaptive card
        """
        card = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "body": [{
                        "type": "TextBlock",
                        "size": "medium",
                        "weight": "bolder",
                        "text": message
                    }]
                }
            }]
        }
        
        if metadata:
            facts = []
            for key, value in metadata.items():
                facts.append({
                    "title": key,
                    "value": str(value)
                })
            
            card["attachments"][0]["content"]["body"].append({
                "type": "FactSet",
                "facts": facts
            })
            
        return card
