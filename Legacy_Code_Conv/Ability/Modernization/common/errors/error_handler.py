"""
Error Handling Framework

Provides a unified error handling system for the entire application.
"""
from datetime import datetime
import traceback
from typing import Any, Dict, Optional, Type
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from ..config import get_settings
from ..monitoring.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None
    method: Optional[str] = None
    trace_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class BaseError(Exception):
    """Base error class."""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

class ValidationError(BaseError):
    """Validation error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize validation error."""
        super().__init__(
            "VALIDATION_ERROR",
            message,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            details
        )

class NotFoundError(BaseError):
    """Not found error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize not found error."""
        super().__init__(
            "NOT_FOUND",
            message,
            status.HTTP_404_NOT_FOUND,
            details
        )

class AuthenticationError(BaseError):
    """Authentication error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize authentication error."""
        super().__init__(
            "AUTHENTICATION_ERROR",
            message,
            status.HTTP_401_UNAUTHORIZED,
            details
        )

class AuthorizationError(BaseError):
    """Authorization error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize authorization error."""
        super().__init__(
            "AUTHORIZATION_ERROR",
            message,
            status.HTTP_403_FORBIDDEN,
            details
        )

class BusinessError(BaseError):
    """Business logic error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize business error."""
        super().__init__(
            "BUSINESS_ERROR",
            message,
            status.HTTP_400_BAD_REQUEST,
            details
        )

class TechnicalError(BaseError):
    """Technical error."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize technical error."""
        super().__init__(
            "TECHNICAL_ERROR",
            message,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            details
        )

class ErrorHandler:
    """Handles application errors."""
    
    def __init__(self, app: FastAPI):
        """Initialize error handler."""
        self.app = app
        self._setup_error_handlers()
        self._setup_sentry()

    def _setup_sentry(self):
        """Setup Sentry integration."""
        if settings.SENTRY_DSN:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                traces_sample_rate=1.0
            )
            self.app.add_middleware(SentryAsgiMiddleware)

    def _setup_error_handlers(self):
        """Setup error handlers."""
        
        @self.app.exception_handler(BaseError)
        async def handle_base_error(
            request: Request,
            exc: BaseError
        ) -> JSONResponse:
            """Handle base errors."""
            error = ErrorDetail(
                code=exc.code,
                message=exc.message,
                path=str(request.url),
                method=request.method,
                trace_id=request.headers.get("X-Request-ID"),
                details=exc.details
            )
            
            logger.error(
                f"Error occurred: {error.dict()}",
                extra={"error": error.dict()}
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error.dict()
            )

        @self.app.exception_handler(Exception)
        async def handle_unhandled_error(
            request: Request,
            exc: Exception
        ) -> JSONResponse:
            """Handle unhandled errors."""
            error = ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                path=str(request.url),
                method=request.method,
                trace_id=request.headers.get("X-Request-ID"),
                details={
                    "error_type": type(exc).__name__,
                    "traceback": traceback.format_exc()
                }
            )
            
            logger.error(
                f"Unhandled error occurred: {error.dict()}",
                extra={"error": error.dict()}
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error.dict()
            )

    def create_error(
        self,
        error_type: Type[BaseError],
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> BaseError:
        """
        Create error instance.
        
        Args:
            error_type: Error class
            message: Error message
            details: Optional error details
            
        Returns:
            Error instance
        """
        return error_type(message, details)

error_handler: Optional[ErrorHandler] = None

def setup_error_handling(app: FastAPI) -> ErrorHandler:
    """
    Setup error handling for application.
    
    Args:
        app: FastAPI application
        
    Returns:
        Error handler instance
    """
    global error_handler
    if not error_handler:
        error_handler = ErrorHandler(app)
    return error_handler

def get_error_handler() -> ErrorHandler:
    """
    Get error handler instance.
    
    Returns:
        Error handler instance
    """
    if not error_handler:
        raise RuntimeError("Error handler not initialized")
    return error_handler
