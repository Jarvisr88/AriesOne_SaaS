import pytest
from pydantic import ValidationError
from ....models.address import Address

def test_valid_address():
    """Test creating a valid address"""
    address = Address(
        address1="123 Main St",
        city="Springfield",
        state="IL",
        zip_code="62701"
    )
    assert address.address1 == "123 Main St"
    assert address.city == "Springfield"
    assert address.state == "IL"
    assert address.zip_code == "62701"
    assert address.address2 is None

def test_address_with_optional_fields():
    """Test address with optional address2 field"""
    address = Address(
        address1="123 Main St",
        address2="Suite 100",
        city="Springfield",
        state="IL",
        zip_code="62701"
    )
    assert address.address2 == "Suite 100"

def test_invalid_state():
    """Test validation of invalid state code"""
    with pytest.raises(ValidationError) as exc_info:
        Address(
            address1="123 Main St",
            city="Springfield",
            state="Illinois",  # Invalid: should be 2 letters
            zip_code="62701"
        )
    assert "State must be a 2-letter code" in str(exc_info.value)

def test_invalid_zip():
    """Test validation of invalid ZIP code"""
    with pytest.raises(ValidationError) as exc_info:
        Address(
            address1="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="6270"  # Invalid: too short
        )
    assert "Invalid ZIP code format" in str(exc_info.value)

def test_address_to_string():
    """Test address string formatting"""
    address = Address(
        address1="123 Main St",
        address2="Suite 100",
        city="Springfield",
        state="IL",
        zip_code="62701"
    )
    expected = "123 Main St\nSuite 100\nSpringfield, IL 62701"
    assert address.to_string() == expected

def test_address_to_map_string():
    """Test map-friendly string formatting"""
    address = Address(
        address1="123 Main St",
        address2="Suite 100",
        city="Springfield",
        state="IL",
        zip_code="62701"
    )
    expected = "123 Main St, Suite 100, Springfield, IL, 62701"
    assert address.to_map_string() == expected
