"""
Tests for ValidationService
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock

from ...src.services.validation_service import ValidationService, ValidationError
from ...src.models.icd_codes import ICDCode

@pytest.fixture
def mock_repos():
    """Create mock repositories"""
    price_list_repo = Mock()
    parameter_repo = Mock()
    icd_code_repo = Mock()
    return price_list_repo, parameter_repo, icd_code_repo

@pytest.fixture
def service(mock_repos):
    """Create service instance with mock repos"""
    price_list_repo, parameter_repo, icd_code_repo = mock_repos
    return ValidationService(
        price_list_repo=price_list_repo,
        parameter_repo=parameter_repo,
        icd_code_repo=icd_code_repo
    )

@pytest.mark.asyncio
async def test_validate_price_update_valid(service):
    """Test validation of valid price update"""
    update_data = {
        "item_id": "TEST001",
        "base_price": "100.00",
        "currency": "USD"
    }
    
    # Should not raise any exceptions
    await service.validate_price_update(update_data)

@pytest.mark.asyncio
async def test_validate_price_update_missing_fields(service):
    """Test validation with missing required fields"""
    update_data = {
        "item_id": "TEST001"
        # Missing base_price
    }
    
    with pytest.raises(ValidationError, match="Missing required fields"):
        await service.validate_price_update(update_data)

@pytest.mark.asyncio
async def test_validate_price_update_invalid_price(service):
    """Test validation with invalid price format"""
    test_cases = [
        {"base_price": "invalid"},
        {"base_price": "-100.00"},
        {"base_price": "1000000000.00"}  # Exceeds maximum
    ]
    
    for test_case in test_cases:
        update_data = {
            "item_id": "TEST001",
            **test_case
        }
        
        with pytest.raises(ValidationError):
            await service.validate_price_update(update_data)

@pytest.mark.asyncio
async def test_validate_price_update_quantity_breaks(service):
    """Test validation of quantity breaks"""
    update_data = {
        "item_id": "TEST001",
        "base_price": "100.00",
        "currency": "USD",
        "quantity_breaks": {
            "10": "0.10",
            "20": "0.20"
        }
    }
    
    # Valid quantity breaks should not raise exception
    await service.validate_price_update(update_data)
    
    # Invalid quantity break values
    invalid_cases = [
        {"0": "0.10"},  # Zero quantity
        {"10": "1.50"},  # Discount > 100%
        {"10": "-0.10"}  # Negative discount
    ]
    
    for breaks in invalid_cases:
        update_data["quantity_breaks"] = breaks
        with pytest.raises(ValidationError):
            await service.validate_price_update(update_data)

@pytest.mark.asyncio
async def test_validate_price_update_currency(service):
    """Test validation of currency code"""
    # Valid currency
    update_data = {
        "item_id": "TEST001",
        "base_price": "100.00",
        "currency": "USD"
    }
    await service.validate_price_update(update_data)
    
    # Invalid currency formats
    invalid_currencies = ["US", "USDD", "123", "us"]
    
    for currency in invalid_currencies:
        update_data["currency"] = currency
        with pytest.raises(ValidationError, match="Invalid currency code"):
            await service.validate_price_update(update_data)

@pytest.mark.asyncio
async def test_validate_price_update_effective_date(service):
    """Test validation of effective date"""
    base_data = {
        "item_id": "TEST001",
        "base_price": "100.00",
        "currency": "USD"
    }
    
    # Future date should be valid
    future_date = datetime.now() + timedelta(days=1)
    update_data = {
        **base_data,
        "effective_date": future_date.isoformat()
    }
    await service.validate_price_update(update_data)
    
    # Past date should be invalid
    past_date = datetime.now() - timedelta(days=1)
    update_data["effective_date"] = past_date.isoformat()
    with pytest.raises(ValidationError, match="cannot be in the past"):
        await service.validate_price_update(update_data)

@pytest.mark.asyncio
async def test_validate_price_update_icd_codes(service, mock_repos):
    """Test validation of ICD codes"""
    _, _, icd_code_repo = mock_repos
    
    # Setup mock ICD codes
    icd_code_repo.get_by_code.side_effect = lambda code: {
        "ICD1": ICDCode(code="ICD1"),
        "ICD2": ICDCode(code="ICD2")
    }.get(code)
    
    # Valid ICD codes
    update_data = {
        "item_id": "TEST001",
        "base_price": "100.00",
        "currency": "USD",
        "icd_codes": ["ICD1", "ICD2"]
    }
    await service.validate_price_update(update_data)
    
    # Invalid ICD code
    update_data["icd_codes"] = ["ICD1", "INVALID"]
    with pytest.raises(ValidationError, match="Invalid ICD code"):
        await service.validate_price_update(update_data)

@pytest.mark.asyncio
async def test_validate_parameter(service):
    """Test parameter validation"""
    # Valid parameter
    parameter = {
        "name": "TEST_PARAM",
        "value": "1.2",
        "parameter_type": "MULTIPLIER"
    }
    await service.validate_parameter(parameter)
    
    # Invalid parameter type
    parameter["parameter_type"] = "INVALID"
    with pytest.raises(ValidationError, match="Invalid parameter type"):
        await service.validate_parameter(parameter)
    
    # Invalid value format
    parameter["parameter_type"] = "MULTIPLIER"
    parameter["value"] = "invalid"
    with pytest.raises(ValidationError, match="Invalid parameter value"):
        await service.validate_parameter(parameter)
