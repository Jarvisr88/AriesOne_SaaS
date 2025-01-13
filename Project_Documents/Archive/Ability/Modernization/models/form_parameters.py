"""
Form Parameters Models Module

This module provides models for form parameters.
"""
from typing import Optional, Dict, Any, List, Union, TypeVar, Generic
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import urllib.parse

T = TypeVar('T')

class ParameterType(str, Enum):
    """Enumeration of parameter types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    LIST = "list"
    DICT = "dict"

class Parameter(BaseModel):
    """Model for a single parameter"""
    key: str
    value: Any
    type: ParameterType = ParameterType.STRING
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FormParameters(BaseModel):
    """Model for form parameters"""
    parameters: Dict[str, Parameter] = Field(default_factory=dict)
    readonly: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_query_string(cls, query: str) -> 'FormParameters':
        """
        Create form parameters from query string.
        
        Args:
            query: Query string
            
        Returns:
            Form parameters
        """
        params = cls()
        if query:
            # Parse query string
            parsed = urllib.parse.parse_qs(query)
            for key, values in parsed.items():
                if values:
                    # Use first value if multiple values exist
                    params.set(key, values[0])
        return params
    
    def set(self, key: str, value: Any, parameter_type: Optional[ParameterType] = None):
        """
        Set parameter value.
        
        Args:
            key: Parameter key
            value: Parameter value
            parameter_type: Parameter type (auto-detected if not specified)
            
        Raises:
            ValueError: If parameters are readonly
        """
        if self.readonly:
            raise ValueError("Cannot modify readonly parameters")
        
        # Auto-detect parameter type if not specified
        if parameter_type is None:
            if isinstance(value, bool):
                parameter_type = ParameterType.BOOLEAN
            elif isinstance(value, int):
                parameter_type = ParameterType.INTEGER
            elif isinstance(value, float):
                parameter_type = ParameterType.FLOAT
            elif isinstance(value, (list, tuple)):
                parameter_type = ParameterType.LIST
            elif isinstance(value, dict):
                parameter_type = ParameterType.DICT
            elif isinstance(value, datetime):
                parameter_type = ParameterType.DATETIME
            else:
                parameter_type = ParameterType.STRING
        
        self.parameters[key] = Parameter(
            key=key,
            value=value,
            type=parameter_type
        )
    
    def get(
        self,
        key: str,
        default: Any = None,
        parameter_type: Optional[ParameterType] = None
    ) -> Any:
        """
        Get parameter value.
        
        Args:
            key: Parameter key
            default: Default value if parameter not found
            parameter_type: Expected parameter type
            
        Returns:
            Parameter value
            
        Raises:
            ValueError: If parameter type doesn't match expected type
        """
        param = self.parameters.get(key)
        if param is None:
            return default
        
        if parameter_type and param.type != parameter_type:
            raise ValueError(
                f"Parameter '{key}' has type {param.type}, expected {parameter_type}"
            )
        
        return param.value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean parameter value"""
        return self.get(key, default, ParameterType.BOOLEAN)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer parameter value"""
        return self.get(key, default, ParameterType.INTEGER)
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float parameter value"""
        return self.get(key, default, ParameterType.FLOAT)
    
    def get_str(self, key: str, default: str = "") -> str:
        """Get string parameter value"""
        return str(self.get(key, default, ParameterType.STRING))
    
    def get_datetime(self, key: str, default: Optional[datetime] = None) -> Optional[datetime]:
        """Get datetime parameter value"""
        return self.get(key, default, ParameterType.DATETIME)
    
    def get_list(self, key: str, default: Optional[List] = None) -> List:
        """Get list parameter value"""
        return self.get(key, default or [], ParameterType.LIST)
    
    def get_dict(self, key: str, default: Optional[Dict] = None) -> Dict:
        """Get dictionary parameter value"""
        return self.get(key, default or {}, ParameterType.DICT)
    
    def contains(self, key: str) -> bool:
        """Check if parameter exists"""
        return key in self.parameters
    
    def clear(self):
        """Clear all parameters"""
        if self.readonly:
            raise ValueError("Cannot modify readonly parameters")
        self.parameters.clear()
    
    def set_readonly(self):
        """Make parameters readonly"""
        self.readonly = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary"""
        return {
            key: param.value
            for key, param in self.parameters.items()
        }
    
    def to_query_string(self) -> str:
        """Convert parameters to query string"""
        params = {
            key: str(param.value)
            for key, param in self.parameters.items()
        }
        return urllib.parse.urlencode(params)

class FormParameterized(BaseModel, Generic[T]):
    """Model for objects that can be parameterized"""
    parameters: FormParameters = Field(default_factory=FormParameters)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def set_parameters(self, parameters: FormParameters):
        """Set form parameters"""
        self.parameters = parameters
        self.timestamp = datetime.utcnow()
