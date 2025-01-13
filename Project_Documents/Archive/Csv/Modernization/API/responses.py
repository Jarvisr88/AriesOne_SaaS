"""
Response models and handlers for CSV processing API endpoints.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from ..Models.types import ImportStatus, ErrorSeverity

class ImportResponse(BaseModel):
    """Response model for import operations."""
    import_id: int
    status: ImportStatus
    message: str

class ImportStatusResponse(BaseModel):
    """Response model for import status."""
    import_id: int
    status: ImportStatus
    filename: str
    row_count: Optional[int]
    error_count: Optional[int]
    created_at: datetime
    updated_at: datetime

class ImportError(BaseModel):
    """Model for import error details."""
    row: Optional[int]
    column: Optional[str]
    message: str
    severity: ErrorSeverity
    raw_data: Optional[str]
    created_at: datetime

class ImportErrorsResponse(BaseModel):
    """Response model for import errors."""
    import_id: int
    total_errors: int
    errors: List[ImportError]

class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""
    detail: str
    errors: List[str]

class CancelResponse(BaseModel):
    """Response model for import cancellation."""
    import_id: int
    status: ImportStatus
    message: str

def create_import_response(
    import_id: int,
    status: ImportStatus,
    message: str
) -> Dict[str, Any]:
    """Create response for import creation."""
    return ImportResponse(
        import_id=import_id,
        status=status,
        message=message
    ).dict()

def create_status_response(import_record: Any) -> Dict[str, Any]:
    """Create response for import status."""
    return ImportStatusResponse(
        import_id=import_record.id,
        status=import_record.status,
        filename=import_record.filename,
        row_count=import_record.row_count,
        error_count=import_record.error_count,
        created_at=import_record.created_at,
        updated_at=import_record.updated_at
    ).dict()

def create_errors_response(
    import_id: int,
    total_errors: int,
    errors: List[Any]
) -> Dict[str, Any]:
    """Create response for import errors."""
    error_list = [
        ImportError(
            row=error.row,
            column=error.column,
            message=error.message,
            severity=error.severity,
            raw_data=error.raw_data,
            created_at=error.created_at
        ) for error in errors
    ]
    
    return ImportErrorsResponse(
        import_id=import_id,
        total_errors=total_errors,
        errors=error_list
    ).dict()

def create_validation_error_response(
    message: str,
    errors: List[str]
) -> Dict[str, Any]:
    """Create response for validation errors."""
    return ValidationErrorResponse(
        detail=message,
        errors=errors
    ).dict()

def create_cancel_response(
    import_id: int,
    status: ImportStatus,
    message: str
) -> Dict[str, Any]:
    """Create response for import cancellation."""
    return CancelResponse(
        import_id=import_id,
        status=status,
        message=message
    ).dict()
