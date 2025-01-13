import pytest
from datetime import datetime, date
from pathlib import Path
import json
from integration.reporting_system import (
    ReportingSystemIntegration,
    ReportFormat,
    ReportType,
    ReportSchedule,
    ReportDeliveryMethod
)
from unittest.mock import AsyncMock, patch

@pytest.fixture
def reporting_system():
    """Create a test instance of ReportingSystemIntegration"""
    return ReportingSystemIntegration(
        db_url="postgresql://test:test@localhost/test_db",
        report_engine_url="https://test.reporting.com/v1",
        api_key="test-api-key"
    )

@pytest.fixture
def sample_report_config():
    """Create a sample report configuration for testing"""
    return {
        "report_type": ReportType.BILLING_SUMMARY,
        "format": ReportFormat.PDF,
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 12, 31),
        "filters": {
            "provider_id": "PR67890",
            "status": "completed"
        },
        "schedule": ReportSchedule.MONTHLY,
        "delivery_method": ReportDeliveryMethod.EMAIL,
        "recipients": ["user@example.com"]
    }

@pytest.mark.asyncio
async def test_generate_report(reporting_system, sample_report_config):
    """Test generating a new report"""
    # Mock report generation API call
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "report_id": "REP123",
            "status": "generating"
        }

        # Generate report
        result = await reporting_system.generate_report(**sample_report_config)

        # Verify result
        assert result["status"] == "success"
        assert "report_id" in result
        assert result["report_id"] == "REP123"

@pytest.mark.asyncio
async def test_get_report_status(reporting_system):
    """Test checking report generation status"""
    report_id = "REP123"

    # Mock status check API call
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "status": "completed",
            "download_url": "https://test.reporting.com/reports/REP123.pdf"
        }

        # Check status
        status = await reporting_system.get_report_status(report_id)

        # Verify result
        assert status["status"] == "completed"
        assert "download_url" in status

@pytest.mark.asyncio
async def test_schedule_report(reporting_system, sample_report_config):
    """Test scheduling a recurring report"""
    # Mock schedule API call
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "schedule_id": "SCH123",
            "status": "active"
        }

        # Schedule report
        result = await reporting_system.schedule_report(**sample_report_config)

        # Verify result
        assert result["status"] == "success"
        assert "schedule_id" in result
        assert result["schedule_id"] == "SCH123"

@pytest.mark.asyncio
async def test_cancel_scheduled_report(reporting_system):
    """Test canceling a scheduled report"""
    schedule_id = "SCH123"

    # Mock cancellation API call
    with patch("httpx.AsyncClient.delete") as mock_delete:
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = {
            "status": "cancelled"
        }

        # Cancel schedule
        result = await reporting_system.cancel_scheduled_report(schedule_id)

        # Verify result
        assert result["status"] == "success"
        assert "Schedule cancelled successfully" in result["message"]

@pytest.mark.asyncio
async def test_download_report(reporting_system):
    """Test downloading a generated report"""
    report_id = "REP123"
    download_path = Path("/tmp/test_report.pdf")

    # Mock download API call
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"test report content"

        # Download report
        result = await reporting_system.download_report(report_id, download_path)

        # Verify result
        assert result["status"] == "success"
        assert download_path.exists()
        assert download_path.stat().st_size > 0

@pytest.mark.asyncio
async def test_list_scheduled_reports(reporting_system):
    """Test listing all scheduled reports"""
    # Mock API call
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "schedules": [
                {
                    "schedule_id": "SCH123",
                    "report_type": ReportType.BILLING_SUMMARY,
                    "schedule": ReportSchedule.MONTHLY,
                    "status": "active"
                }
            ]
        }

        # List schedules
        schedules = await reporting_system.list_scheduled_reports()

        # Verify result
        assert isinstance(schedules, list)
        assert len(schedules) > 0
        for schedule in schedules:
            assert "schedule_id" in schedule
            assert "report_type" in schedule
            assert "schedule" in schedule
            assert "status" in schedule

@pytest.mark.asyncio
async def test_error_handling(reporting_system, sample_report_config):
    """Test error handling in reporting operations"""
    # Test API error
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            await reporting_system.generate_report(**sample_report_config)
        assert "API Error" in str(exc_info.value)

    # Test invalid report configuration
    invalid_config = sample_report_config.copy()
    invalid_config["format"] = "INVALID_FORMAT"

    with pytest.raises(Exception) as exc_info:
        await reporting_system.generate_report(**invalid_config)
    assert "validation" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_report_formats(reporting_system, sample_report_config):
    """Test generating reports in different formats"""
    formats = [ReportFormat.PDF, ReportFormat.CSV, ReportFormat.EXCEL, ReportFormat.JSON]
    
    for format in formats:
        config = sample_report_config.copy()
        config["format"] = format

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "report_id": f"REP123_{format}",
                "status": "generating"
            }

            result = await reporting_system.generate_report(**config)
            assert result["status"] == "success"
            assert format.value in result["report_id"]

@pytest.mark.asyncio
async def test_delivery_methods(reporting_system, sample_report_config):
    """Test different report delivery methods"""
    delivery_methods = [
        (ReportDeliveryMethod.EMAIL, ["user@example.com"]),
        (ReportDeliveryMethod.FTP, {"host": "ftp.example.com", "path": "/reports"}),
        (ReportDeliveryMethod.API_CALLBACK, {"url": "https://api.example.com/webhook"})
    ]

    for method, config in delivery_methods:
        report_config = sample_report_config.copy()
        report_config["delivery_method"] = method
        report_config["delivery_config"] = config

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "report_id": "REP123",
                "status": "generating",
                "delivery": {"method": method.value, "config": config}
            }

            result = await reporting_system.generate_report(**report_config)
            assert result["status"] == "success"
            assert "delivery" in result

if __name__ == "__main__":
    pytest.main([__file__])
