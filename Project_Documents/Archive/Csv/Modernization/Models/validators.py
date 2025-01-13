"""
Validation rules and functions for CSV processing.
"""
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from .types import ValidationResult, ValidationFunc, RowData, Headers
from .models import CsvConfig

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class CsvValidator:
    """CSV validation handler."""
    
    def __init__(self, config: CsvConfig):
        self.config = config
        self.validators: Dict[str, ValidationFunc] = {}
        self._setup_default_validators()

    def _setup_default_validators(self):
        """Setup default validation functions."""
        self.validators.update({
            'required': self.validate_required,
            'type': self.validate_type,
            'length': self.validate_length,
            'range': self.validate_range,
            'pattern': self.validate_pattern,
            'custom': None  # Placeholder for custom validation
        })

    def add_validator(self, name: str, func: ValidationFunc):
        """Add custom validator function."""
        self.validators[name] = func

    def validate_headers(self, headers: Headers) -> ValidationResult:
        """Validate CSV headers."""
        if not headers:
            return ValidationResult(False, errors=["No headers found"])

        if self.config.required_fields:
            missing = set(self.config.required_fields) - set(headers)
            if missing:
                return ValidationResult(
                    False,
                    errors=[f"Missing required fields: {', '.join(missing)}"]
                )

        return ValidationResult(True, data=headers)

    def validate_row(self, row: RowData, row_number: int) -> ValidationResult:
        """Validate a single CSV row."""
        errors = []
        
        for field, value in row.items():
            field_rules = self.config.field_rules.get(field, {})
            
            for rule, params in field_rules.items():
                validator = self.validators.get(rule)
                if validator:
                    try:
                        validator(value, params, field)
                    except ValidationError as e:
                        errors.append(f"Row {row_number}, Field '{field}': {str(e)}")

        return ValidationResult(not bool(errors), data=row, errors=errors)

    def validate_required(self, value: Any, params: bool, field: str):
        """Validate required fields."""
        if params and (value is None or str(value).strip() == ""):
            raise ValidationError(f"Required field '{field}' is missing or empty")

    def validate_type(self, value: Any, params: Dict[str, Any], field: str):
        """Validate field type."""
        expected_type = params.get('type')
        if not expected_type:
            return

        try:
            if expected_type == 'int':
                int(value)
            elif expected_type == 'float':
                float(value)
            elif expected_type == 'date':
                datetime.strptime(value, params.get('format', '%Y-%m-%d'))
            elif expected_type == 'bool':
                str(value).lower() in ('true', 'false', '1', '0', 'yes', 'no')
        except (ValueError, TypeError):
            raise ValidationError(
                f"Invalid type for field '{field}'. Expected {expected_type}"
            )

    def validate_length(self, value: Any, params: Dict[str, Any], field: str):
        """Validate field length."""
        if not isinstance(value, str):
            return

        min_len = params.get('min')
        max_len = params.get('max')
        
        if min_len is not None and len(value) < min_len:
            raise ValidationError(
                f"Field '{field}' length must be at least {min_len}"
            )
            
        if max_len is not None and len(value) > max_len:
            raise ValidationError(
                f"Field '{field}' length must not exceed {max_len}"
            )

    def validate_range(self, value: Any, params: Dict[str, Any], field: str):
        """Validate numeric range."""
        try:
            num_value = float(value)
            min_val = params.get('min')
            max_val = params.get('max')
            
            if min_val is not None and num_value < min_val:
                raise ValidationError(
                    f"Field '{field}' must be greater than or equal to {min_val}"
                )
                
            if max_val is not None and num_value > max_val:
                raise ValidationError(
                    f"Field '{field}' must be less than or equal to {max_val}"
                )
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid numeric value for field '{field}'")

    def validate_pattern(self, value: str, params: Dict[str, Any], field: str):
        """Validate against regex pattern."""
        import re
        pattern = params.get('pattern')
        if not pattern or not isinstance(value, str):
            return

        if not re.match(pattern, value):
            raise ValidationError(
                f"Field '{field}' does not match required pattern"
            )
