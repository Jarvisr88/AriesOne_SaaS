from typing import List, Dict, Any, Type, Optional
from pydantic import BaseModel, ValidationError, validator
from datetime import datetime, date
import re
from app.models.file import ProcessingError

class ValidationRule:
    def __init__(self, field: str, rule: callable, message: str):
        self.field = field
        self.rule = rule
        self.message = message

    def validate(self, value: Any) -> Optional[str]:
        try:
            if not self.rule(value):
                return self.message
        except Exception:
            return self.message
        return None

class DataValidator:
    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}

    def add_rule(self, field: str, rule: callable, message: str) -> None:
        """Add a validation rule for a field"""
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append(ValidationRule(field, rule, message))

    def validate(self, data: Dict[str, Any]) -> List[ProcessingError]:
        """Validate data against all rules"""
        errors = []
        for field, rules in self.rules.items():
            value = data.get(field)
            for rule in rules:
                error_message = rule.validate(value)
                if error_message:
                    errors.append(
                        ProcessingError(
                            line=0,  # Set by processor
                            column=field,
                            message=error_message,
                            severity="ERROR"
                        )
                    )
        return errors

class CommonValidators:
    @staticmethod
    def required(message: str = "This field is required") -> callable:
        return lambda v: v is not None and str(v).strip() != ""

    @staticmethod
    def min_length(min_len: int, message: str = None) -> callable:
        return lambda v: len(str(v)) >= min_len

    @staticmethod
    def max_length(max_len: int, message: str = None) -> callable:
        return lambda v: len(str(v)) <= max_len

    @staticmethod
    def pattern(regex: str, message: str = None) -> callable:
        return lambda v: bool(re.match(regex, str(v)))

    @staticmethod
    def email(message: str = "Invalid email format") -> callable:
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return lambda v: bool(re.match(email_regex, str(v)))

    @staticmethod
    def phone(message: str = "Invalid phone number") -> callable:
        phone_regex = r"^\+?1?\d{9,15}$"
        return lambda v: bool(re.match(phone_regex, str(v)))

    @staticmethod
    def date_format(fmt: str = "%Y-%m-%d", message: str = None) -> callable:
        def validate_date(v):
            try:
                if isinstance(v, (date, datetime)):
                    return True
                datetime.strptime(str(v), fmt)
                return True
            except ValueError:
                return False
        return validate_date

    @staticmethod
    def numeric(message: str = "Must be a number") -> callable:
        return lambda v: str(v).replace(".", "").replace("-", "").isdigit()

    @staticmethod
    def min_value(min_val: float, message: str = None) -> callable:
        return lambda v: float(v) >= min_val

    @staticmethod
    def max_value(max_val: float, message: str = None) -> callable:
        return lambda v: float(v) <= max_val

    @staticmethod
    def in_list(valid_values: List[Any], message: str = None) -> callable:
        return lambda v: v in valid_values

class MedicareValidators:
    @staticmethod
    def npi(message: str = "Invalid NPI number") -> callable:
        def validate_npi(v: str) -> bool:
            if not v or not v.isdigit() or len(v) != 10:
                return False
            
            # NPI checksum validation
            digits = [int(d) for d in v]
            check_digit = digits.pop()
            
            # Multiply even positions by 2
            for i in range(0, len(digits), 2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            
            # Calculate checksum
            checksum = (sum(digits) * 9) % 10
            return checksum == check_digit
            
        return validate_npi

    @staticmethod
    def hcpcs_code(message: str = "Invalid HCPCS code") -> callable:
        def validate_hcpcs(v: str) -> bool:
            if not v:
                return False
            
            # Level I (CPT) codes: 5 digits
            if v.isdigit() and len(v) == 5:
                return True
            
            # Level II codes: Letter followed by 4 digits
            if (len(v) == 5 and 
                v[0].isalpha() and 
                v[1:].isdigit()):
                return True
            
            return False
            
        return validate_hcpcs

    @staticmethod
    def diagnosis_code(message: str = "Invalid ICD-10 code") -> callable:
        def validate_icd10(v: str) -> bool:
            if not v:
                return False
            
            # ICD-10 format: Letter followed by 2 digits
            # Optional: decimal point and up to 4 more digits
            pattern = r"^[A-Z][0-9]{2}(\.[0-9]{1,4})?$"
            return bool(re.match(pattern, v))
            
        return validate_icd10

    @staticmethod
    def medicare_id(message: str = "Invalid Medicare ID") -> callable:
        def validate_medicare_id(v: str) -> bool:
            if not v:
                return False
            
            # MBI format validation
            pattern = r"^[1-9][A-Z][0-9][A-Z][0-9][A-Z][0-9]{3}[A-Z]$"
            return bool(re.match(pattern, v))
            
        return validate_medicare_id

class ValidationSchema(BaseModel):
    """Base class for validation schemas with common validators"""
    
    @validator("*", pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    @validator("*", pre=True)
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        anystr_strip_whitespace = True
        validate_assignment = True
        extra = "forbid"
