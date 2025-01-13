import pytest
from pydantic import ValidationError
from ....models.name import Name, Courtesy

def test_valid_name():
    """Test creating a valid name"""
    name = Name(
        first_name="John",
        last_name="Doe"
    )
    assert name.first_name == "John"
    assert name.last_name == "Doe"
    assert name.middle_name is None
    assert name.courtesy is None
    assert name.suffix is None

def test_name_with_all_fields():
    """Test name with all optional fields"""
    name = Name(
        courtesy=Courtesy.DR,
        first_name="John",
        middle_name="William",
        last_name="Doe",
        suffix="Jr."
    )
    assert name.courtesy == Courtesy.DR
    assert name.middle_name == "William"
    assert name.suffix == "Jr."

def test_name_capitalization():
    """Test automatic name capitalization"""
    name = Name(
        first_name="john william",
        last_name="doe"
    )
    assert name.first_name == "John William"
    assert name.last_name == "Doe"

def test_invalid_suffix():
    """Test validation of invalid name suffix"""
    with pytest.raises(ValidationError) as exc_info:
        Name(
            first_name="John",
            last_name="Doe",
            suffix="Invalid"
        )
    assert "Invalid name suffix" in str(exc_info.value)

def test_full_name_formatting():
    """Test full name string formatting"""
    name = Name(
        courtesy=Courtesy.DR,
        first_name="John",
        middle_name="William",
        last_name="Doe",
        suffix="Jr."
    )
    assert name.to_full_name() == "Dr. John William Doe Jr."

def test_formal_name_formatting():
    """Test formal name string formatting"""
    name = Name(
        courtesy=Courtesy.DR,
        first_name="John",
        middle_name="William",
        last_name="Doe",
        suffix="Jr."
    )
    assert name.to_formal_name() == "Doe, Dr. John W. Jr."

def test_minimal_name_formatting():
    """Test name formatting with minimal fields"""
    name = Name(
        first_name="John",
        last_name="Doe"
    )
    assert name.to_full_name() == "John Doe"
    assert name.to_formal_name() == "Doe, John"
