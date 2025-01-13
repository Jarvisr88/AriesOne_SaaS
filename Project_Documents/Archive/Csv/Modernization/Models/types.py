"""
Type definitions for CSV processing module.
"""
from typing import Dict, List, Optional, Any, Union, TypeVar, Generic
from enum import Enum
from datetime import datetime

# Type variables
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Custom types
FilePath = str
RowData = Dict[str, Any]
Headers = List[str]
RowIndex = int
ColumnName = str
ErrorMessage = str

# Enums
class ImportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ErrorSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ParseErrorAction(str, Enum):
    SKIP = "skip"
    ABORT = "abort"
    CONTINUE = "continue"

class ValidationResult(Generic[T]):
    """Generic validation result container."""
    def __init__(
        self,
        is_valid: bool,
        data: Optional[T] = None,
        errors: Optional[List[str]] = None
    ):
        self.is_valid = is_valid
        self.data = data
        self.errors = errors or []

# Type aliases for specific use cases
ImportId = int
ErrorId = int
ConfigDict = Dict[str, Any]
ValidationErrors = List[str]
ProcessingResult = Dict[str, Any]
TransformationFunc = callable
ValidationFunc = callable
