import pytest
import pandas as pd
from pathlib import Path
import json
import tempfile
from datetime import datetime

from app.services.csv_processor import (
    CSVProcessor,
    CSVSchema,
    ColumnSchema,
    ValidationResult,
    ProcessingResult
)
from app.models.core import ProcessingStatus

@pytest.fixture
def test_schema():
    return CSVSchema(
        name="test_schema",
        columns=[
            ColumnSchema(
                name="id",
                data_type="string",
                required=True,
                validation_rules={"regex": "^\\d{6}$"}
            ),
            ColumnSchema(
                name="name",
                data_type="string",
                required=True,
                transformation_rules={"uppercase": True, "trim": True}
            ),
            ColumnSchema(
                name="age",
                data_type="integer",
                required=True,
                validation_rules={"min": 0, "max": 120}
            ),
            ColumnSchema(
                name="email",
                data_type="string",
                required=False,
                validation_rules={
                    "regex": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                }
            )
        ],
        delimiter=",",
        encoding="utf-8"
    )

@pytest.fixture
def csv_processor(test_schema):
    processor = CSVProcessor()
    processor.schemas["test_schema"] = test_schema
    return processor

@pytest.fixture
def valid_csv_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name,age,email\n")
        f.write("123456,John Doe,30,john@example.com\n")
        f.write("234567,Jane Smith,25,jane@example.com\n")
    return Path(f.name)

@pytest.fixture
def invalid_csv_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name,age,email\n")
        f.write("12345,John Doe,30,invalid-email\n")  # Invalid ID and email
        f.write("234567,Jane Smith,-5,jane@example.com\n")  # Invalid age
    return Path(f.name)

def test_schema_detection(csv_processor, valid_csv_file):
    schema_name, confidence = csv_processor.detect_schema(str(valid_csv_file))
    assert schema_name == "test_schema"
    assert confidence > 0.8

def test_validate_valid_file(csv_processor, valid_csv_file):
    result = csv_processor.validate_file(str(valid_csv_file), "test_schema")
    assert isinstance(result, ValidationResult)
    assert result.is_valid
    assert result.errors == []
    assert result.row_count == 2
    assert result.valid_row_count == 2
    assert result.invalid_row_count == 0

def test_validate_invalid_file(csv_processor, invalid_csv_file):
    result = csv_processor.validate_file(str(invalid_csv_file), "test_schema")
    assert isinstance(result, ValidationResult)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.row_count == 2
    assert result.valid_row_count < 2
    assert result.invalid_row_count > 0

    # Check specific error types
    error_types = {error["type"] for error in result.errors}
    assert "invalid_type" in error_types or "rule_violation" in error_types

def test_process_valid_file(csv_processor, valid_csv_file):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as output_file:
        result = csv_processor.process_file(
            str(valid_csv_file),
            "test_schema",
            output_file.name
        )
        
        assert isinstance(result, ProcessingResult)
        assert result.status == ProcessingStatus.COMPLETED
        assert result.total_rows == 2
        assert result.processed_rows == 2
        assert result.failed_rows == 0
        assert result.errors == []
        assert result.output_path == output_file.name

        # Verify transformations
        df = pd.read_csv(output_file.name)
        assert all(name == name.upper().strip() for name in df["name"])

def test_process_invalid_file(csv_processor, invalid_csv_file):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as output_file:
        result = csv_processor.process_file(
            str(invalid_csv_file),
            "test_schema",
            output_file.name
        )
        
        assert isinstance(result, ProcessingResult)
        assert result.status == ProcessingStatus.FAILED
        assert len(result.errors) > 0

def test_column_validation(csv_processor):
    # Test required columns
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name,email\n")  # Missing required 'age' column
        f.write("123456,John Doe,john@example.com\n")
    
    result = csv_processor.validate_file(f.name, "test_schema")
    assert not result.is_valid
    assert any(error["type"] == "missing_columns" for error in result.errors)

def test_data_type_validation(csv_processor):
    # Test integer validation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name,age,email\n")
        f.write("123456,John Doe,invalid,john@example.com\n")  # Invalid age
    
    result = csv_processor.validate_file(f.name, "test_schema")
    assert not result.is_valid
    assert any(
        error["type"] == "invalid_type" and error["column"] == "age"
        for error in result.errors
    )

def test_custom_validation_rules(csv_processor):
    # Test regex validation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name,age,email\n")
        f.write("12345,John Doe,30,john@example.com\n")  # Invalid ID (5 digits)
    
    result = csv_processor.validate_file(f.name, "test_schema")
    assert not result.is_valid
    assert any(
        error["type"] == "rule_violation" and error["column"] == "id"
        for error in result.errors
    )

def test_transformation_rules(csv_processor):
    # Test uppercase transformation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name,age,email\n")
        f.write("123456,john doe,30,john@example.com\n")
    
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as output_file:
        result = csv_processor.process_file(f.name, "test_schema", output_file.name)
        
        assert result.status == ProcessingStatus.COMPLETED
        
        # Verify transformation
        df = pd.read_csv(output_file.name)
        assert df["name"][0] == "JOHN DOE"

def test_error_handling(csv_processor):
    # Test non-existent file
    with pytest.raises(Exception):
        csv_processor.validate_file("non_existent.csv", "test_schema")

    # Test invalid schema
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name,age,email\n")
        f.write("123456,John Doe,30,john@example.com\n")
    
    with pytest.raises(ValueError):
        csv_processor.validate_file(f.name, "non_existent_schema")

def test_performance(csv_processor):
    # Generate a large CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("id,name,age,email\n")
        for i in range(10000):
            f.write(f"{123456+i},Name{i},30,test{i}@example.com\n")
    
    start_time = datetime.utcnow()
    result = csv_processor.validate_file(f.name, "test_schema")
    end_time = datetime.utcnow()
    
    # Validation should complete in reasonable time
    assert (end_time - start_time).total_seconds() < 5
    assert result.row_count == 10000
