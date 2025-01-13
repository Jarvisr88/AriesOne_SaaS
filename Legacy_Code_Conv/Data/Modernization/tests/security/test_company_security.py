"""Security tests for company operations."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.company import Company
from core.security.encryption import EncryptionService, EncryptionSettings

def test_unauthorized_access(test_client: TestClient):
    """Test unauthorized access to company endpoints."""
    # Test without auth header
    response = test_client.get("/companies/")
    assert response.status_code == 401
    
    # Test with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_client.get("/companies/", headers=headers)
    assert response.status_code == 401

def test_sql_injection_protection(
    test_client: TestClient,
    auth_headers: dict
):
    """Test SQL injection protection."""
    # Test with SQL injection in company name
    company_data = {
        "name": "Company'; DROP TABLE companies; --",
        "npi": "1234567890",
        "tax_id": "12-3456789",
        "is_active": True
    }
    
    response = test_client.post(
        "/companies/",
        json=company_data,
        headers=auth_headers
    )
    
    # Should still create company with exact name
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == company_data["name"]

@pytest.mark.asyncio
async def test_sensitive_data_encryption(
    test_session: AsyncSession
):
    """Test encryption of sensitive company data."""
    # Arrange
    encryption_service = EncryptionService(
        EncryptionSettings(SECRET_KEY="test_key")
    )
    
    tax_id = "12-3456789"
    company = Company(
        name="Encryption Test Company",
        npi="1234567890",
        tax_id=encryption_service.encrypt(tax_id),
        is_active=True
    )
    
    # Act
    test_session.add(company)
    await test_session.commit()
    
    # Assert
    # Raw database value should be encrypted
    await test_session.refresh(company)
    assert company.tax_id != tax_id
    
    # Decrypted value should match original
    decrypted = encryption_service.decrypt(company.tax_id)
    assert decrypted == tax_id

def test_rate_limiting(test_client: TestClient, auth_headers: dict):
    """Test rate limiting on company endpoints."""
    # Make multiple rapid requests
    for _ in range(10):
        response = test_client.get(
            "/companies/",
            headers=auth_headers
        )
    
    # Last request should be rate limited
    response = test_client.get(
        "/companies/",
        headers=auth_headers
    )
    assert response.status_code == 429

@pytest.mark.asyncio
async def test_audit_logging(
    test_client: TestClient,
    test_session: AsyncSession,
    auth_headers: dict
):
    """Test audit logging for company operations."""
    # Create company
    company_data = {
        "name": "Audit Test Company",
        "npi": "1234567890",
        "tax_id": "12-3456789",
        "is_active": True
    }
    
    response = test_client.post(
        "/companies/",
        json=company_data,
        headers=auth_headers
    )
    
    company_id = response.json()["id"]
    
    # Verify audit log entry
    audit_log = await test_session.execute(
        "SELECT * FROM audit_events WHERE entity_id = :id",
        {"id": company_id}
    )
    log_entry = audit_log.first()
    
    assert log_entry is not None
    assert log_entry.event_type == "CREATE"
    assert log_entry.entity_type == "company"
