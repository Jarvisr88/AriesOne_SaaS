from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException
import re

class ValidationRule(BaseModel):
    field: str
    rule_type: str
    params: Dict[str, Any] = {}
    error_message: str

class ValidationFramework:
    def __init__(self):
        self._rules: Dict[Type[BaseModel], List[ValidationRule]] = {}

    def add_rule(self, model_class: Type[BaseModel], rule: ValidationRule):
        if model_class not in self._rules:
            self._rules[model_class] = []
        self._rules[model_class].append(rule)

    def validate(self, model_instance: BaseModel) -> List[str]:
        errors = []
        model_class = type(model_instance)
        
        if model_class not in self._rules:
            return errors

        for rule in self._rules[model_class]:
            try:
                value = getattr(model_instance, rule.field)
                if not self._check_rule(value, rule):
                    errors.append(rule.error_message)
            except AttributeError:
                errors.append(f"Field {rule.field} not found")

        return errors

    def _check_rule(self, value: Any, rule: ValidationRule) -> bool:
        if rule.rule_type == "required":
            return value is not None and value != ""
        elif rule.rule_type == "regex":
            return bool(re.match(rule.params["pattern"], str(value)))
        elif rule.rule_type == "range":
            return rule.params["min"] <= value <= rule.params["max"]
        elif rule.rule_type == "length":
            return rule.params["min"] <= len(str(value)) <= rule.params["max"]
        elif rule.rule_type == "custom":
            return rule.params["validator"](value)
        return True

class AddressValidator:
    @staticmethod
    def validate_us_address(address: str) -> bool:
        # Basic US address pattern
        pattern = r"^\d+\s+[A-Za-z0-9\s\.,'-]+\s+(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\s+\d{5}(?:-\d{4})?$"
        return bool(re.match(pattern, address))

class NameValidator:
    @staticmethod
    def validate_name(name: str) -> bool:
        # Allow letters, spaces, hyphens, and apostrophes
        pattern = r"^[A-Za-z\s\-']+$"
        return bool(re.match(pattern, name))

    @staticmethod
    def validate_professional_title(title: str) -> bool:
        valid_titles = {
            "Dr.", "Prof.", "Mr.", "Mrs.", "Ms.", "Mx.",
            "MD", "PhD", "DDS", "DVM", "DO", "PA-C", "NP"
        }
        return title in valid_titles

# Initialize global validator
validator = ValidationFramework()
