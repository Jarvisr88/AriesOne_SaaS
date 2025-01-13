"""
Unit tests for CSVValidator class
"""
import pytest
from datetime import datetime

from csv_validator import (
    CSVValidator,
    ValidationRule,
    ValidationError,
    not_empty,
    is_numeric,
    matches_pattern,
    in_range,
    max_length,
    is_date
)

@pytest.fixture
def validator():
    """Create validator with common rules."""
    validator = CSVValidator()
    
    # Add some common validation rules
    validator.add_rule(ValidationRule(
        field_name='id',
        validator=is_numeric,
        error_message='ID must be numeric'
    ))
    
    validator.add_rule(ValidationRule(
        field_name='name',
        validator=not_empty,
        error_message='Name cannot be empty'
    ))
    
    validator.add_rule(ValidationRule(
        field_name='price',
        validator=in_range(0, 1000),
        error_message='Price must be between 0 and 1000'
    ))
    
    return validator

def test_basic_validation(validator):
    """Test basic validation rules."""
    valid_row = {
        'id': '123',
        'name': 'Test Item',
        'price': '99.99'
    }
    
    errors = validator.validate_row(valid_row, 1)
    assert len(errors) == 0
    
def test_invalid_data(validator):
    """Test validation of invalid data."""
    invalid_row = {
        'id': 'abc',  # Should be numeric
        'name': '',   # Should not be empty
        'price': '1001'  # Should be <= 1000
    }
    
    errors = validator.validate_row(invalid_row, 1)
    assert len(errors) == 3
    
    error_fields = [e.field_name for e in errors]
    assert 'id' in error_fields
    assert 'name' in error_fields
    assert 'price' in error_fields
    
def test_missing_required_field(validator):
    """Test handling of missing required fields."""
    incomplete_row = {
        'id': '123',
        'price': '99.99'
        # 'name' is missing
    }
    
    errors = validator.validate_row(incomplete_row, 1)
    assert len(errors) == 1
    assert errors[0].field_name == 'name'
    
def test_pattern_validation():
    """Test regex pattern validation."""
    validator = CSVValidator()
    validator.add_rule(ValidationRule(
        field_name='email',
        validator=matches_pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$'),
        error_message='Invalid email format'
    ))
    
    valid_row = {'email': 'test@example.com'}
    invalid_row = {'email': 'invalid-email'}
    
    assert len(validator.validate_row(valid_row, 1)) == 0
    assert len(validator.validate_row(invalid_row, 1)) == 1
    
def test_date_validation():
    """Test date format validation."""
    validator = CSVValidator()
    validator.add_rule(ValidationRule(
        field_name='date',
        validator=is_date('%Y-%m-%d'),
        error_message='Invalid date format'
    ))
    
    valid_row = {'date': '2025-01-10'}
    invalid_row = {'date': '2025/01/10'}
    
    assert len(validator.validate_row(valid_row, 1)) == 0
    assert len(validator.validate_row(invalid_row, 1)) == 1
    
def test_multiple_rules_per_field():
    """Test multiple validation rules for single field."""
    validator = CSVValidator()
    
    # Add multiple rules for the same field
    validator.add_rule(ValidationRule(
        field_name='username',
        validator=not_empty,
        error_message='Username cannot be empty'
    ))
    
    validator.add_rule(ValidationRule(
        field_name='username',
        validator=max_length(10),
        error_message='Username too long'
    ))
    
    valid_row = {'username': 'user123'}
    empty_row = {'username': ''}
    long_row = {'username': 'verylongusername'}
    
    assert len(validator.validate_row(valid_row, 1)) == 0
    assert len(validator.validate_row(empty_row, 1)) == 1
    assert len(validator.validate_row(long_row, 1)) == 1
    
def test_error_handlers():
    """Test error handler callbacks."""
    validator = CSVValidator()
    errors_received = []
    
    def error_handler(error):
        errors_received.append(error)
    
    validator.add_error_handler(error_handler)
    validator.add_rule(ValidationRule(
        field_name='test',
        validator=not_empty,
        error_message='Cannot be empty'
    ))
    
    validator.validate_row({'test': ''}, 1)
    assert len(errors_received) == 1
    assert isinstance(errors_received[0], ValidationError)
    
def test_custom_validator():
    """Test custom validation function."""
    def is_even(value):
        try:
            return int(value) % 2 == 0
        except (ValueError, TypeError):
            return False
    
    validator = CSVValidator()
    validator.add_rule(ValidationRule(
        field_name='number',
        validator=is_even,
        error_message='Must be even number'
    ))
    
    assert len(validator.validate_row({'number': '2'}, 1)) == 0
    assert len(validator.validate_row({'number': '3'}, 1)) == 1
    
def test_validation_error_attributes():
    """Test validation error object attributes."""
    validator = CSVValidator()
    validator.add_rule(ValidationRule(
        field_name='test',
        validator=not_empty,
        error_message='Test error'
    ))
    
    errors = validator.validate_row({'test': ''}, 5)
    error = errors[0]
    
    assert error.field_name == 'test'
    assert error.value == ''
    assert error.error_message == 'Test error'
    assert error.row_number == 5
    assert isinstance(error.timestamp, datetime)
