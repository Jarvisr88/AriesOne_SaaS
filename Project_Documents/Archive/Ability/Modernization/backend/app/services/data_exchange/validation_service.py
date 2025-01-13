from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.data_exchange import (
    ValidationSchema,
    ValidationRule,
    ValidationLog
)

class ValidationService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.supported_types = [
            "string",
            "number",
            "integer",
            "boolean",
            "date",
            "email",
            "phone",
            "url",
            "enum",
            "array",
            "object"
        ]

    async def validate_data(
        self,
        schema_id: str,
        data: Any,
        context: Optional[Dict] = None
    ) -> Dict:
        """Validate data against schema"""
        try:
            # Get schema
            schema = await self._get_schema(schema_id)
            
            # Create validation log
            log = await ValidationLog.create(
                schema_id=schema_id,
                context=context or {},
                status="processing",
                created_at=datetime.now()
            )
            
            # Perform validation
            validation_result = await self._validate(
                data,
                schema.rules,
                schema.options or {}
            )
            
            # Update log
            log.status = "completed"
            log.is_valid = validation_result["valid"]
            log.errors = validation_result.get("errors", [])
            log.completed_at = datetime.now()
            await log.save()
            
            return validation_result
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            if log:
                log.status = "failed"
                log.error = str(e)
                await log.save()
            raise HTTPException(status_code=500, detail=str(e))

    async def create_schema(
        self,
        schema_data: Dict
    ) -> ValidationSchema:
        """Create validation schema"""
        try:
            # Validate schema data
            self._validate_schema_data(schema_data)
            
            # Create schema
            schema = await ValidationSchema.create(
                name=schema_data["name"],
                description=schema_data.get("description"),
                rules=schema_data["rules"],
                options=schema_data.get("options", {}),
                created_at=datetime.now()
            )
            
            return schema
        except Exception as e:
            logger.error(f"Failed to create schema: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_rule(
        self,
        rule_data: Dict
    ) -> ValidationRule:
        """Create validation rule"""
        try:
            # Validate rule data
            self._validate_rule_data(rule_data)
            
            # Create rule
            rule = await ValidationRule.create(
                name=rule_data["name"],
                description=rule_data.get("description"),
                type=rule_data["type"],
                settings=rule_data.get("settings", {}),
                created_at=datetime.now()
            )
            
            return rule
        except Exception as e:
            logger.error(f"Failed to create rule: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_schema(self, schema_id: str) -> ValidationSchema:
        """Get validation schema"""
        schema = await ValidationSchema.get(id=schema_id)
        if not schema:
            raise ValueError(f"Schema not found: {schema_id}")
        return schema

    async def _validate(
        self,
        data: Any,
        rules: Dict,
        options: Dict
    ) -> Dict:
        """Validate data against rules"""
        errors = []
        
        # Handle different data types
        if isinstance(data, dict):
            errors.extend(
                await self._validate_object(data, rules, options)
            )
        elif isinstance(data, list):
            errors.extend(
                await self._validate_array(data, rules, options)
            )
        else:
            errors.extend(
                await self._validate_value(data, rules, options)
            )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    async def _validate_object(
        self,
        data: Dict,
        rules: Dict,
        options: Dict
    ) -> List[Dict]:
        """Validate object data"""
        errors = []
        
        # Required fields
        for field, rule in rules.items():
            if rule.get("required", False) and field not in data:
                errors.append({
                    "field": field,
                    "error": "Field is required"
                })
        
        # Field validations
        for field, value in data.items():
            if field in rules:
                field_errors = await self._validate_value(
                    value,
                    rules[field],
                    options
                )
                for error in field_errors:
                    error["field"] = field
                    errors.append(error)
        
        # Additional properties
        if not options.get("allow_additional_properties", True):
            for field in data:
                if field not in rules:
                    errors.append({
                        "field": field,
                        "error": "Additional properties not allowed"
                    })
        
        return errors

    async def _validate_array(
        self,
        data: List,
        rules: Dict,
        options: Dict
    ) -> List[Dict]:
        """Validate array data"""
        errors = []
        
        # Array length
        min_items = rules.get("min_items")
        max_items = rules.get("max_items")
        
        if min_items is not None and len(data) < min_items:
            errors.append({
                "error": f"Array must have at least {min_items} items"
            })
        
        if max_items is not None and len(data) > max_items:
            errors.append({
                "error": f"Array must have at most {max_items} items"
            })
        
        # Item validation
        if "items" in rules:
            for idx, item in enumerate(data):
                item_errors = await self._validate_value(
                    item,
                    rules["items"],
                    options
                )
                for error in item_errors:
                    error["index"] = idx
                    errors.append(error)
        
        # Unique items
        if rules.get("unique_items", False):
            seen = set()
            for idx, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    item_str = str(item)
                else:
                    item_str = item
                
                if item_str in seen:
                    errors.append({
                        "index": idx,
                        "error": "Duplicate item"
                    })
                seen.add(item_str)
        
        return errors

    async def _validate_value(
        self,
        value: Any,
        rules: Dict,
        options: Dict
    ) -> List[Dict]:
        """Validate single value"""
        errors = []
        
        # Type validation
        if "type" in rules:
            type_valid = self._validate_type(value, rules["type"])
            if not type_valid:
                errors.append({
                    "error": f"Value must be of type {rules['type']}"
                })
                return errors  # Skip further validation if type is invalid
        
        # Format validation
        if "format" in rules:
            format_valid = self._validate_format(
                value,
                rules["format"]
            )
            if not format_valid:
                errors.append({
                    "error": f"Invalid {rules['format']} format"
                })
        
        # Pattern validation
        if "pattern" in rules:
            pattern_valid = self._validate_pattern(
                value,
                rules["pattern"]
            )
            if not pattern_valid:
                errors.append({
                    "error": "Value does not match pattern"
                })
        
        # Range validation
        if any(key in rules for key in ["minimum", "maximum", "min_length", "max_length"]):
            range_valid = self._validate_range(value, rules)
            if not range_valid["valid"]:
                errors.append({
                    "error": range_valid["error"]
                })
        
        # Enum validation
        if "enum" in rules:
            enum_valid = value in rules["enum"]
            if not enum_valid:
                errors.append({
                    "error": "Value not in allowed options"
                })
        
        # Custom validation
        if "custom" in rules:
            custom_valid = await self._validate_custom(
                value,
                rules["custom"],
                options
            )
            if not custom_valid["valid"]:
                errors.append({
                    "error": custom_valid["error"]
                })
        
        return errors

    def _validate_type(self, value: Any, type_name: str) -> bool:
        """Validate value type"""
        if type_name not in self.supported_types:
            raise ValueError(f"Unsupported type: {type_name}")
        
        if value is None:
            return False
        
        if type_name == "string":
            return isinstance(value, str)
        elif type_name == "number":
            return isinstance(value, (int, float))
        elif type_name == "integer":
            return isinstance(value, int)
        elif type_name == "boolean":
            return isinstance(value, bool)
        elif type_name == "date":
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return True
            except:
                return False
        elif type_name == "array":
            return isinstance(value, list)
        elif type_name == "object":
            return isinstance(value, dict)
        
        return True

    def _validate_format(self, value: str, format_name: str) -> bool:
        """Validate value format"""
        if not isinstance(value, str):
            return False
        
        if format_name == "email":
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            return bool(re.match(pattern, value))
        elif format_name == "phone":
            pattern = r"^\+?1?\d{9,15}$"
            return bool(re.match(pattern, value))
        elif format_name == "url":
            pattern = r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$"
            return bool(re.match(pattern, value))
        
        return True

    def _validate_pattern(self, value: str, pattern: str) -> bool:
        """Validate value against pattern"""
        if not isinstance(value, str):
            return False
        return bool(re.match(pattern, value))

    def _validate_range(self, value: Any, rules: Dict) -> Dict:
        """Validate value range"""
        try:
            if isinstance(value, (int, float)):
                if "minimum" in rules and value < rules["minimum"]:
                    return {
                        "valid": False,
                        "error": f"Value must be >= {rules['minimum']}"
                    }
                if "maximum" in rules and value > rules["maximum"]:
                    return {
                        "valid": False,
                        "error": f"Value must be <= {rules['maximum']}"
                    }
            elif isinstance(value, str):
                if "min_length" in rules and len(value) < rules["min_length"]:
                    return {
                        "valid": False,
                        "error": f"Length must be >= {rules['min_length']}"
                    }
                if "max_length" in rules and len(value) > rules["max_length"]:
                    return {
                        "valid": False,
                        "error": f"Length must be <= {rules['max_length']}"
                    }
            elif isinstance(value, list):
                if "min_length" in rules and len(value) < rules["min_length"]:
                    return {
                        "valid": False,
                        "error": f"Array length must be >= {rules['min_length']}"
                    }
                if "max_length" in rules and len(value) > rules["max_length"]:
                    return {
                        "valid": False,
                        "error": f"Array length must be <= {rules['max_length']}"
                    }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Range validation failed: {str(e)}"
            }
        
        return {"valid": True}

    async def _validate_custom(
        self,
        value: Any,
        custom_rule: Dict,
        options: Dict
    ) -> Dict:
        """Execute custom validation rule"""
        try:
            rule_type = custom_rule.get("type")
            if not rule_type:
                return {
                    "valid": False,
                    "error": "Custom rule type not specified"
                }
            
            # Get custom rule implementation
            rule = await ValidationRule.get(
                type=rule_type,
                is_active=True
            )
            if not rule:
                return {
                    "valid": False,
                    "error": f"Custom rule not found: {rule_type}"
                }
            
            # Execute rule
            settings = {
                **rule.settings,
                **custom_rule.get("settings", {})
            }
            
            # Rule implementation would go here
            # This is a placeholder for custom validation logic
            return {"valid": True}
        except Exception as e:
            return {
                "valid": False,
                "error": f"Custom validation failed: {str(e)}"
            }

    def _validate_schema_data(self, schema_data: Dict) -> None:
        """Validate schema creation data"""
        required_fields = ["name", "rules"]
        for field in required_fields:
            if field not in schema_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(schema_data["rules"], dict):
            raise ValueError("Rules must be a dictionary")

    def _validate_rule_data(self, rule_data: Dict) -> None:
        """Validate rule creation data"""
        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in rule_data:
                raise ValueError(f"Missing required field: {field}")
        
        if rule_data["type"] not in self.supported_types:
            raise ValueError(f"Unsupported type: {rule_data['type']}")
