"""
AriesOne CSV Validation Module

Provides validation hooks and data quality checks for CSV processing.
"""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ValidationRule:
    """Defines a validation rule for CSV data."""
    field_name: str
    validator: Callable[[Any], bool]
    error_message: str
    is_required: bool = True

@dataclass
class ValidationError:
    """Represents a validation error."""
    field_name: str
    value: Any
    error_message: str
    row_number: int
    timestamp: datetime = datetime.now()

class CSVValidator:
    """Validator for CSV data with customizable rules."""
    
    def __init__(self):
        """Initialize validator with empty rules."""
        self.rules: Dict[str, List[ValidationRule]] = {}
        self._error_handlers: List[Callable[[ValidationError], None]] = []
        
    def add_rule(self, rule: ValidationRule):
        """Add a validation rule.
        
        Args:
            rule: ValidationRule to add
        """
        if rule.field_name not in self.rules:
            self.rules[rule.field_name] = []
        self.rules[rule.field_name].append(rule)
        
    def add_error_handler(self, handler: Callable[[ValidationError], None]):
        """Add error handler callback.
        
        Args:
            handler: Callback for validation errors
        """
        self._error_handlers.append(handler)
        
    def _handle_error(self, error: ValidationError):
        """Process validation error through handlers.
        
        Args:
            error: ValidationError instance
        """
        for handler in self._error_handlers:
            handler(error)
            
    def validate_row(
        self,
        row: Dict[str, Any],
        row_number: int
    ) -> List[ValidationError]:
        """Validate a single row of CSV data.
        
        Args:
            row: Dictionary of field names to values
            row_number: Row number in CSV file
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required fields
        for field_name, rules in self.rules.items():
            required = any(rule.is_required for rule in rules)
            if required and field_name not in row:
                error = ValidationError(
                    field_name=field_name,
                    value=None,
                    error_message="Required field missing",
                    row_number=row_number
                )
                errors.append(error)
                self._handle_error(error)
                continue
                
            # Apply validation rules
            if field_name in row:
                value = row[field_name]
                for rule in rules:
                    try:
                        if not rule.validator(value):
                            error = ValidationError(
                                field_name=field_name,
                                value=value,
                                error_message=rule.error_message,
                                row_number=row_number
                            )
                            errors.append(error)
                            self._handle_error(error)
                    except Exception as e:
                        error = ValidationError(
                            field_name=field_name,
                            value=value,
                            error_message=f"Validation error: {str(e)}",
                            row_number=row_number
                        )
                        errors.append(error)
                        self._handle_error(error)
                        
        return errors

# Common validation functions
def not_empty(value: Any) -> bool:
    """Check if value is not empty."""
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True

def is_numeric(value: Any) -> bool:
    """Check if value is numeric."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def matches_pattern(pattern: str) -> Callable[[str], bool]:
    """Create regex pattern validator.
    
    Args:
        pattern: Regular expression pattern
        
    Returns:
        Validation function
    """
    regex = re.compile(pattern)
    return lambda value: bool(regex.match(str(value)))

def in_range(min_val: float, max_val: float) -> Callable[[Any], bool]:
    """Create range validator.
    
    Args:
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validation function
    """
    def validator(value: Any) -> bool:
        try:
            num_val = float(value)
            return min_val <= num_val <= max_val
        except (ValueError, TypeError):
            return False
    return validator

def max_length(max_len: int) -> Callable[[str], bool]:
    """Create string length validator.
    
    Args:
        max_len: Maximum allowed length
        
    Returns:
        Validation function
    """
    return lambda value: len(str(value)) <= max_len

def is_date(format_str: str = "%Y-%m-%d") -> Callable[[str], bool]:
    """Create date format validator.
    
    Args:
        format_str: Expected date format
        
    Returns:
        Validation function
    """
    def validator(value: str) -> bool:
        try:
            datetime.strptime(str(value), format_str)
            return True
        except (ValueError, TypeError):
            return False
    return validator
