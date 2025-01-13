"""
Monitoring Tests
Version: 1.0.0
Last Updated: 2025-01-10
"""
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from prometheus_client import REGISTRY
from sqlalchemy.ext.asyncio import AsyncSession

from core.monitoring import (Alert, AlertChannel, AlertManager, AlertSeverity,
                           HealthCheck, MetricsCollector, track_db_metrics,
                           track_request_metrics)
from core.utils.config import get_settings

settings = get_settings()


# Metrics Tests
@pytest.mark.asyncio
async def test_request_metrics():
    """Test request metrics tracking."""
    @track_request_metrics("GET", "/test")
    async def test_endpoint():
        return "success"
    
    # Execute endpoint
    result = await test_endpoint()
    assert result == "success"
    
    # Verify metrics
    for metric in REGISTRY.get_sample_value(
        'request_latency_seconds_count',
        {'method': 'GET', 'endpoint': '/test'}
    ):
        assert metric > 0
    
    for metric in REGISTRY.get_sample_value(
        'request_count_total',
        {'method': 'GET', 'endpoint': '/test', 'status': 'success'}
    ):
        assert metric > 0


@pytest.mark.asyncio
async def test_db_metrics():
    """Test database metrics tracking."""
    @track_db_metrics("select", "test_table")
    async def test_query():
        await asyncio.sleep(0.1)  # Simulate query execution
        return "result"
    
    # Execute query
    result = await test_query()
    assert result == "result"
    
    # Verify metrics
    for metric in REGISTRY.get_sample_value(
        'db_query_latency_seconds_count',
        {'operation': 'select', 'table': 'test_table'}
    ):
        assert metric > 0


def test_metrics_collector():
    """Test metrics collector functionality."""
    collector = MetricsCollector()
    
    # Test cache metrics
    collector.record_cache_operation("test_cache", True)
    collector.record_cache_operation("test_cache", False)
    
    # Test active users
    collector.update_active_users(10)
    
    # Test resource usage
    collector.update_resource_usage(1024 * 1024, 50.0)
    
    # Test DB pool stats
    collector.update_db_pool_stats(5, 3, 0)
    
    # Get current metrics
    metrics = collector.get_current_metrics()
    assert "request_metrics" in metrics
    assert "database_metrics" in metrics
    assert "cache_metrics" in metrics
    assert "business_metrics" in metrics
    assert "resource_metrics" in metrics
    assert "timestamp" in metrics


# Health Check Tests
@pytest.mark.asyncio
async def test_health_check():
    """Test health check functionality."""
    # Mock session
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=AsyncMock(
        scalar_one=AsyncMock(return_value=1)
    ))
    
    health_check = HealthCheck(mock_session)
    
    # Test database health
    db_health = await health_check.check_database()
    assert db_health["status"] == "healthy"
    
    # Test cache health
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        cache_health = await health_check.check_cache()
        assert cache_health["status"] == "healthy"
    
    # Test event bus health
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        event_health = await health_check.check_event_bus()
        assert event_health["status"] == "healthy"
    
    # Test all components
    all_health = await health_check.check_all(use_cache=False)
    assert all_health["database"]["status"] == "healthy"
    assert all_health["cache"]["status"] == "healthy"
    assert all_health["event_bus"]["status"] == "healthy"
    assert "timestamp" in all_health


# Alert Tests
@pytest.mark.asyncio
async def test_alert_manager():
    """Test alert management functionality."""
    manager = AlertManager()
    
    # Create alert
    alert = await manager.create_alert(
        title="Test Alert",
        message="Test message",
        severity=AlertSeverity.WARNING,
        source="test",
        channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
    )
    
    assert alert.id in manager._active_alerts
    assert alert.title == "Test Alert"
    assert alert.severity == AlertSeverity.WARNING
    assert not alert.acknowledged
    
    # Get active alerts
    active_alerts = manager.get_active_alerts()
    assert len(active_alerts) == 1
    assert active_alerts[0].id == alert.id
    
    # Filter by severity
    warning_alerts = manager.get_active_alerts(AlertSeverity.WARNING)
    assert len(warning_alerts) == 1
    error_alerts = manager.get_active_alerts(AlertSeverity.ERROR)
    assert len(error_alerts) == 0
    
    # Acknowledge alert
    acknowledged = await manager.acknowledge_alert(alert.id, "test_user")
    assert acknowledged is not None
    assert acknowledged.acknowledged
    assert acknowledged.acknowledged_by == "test_user"
    assert acknowledged.acknowledged_at is not None
    
    # Verify alert moved to history
    assert alert.id not in manager._active_alerts
    assert len(manager.get_alert_history()) == 1


@pytest.mark.asyncio
async def test_alert_notifications():
    """Test alert notifications."""
    manager = AlertManager()
    
    # Mock notification methods
    manager._send_email_alert = AsyncMock()
    manager._send_slack_alert = AsyncMock()
    manager._send_webhook_alert = AsyncMock()
    manager._send_sms_alert = AsyncMock()
    
    # Create alert with all channels
    alert = await manager.create_alert(
        title="Test Alert",
        message="Test message",
        severity=AlertSeverity.ERROR,
        source="test",
        channels=[
            AlertChannel.EMAIL,
            AlertChannel.SLACK,
            AlertChannel.WEBHOOK,
            AlertChannel.SMS
        ]
    )
    
    # Verify all notification methods were called
    manager._send_email_alert.assert_called_once_with(alert)
    manager._send_slack_alert.assert_called_once_with(alert)
    manager._send_webhook_alert.assert_called_once_with(alert)
    manager._send_sms_alert.assert_called_once_with(alert)
