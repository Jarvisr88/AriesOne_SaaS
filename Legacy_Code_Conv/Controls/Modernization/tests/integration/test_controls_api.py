import pytest
from fastapi.testclient import TestClient
from ....api.controls_routes import router
from ....models.address import Address
from ....models.name import Name
from ....services.map_service import MapService

@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def valid_address():
    return {
        "address1": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "zip_code": "62701"
    }

@pytest.fixture
def valid_name():
    return {
        "courtesy": "Dr.",
        "first_name": "John",
        "middle_name": "William",
        "last_name": "Doe",
        "suffix": "Jr."
    }

def test_validate_address(client, valid_address):
    """Test address validation endpoint"""
    response = client.post("/controls/address/validate", json=valid_address)
    assert response.status_code == 200
    assert response.json() == {"valid": True}

def test_validate_invalid_address(client):
    """Test validation of invalid address"""
    invalid_address = {
        "address1": "123 Main St",
        "city": "Springfield",
        "state": "Invalid",  # Invalid state
        "zip_code": "62701"
    }
    response = client.post("/controls/address/validate", json=invalid_address)
    assert response.status_code == 400

def test_geocode_address(client, valid_address):
    """Test address geocoding endpoint"""
    response = client.post(
        "/controls/address/geocode",
        params={"provider": "google"},
        json=valid_address
    )
    assert response.status_code == 200
    data = response.json()
    assert "latitude" in data
    assert "longitude" in data

def test_list_map_providers(client):
    """Test listing map providers endpoint"""
    response = client.get("/controls/map/providers")
    assert response.status_code == 200
    providers = response.json()
    assert isinstance(providers, list)
    assert "google" in providers

def test_format_name_full(client, valid_name):
    """Test name formatting endpoint - full format"""
    response = client.post(
        "/controls/name/format",
        params={"format_type": "full"},
        json=valid_name
    )
    assert response.status_code == 200
    assert response.json() == {
        "formatted": "Dr. John William Doe Jr."
    }

def test_format_name_formal(client, valid_name):
    """Test name formatting endpoint - formal format"""
    response = client.post(
        "/controls/name/format",
        params={"format_type": "formal"},
        json=valid_name
    )
    assert response.status_code == 200
    assert response.json() == {
        "formatted": "Doe, Dr. John W. Jr."
    }

def test_invalid_name_format(client, valid_name):
    """Test invalid name format type"""
    response = client.post(
        "/controls/name/format",
        params={"format_type": "invalid"},
        json=valid_name
    )
    assert response.status_code == 400

def test_invalid_json(client):
    """Test handling of invalid JSON"""
    response = client.post(
        "/controls/address/validate",
        json={"invalid": "data"}
    )
    assert response.status_code == 422
