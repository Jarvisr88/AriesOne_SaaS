"""Integration tests for company API."""
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.company import Company

def test_create_company(test_client: TestClient, auth_headers: dict):
    """Test company creation endpoint."""
    # Arrange
    company_data = {
        "name": "API Test Company",
        "npi": "6666666666",
        "tax_id": "66-6666666",
        "is_active": True
    }
    
    # Act
    response = test_client.post(
        "/companies/",
        json=company_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == company_data["name"]
    assert data["npi"] == company_data["npi"]
    assert "id" in data

def test_get_company(
    test_client: TestClient,
    test_session: AsyncSession,
    auth_headers: dict
):
    """Test get company endpoint."""
    # Arrange
    company = Company(
        name="Company to Get",
        npi="7777777777",
        tax_id="77-7777777",
        is_active=True
    )
    test_session.add(company)
    test_session.commit()
    
    # Act
    response = test_client.get(
        f"/companies/{company.id}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(company.id)
    assert data["name"] == company.name

def test_list_companies(
    test_client: TestClient,
    test_session: AsyncSession,
    auth_headers: dict
):
    """Test list companies endpoint."""
    # Arrange
    companies = [
        Company(
            name="List Company 1",
            npi="8888888888",
            tax_id="88-8888888",
            is_active=True
        ),
        Company(
            name="List Company 2",
            npi="9999999999",
            tax_id="99-9999999",
            is_active=True
        )
    ]
    
    for company in companies:
        test_session.add(company)
    test_session.commit()
    
    # Act
    response = test_client.get("/companies/", headers=auth_headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert all(c["is_active"] for c in data)

def test_update_company(
    test_client: TestClient,
    test_session: AsyncSession,
    auth_headers: dict
):
    """Test update company endpoint."""
    # Arrange
    company = Company(
        name="Original API Name",
        npi="1010101010",
        tax_id="10-1010101",
        is_active=True
    )
    test_session.add(company)
    test_session.commit()
    
    update_data = {
        "name": "Updated API Name"
    }
    
    # Act
    response = test_client.put(
        f"/companies/{company.id}",
        json=update_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]

def test_delete_company(
    test_client: TestClient,
    test_session: AsyncSession,
    auth_headers: dict
):
    """Test delete company endpoint."""
    # Arrange
    company = Company(
        name="Company to Delete",
        npi="1212121212",
        tax_id="12-1212121",
        is_active=True
    )
    test_session.add(company)
    test_session.commit()
    
    # Act
    response = test_client.delete(
        f"/companies/{company.id}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 204
    
    # Verify soft delete
    test_session.refresh(company)
    assert company.is_deleted is True

def test_get_nonexistent_company(
    test_client: TestClient,
    auth_headers: dict
):
    """Test getting nonexistent company."""
    # Arrange
    random_id = uuid.uuid4()
    
    # Act
    response = test_client.get(
        f"/companies/{random_id}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 404
