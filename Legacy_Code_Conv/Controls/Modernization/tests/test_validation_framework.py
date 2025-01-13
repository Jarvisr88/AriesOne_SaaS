import pytest
from datetime import datetime
from validation.validation_framework import validator
from pydantic import ValidationError

def test_address_validation():
    """Test address validation functionality"""
    # Valid address
    valid_address = {
        "street_address": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94105",
        "country": "USA"
    }
    assert validator.validate_address(valid_address) == []

    # Invalid address - missing required fields
    invalid_address = {
        "street_address": "123 Main St",
        "city": "San Francisco"
    }
    errors = validator.validate_address(invalid_address)
    assert len(errors) > 0
    assert any("state" in error for error in errors)

    # Invalid postal code format
    invalid_postal = {
        "street_address": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "9410",  # Too short
        "country": "USA"
    }
    errors = validator.validate_address(invalid_postal)
    assert len(errors) > 0
    assert any("postal_code" in error for error in errors)

def test_name_validation():
    """Test name validation functionality"""
    # Valid name
    valid_name = {
        "first_name": "John",
        "middle_name": "Robert",
        "last_name": "Smith",
        "prefix": "Dr.",
        "suffix": "Jr.",
        "credentials": "MD"
    }
    assert validator.validate_name(valid_name) == []

    # Invalid name - empty required fields
    invalid_name = {
        "first_name": "",
        "last_name": "Smith"
    }
    errors = validator.validate_name(invalid_name)
    assert len(errors) > 0
    assert any("first_name" in error for error in errors)

    # Invalid characters in name
    invalid_chars = {
        "first_name": "John123",
        "last_name": "Smith"
    }
    errors = validator.validate_name(invalid_chars)
    assert len(errors) > 0
    assert any("numeric" in error for error in errors)

def test_date_validation():
    """Test date validation functionality"""
    # Valid date
    valid_date = datetime.now().date()
    assert validator.validate_date(valid_date) == []

    # Future date validation
    future_date = datetime.now().date().replace(year=datetime.now().year + 1)
    errors = validator.validate_date(future_date, allow_future=False)
    assert len(errors) > 0
    assert any("future" in error for error in errors)

    # Date format validation
    invalid_format = "2023/13/45"
    errors = validator.validate_date(invalid_format)
    assert len(errors) > 0
    assert any("format" in error for error in errors)

def test_phone_validation():
    """Test phone number validation functionality"""
    # Valid US phone numbers
    valid_phones = [
        "123-456-7890",
        "(123) 456-7890",
        "1234567890"
    ]
    for phone in valid_phones:
        assert validator.validate_phone(phone, country="US") == []

    # Invalid phone numbers
    invalid_phones = [
        "123-456-789",  # Too short
        "123-456-78901",  # Too long
        "abc-def-ghij",  # Non-numeric
        "(123 456-7890"  # Mismatched parentheses
    ]
    for phone in invalid_phones:
        errors = validator.validate_phone(phone, country="US")
        assert len(errors) > 0

def test_email_validation():
    """Test email validation functionality"""
    # Valid email addresses
    valid_emails = [
        "test@example.com",
        "user.name+tag@example.co.uk",
        "user.name@subdomain.example.com"
    ]
    for email in valid_emails:
        assert validator.validate_email(email) == []

    # Invalid email addresses
    invalid_emails = [
        "test@",  # Incomplete
        "test@.com",  # Missing domain
        "@example.com",  # Missing local part
        "test@example",  # Missing TLD
        "test@exam ple.com"  # Contains space
    ]
    for email in invalid_emails:
        errors = validator.validate_email(email)
        assert len(errors) > 0

def test_custom_validation_rules():
    """Test custom validation rules functionality"""
    # Define custom rule
    def validate_age(value):
        if not isinstance(value, int):
            return ["Age must be a number"]
        if value < 0 or value > 150:
            return ["Age must be between 0 and 150"]
        return []

    # Register custom rule
    validator.register_custom_rule("age", validate_age)

    # Test custom rule
    assert validator.validate_with_rule("age", 25) == []
    assert len(validator.validate_with_rule("age", -1)) > 0
    assert len(validator.validate_with_rule("age", 200)) > 0
    assert len(validator.validate_with_rule("age", "not a number")) > 0

def test_validation_chain():
    """Test chaining multiple validations"""
    data = {
        "name": {
            "first_name": "John",
            "last_name": "Smith"
        },
        "address": {
            "street_address": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94105"
        },
        "contact": {
            "email": "john.smith@example.com",
            "phone": "123-456-7890"
        }
    }

    # Validate all fields
    errors = validator.validate_all(data)
    assert isinstance(errors, dict)
    assert len(errors) == 0

    # Invalid data
    invalid_data = {
        "name": {
            "first_name": "",  # Empty
            "last_name": "Smith123"  # Invalid characters
        },
        "address": {
            "street_address": "123 Main St",
            "city": "",  # Empty
            "postal_code": "941"  # Invalid format
        },
        "contact": {
            "email": "invalid.email@",  # Invalid format
            "phone": "123-456"  # Invalid format
        }
    }

    errors = validator.validate_all(invalid_data)
    assert isinstance(errors, dict)
    assert len(errors) > 0
    assert "name" in errors
    assert "address" in errors
    assert "contact" in errors

def test_validation_performance():
    """Test validation performance with large datasets"""
    import time

    # Create large dataset
    large_dataset = [
        {
            "name": {
                "first_name": f"First{i}",
                "last_name": f"Last{i}"
            },
            "address": {
                "street_address": f"{i} Main St",
                "city": "San Francisco",
                "state": "CA",
                "postal_code": "94105"
            }
        }
        for i in range(1000)
    ]

    # Measure validation time
    start_time = time.time()
    for data in large_dataset:
        validator.validate_all(data)
    end_time = time.time()

    # Assert reasonable performance (adjust threshold as needed)
    assert end_time - start_time < 5.0  # Should validate 1000 records in under 5 seconds

if __name__ == "__main__":
    pytest.main([__file__])
