"""
Core Alerts Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides alerting functionality.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

from ..utils.config import get_settings
from ..utils.logging import CoreLogger

settings = get_settings()
logger = CoreLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"


class Alert:
    """Alert model."""
    
    def __init__(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        source: str,
        channels: List[AlertChannel],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize alert."""
        self.id = str(hash(f"{title}{datetime.utcnow().isoformat()}"))
        self.title = title
        self.message = message
        self.severity = severity
        self.source = source
        self.channels = channels
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        self.acknowledged = False
        self.acknowledged_by: Optional[str] = None
        self.acknowledged_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source,
            "channels": [c.value for c in self.channels],
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat()
            if self.acknowledged_at else None
        }


class AlertManager:
    """Alert management service."""
    
    def __init__(self):
        """Initialize alert manager."""
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
    
    async def create_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        source: str,
        channels: List[AlertChannel],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """Create and send new alert."""
        alert = Alert(title, message, severity, source, channels, metadata)
        self._active_alerts[alert.id] = alert
        
        # Send notifications
        await self._notify_channels(alert)
        
        return alert
    
    async def acknowledge_alert(self, alert_id: str,
                              acknowledged_by: str) -> Optional[Alert]:
        """Acknowledge an active alert."""
        if alert_id not in self._active_alerts:
            return None
        
        alert = self._active_alerts[alert_id]
        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow()
        
        # Move to history
        self._alert_history.append(alert)
        del self._active_alerts[alert_id]
        
        return alert
    
    def get_active_alerts(self,
                         severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity."""
        alerts = list(self._active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_history(self,
                         limit: Optional[int] = None) -> List[Alert]:
        """Get alert history, optionally limited."""
        alerts = sorted(self._alert_history,
                       key=lambda x: x.timestamp,
                       reverse=True)
        return alerts[:limit] if limit else alerts
    
    async def _notify_channels(self, alert: Alert) -> None:
        """Send alert notifications to configured channels."""
        for channel in alert.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_alert(alert)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_alert(alert)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_alert(alert)
                elif channel == AlertChannel.SMS:
                    await self._send_sms_alert(alert)
            except Exception as e:
                logger.error(
                    f"Failed to send alert to {channel.value}: {str(e)}"
                )
    
    async def _send_email_alert(self, alert: Alert) -> None:
        """Send email alert."""
        # Implement email sending logic
        # Example:
        # await send_email(
        #     to=settings.ALERT_EMAIL,
        #     subject=f"[{alert.severity.value.upper()}] {alert.title}",
        #     body=alert.message
        # )
        pass
    
    async def _send_slack_alert(self, alert: Alert) -> None:
        """Send Slack alert."""
        if not settings.SLACK_WEBHOOK_URL:
            return
            
        payload = {
            "text": f"*[{alert.severity.value.upper()}] {alert.title}*\n{alert.message}",
            "attachments": [{
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in alert.metadata.items()
                ]
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(settings.SLACK_WEBHOOK_URL, json=payload)
    
    async def _send_webhook_alert(self, alert: Alert) -> None:
        """Send webhook alert."""
        if not settings.ALERT_WEBHOOK_URL:
            return
            
        async with aiohttp.ClientSession() as session:
            await session.post(
                settings.ALERT_WEBHOOK_URL,
                json=alert.to_dict()
            )
    
    async def _send_sms_alert(self, alert: Alert) -> None:
        """Send SMS alert."""
        # Implement SMS sending logic
        # Example:
        # await send_sms(
        #     to=settings.ALERT_PHONE,
        #     message=f"[{alert.severity.value.upper()}] {alert.title}"
        # )
        pass


# Global alert manager instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get alert manager instance."""
    global _alert_manager
    if not _alert_manager:
        _alert_manager = AlertManager()
    return _alert_manager
