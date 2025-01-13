"""
Alert configuration and management.
"""
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class AlertRule(BaseModel):
    """Alert rule configuration."""
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    metric: str = Field(..., description="Metric to monitor")
    condition: str = Field(..., description="Alert condition")
    threshold: float = Field(..., description="Alert threshold")
    severity: AlertSeverity = Field(
        ...,
        description="Alert severity"
    )
    interval: int = Field(
        ...,
        description="Check interval in seconds"
    )
    enabled: bool = Field(
        True,
        description="Whether rule is enabled"
    )


class Alert(BaseModel):
    """Alert instance."""
    rule_name: str = Field(..., description="Rule name")
    severity: AlertSeverity = Field(
        ...,
        description="Alert severity"
    )
    message: str = Field(..., description="Alert message")
    value: float = Field(..., description="Current value")
    threshold: float = Field(..., description="Alert threshold")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Alert timestamp"
    )


class AlertManager:
    """Manager for alert rules and notifications."""

    def __init__(self):
        """Initialize manager."""
        self.rules: Dict[str, AlertRule] = {}
        self.handlers: Dict[
            AlertSeverity,
            List[Callable[[Alert], None]]
        ] = {
            severity: []
            for severity in AlertSeverity
        }

    def add_rule(self, rule: AlertRule):
        """Add alert rule.
        
        Args:
            rule: Alert rule
        """
        self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str):
        """Remove alert rule.
        
        Args:
            rule_name: Rule name
        """
        self.rules.pop(rule_name, None)

    def add_handler(
        self,
        severity: AlertSeverity,
        handler: Callable[[Alert], None]
    ):
        """Add alert handler.
        
        Args:
            severity: Alert severity
            handler: Handler function
        """
        self.handlers[severity].append(handler)

    def check_condition(
        self,
        rule: AlertRule,
        value: float
    ) -> bool:
        """Check if alert condition is met.
        
        Args:
            rule: Alert rule
            value: Current value
            
        Returns:
            True if condition met
        """
        if rule.condition == ">":
            return value > rule.threshold
        elif rule.condition == ">=":
            return value >= rule.threshold
        elif rule.condition == "<":
            return value < rule.threshold
        elif rule.condition == "<=":
            return value <= rule.threshold
        elif rule.condition == "==":
            return value == rule.threshold
        return False

    def trigger_alert(
        self,
        rule: AlertRule,
        value: float
    ):
        """Trigger alert for rule.
        
        Args:
            rule: Alert rule
            value: Current value
        """
        alert = Alert(
            rule_name=rule.name,
            severity=rule.severity,
            message=rule.description,
            value=value,
            threshold=rule.threshold
        )
        
        # Notify handlers
        for handler in self.handlers[rule.severity]:
            try:
                handler(alert)
            except Exception as e:
                print(
                    f"Alert handler error: {str(e)}"
                )

    async def check_rules(
        self,
        metrics: Dict[str, float]
    ):
        """Check all alert rules.
        
        Args:
            metrics: Current metric values
        """
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            value = metrics.get(rule.metric)
            if value is None:
                continue
                
            if self.check_condition(rule, value):
                self.trigger_alert(rule, value)
