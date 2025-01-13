"""
Integration tests for eligibility verification.
"""
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest_asyncio

from ability.services.payer_interface import EligibilityRequest
from ability.main import app
from ability.config import Settings


@pytest.fixture
def test_settings():
    """Test settings fixture."""
    return Settings(
        medicare_hets_url="http://test-hets.medicare.gov",
        medicaid_portal_url="http://test-portal.medicaid.gov",
        private_payer_url="http://test-api.private-payer.com",
        test_mode=True
    )

@pytest_asyncio.fixture
async def test_client():
    """Test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_medicare_eligibility(test_client, test_settings):
    """Test Medicare eligibility verification."""
    request = EligibilityRequest(
        subscriber_id="123456789A",
        provider_npi="1234567890",
        service_date=datetime.utcnow(),
        service_type_codes=["30"]
    )
    
    response = await test_client.post(
        "/api/v1/eligibility/medicare",
        json=request.dict()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "is_eligible" in data
    assert "coverage_status" in data
    assert "plan_info" in data

@pytest.mark.asyncio
async def test_medicaid_eligibility(test_client, test_settings):
    """Test Medicaid eligibility verification."""
    request = EligibilityRequest(
        subscriber_id="987654321B",
        provider_npi="1234567890",
        service_date=datetime.utcnow(),
        service_type_codes=["30"]
    )
    
    response = await test_client.post(
        "/api/v1/eligibility/medicaid",
        json=request.dict()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "is_eligible" in data
    assert "coverage_status" in data
    assert "plan_info" in data

@pytest.mark.asyncio
async def test_private_payer_eligibility(test_client, test_settings):
    """Test private payer eligibility verification."""
    request = EligibilityRequest(
        subscriber_id="555555555C",
        provider_npi="1234567890",
        service_date=datetime.utcnow(),
        service_type_codes=["30"]
    )
    
    response = await test_client.post(
        "/api/v1/eligibility/private/BCBS",
        json=request.dict()
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "is_eligible" in data
    assert "coverage_status" in data
    assert "plan_info" in data

@pytest.mark.asyncio
async def test_invalid_medicare_request(test_client, test_settings):
    """Test invalid Medicare request handling."""
    request = EligibilityRequest(
        subscriber_id="invalid",
        provider_npi="1234567890",
        service_date=datetime.utcnow(),
        service_type_codes=["30"]
    )
    
    response = await test_client.post(
        "/api/v1/eligibility/medicare",
        json=request.dict()
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_service_unavailable(test_client, test_settings):
    """Test service unavailability handling."""
    request = EligibilityRequest(
        subscriber_id="123456789A",
        provider_npi="1234567890",
        service_date=datetime.utcnow(),
        service_type_codes=["30"]
    )
    
    # Simulate service being down
    test_settings.medicare_hets_url = "http://invalid-url"
    
    response = await test_client.post(
        "/api/v1/eligibility/medicare",
        json=request.dict()
    )
    
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
