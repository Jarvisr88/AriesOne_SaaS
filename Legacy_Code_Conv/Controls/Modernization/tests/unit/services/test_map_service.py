import pytest
from unittest.mock import AsyncMock, patch
from ....services.map_service import MapService, GoogleMapsProvider
from ....models.address import Address

@pytest.fixture
def address():
    return Address(
        address1="123 Main St",
        city="Springfield",
        state="IL",
        zip_code="62701"
    )

@pytest.fixture
def map_service():
    service = MapService()
    provider = GoogleMapsProvider(api_key="test_key")
    service.register_provider("google", provider)
    return service

@pytest.mark.asyncio
async def test_geocode_success(address, map_service):
    """Test successful geocoding"""
    provider = map_service.get_provider("google")
    
    # Mock the geocoding response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "status": "OK",
        "results": [{
            "geometry": {
                "location": {
                    "lat": 39.78,
                    "lng": -89.65
                }
            }
        }]
    })
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        coords = await provider.geocode(address)
        assert coords["latitude"] == 39.78
        assert coords["longitude"] == -89.65

@pytest.mark.asyncio
async def test_geocode_failure(address, map_service):
    """Test geocoding failure"""
    provider = map_service.get_provider("google")
    
    # Mock failed response
    mock_response = AsyncMock()
    mock_response.status = 400
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        with pytest.raises(Exception):
            await provider.geocode(address)

@pytest.mark.asyncio
async def test_validate_address_success(address, map_service):
    """Test successful address validation"""
    provider = map_service.get_provider("google")
    
    # Mock successful validation
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "status": "OK",
        "results": [{"geometry": {"location": {}}}]
    })
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        is_valid = await provider.validate_address(address)
        assert is_valid is True

@pytest.mark.asyncio
async def test_validate_address_failure(address, map_service):
    """Test failed address validation"""
    provider = map_service.get_provider("google")
    
    # Mock failed validation
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "status": "ZERO_RESULTS"
    })
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        is_valid = await provider.validate_address(address)
        assert is_valid is False

def test_map_service_providers(map_service):
    """Test map service provider management"""
    # Test getting registered provider
    provider = map_service.get_provider("google")
    assert isinstance(provider, GoogleMapsProvider)
    
    # Test getting providers list
    providers = map_service.get_providers()
    assert "google" in providers
    
    # Test invalid provider
    with pytest.raises(ValueError):
        map_service.get_provider("invalid")
