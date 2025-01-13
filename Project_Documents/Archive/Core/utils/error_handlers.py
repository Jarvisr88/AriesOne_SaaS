"""
Comprehensive error handling system.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

class AppError(Exception):
    """Base application error"""
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class DatabaseError(AppError):
    """Database operation error"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )

class ValidationError(AppError):
    """Data validation error"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )

async def app_error_handler(
    request: Request,
    exc: AppError
) -> JSONResponse:
    """Handle application errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "errors": exc.errors()
                }
            }
        }
    )

async def sqlalchemy_error_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """Handle SQLAlchemy errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database operation failed",
                "details": {
                    "error": str(exc)
                }
            }
        }
    )

async def http_error_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Handle HTTP errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": getattr(exc, "details", {})
            }
        }
    )

def setup_error_handlers(app):
    """Set up error handlers for the application"""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
