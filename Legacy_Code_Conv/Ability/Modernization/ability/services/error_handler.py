"""
Error Handler Module

This module provides comprehensive error handling for external integrations.
"""
from datetime import datetime
import json
from typing import Dict, Optional, Type
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from ..monitoring.telemetry import TelemetryService


class IntegrationError(Exception):
    """Base class for integration errors."""
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class PayerError(IntegrationError):
    """Error from payer systems."""
    pass


class NetworkError(IntegrationError):
    """Network-related errors."""
    pass


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error_code: str
    message: str
    timestamp: datetime
    trace_id: UUID
    details: Optional[Dict] = None


class ErrorHandler:
    """Handler for integration errors."""

    def __init__(self, telemetry: TelemetryService):
        """Initialize error handler."""
        self.telemetry = telemetry
        self.error_mappings = {
            # Medicare HETS errors
            "HETS001": ("Invalid Medicare ID", status.HTTP_400_BAD_REQUEST),
            "HETS002": ("Service temporarily unavailable", status.HTTP_503_SERVICE_UNAVAILABLE),
            "HETS003": ("Invalid provider NPI", status.HTTP_400_BAD_REQUEST),
            
            # Medicaid errors
            "MCD001": ("Invalid Medicaid ID", status.HTTP_400_BAD_REQUEST),
            "MCD002": ("State system unavailable", status.HTTP_503_SERVICE_UNAVAILABLE),
            "MCD003": ("Provider not enrolled", status.HTTP_403_FORBIDDEN),
            
            # Private payer errors
            "PRV001": ("Member not found", status.HTTP_404_NOT_FOUND),
            "PRV002": ("Service not responding", status.HTTP_503_SERVICE_UNAVAILABLE),
            "PRV003": ("Invalid credentials", status.HTTP_401_UNAUTHORIZED),
            
            # Network errors
            "NET001": ("Connection timeout", status.HTTP_504_GATEWAY_TIMEOUT),
            "NET002": ("Service unavailable", status.HTTP_503_SERVICE_UNAVAILABLE),
            "NET003": ("Rate limit exceeded", status.HTTP_429_TOO_MANY_REQUESTS)
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(NetworkError)
    )
    async def handle_request(self, func, *args, **kwargs):
        """Handle requests with retry logic."""
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            await self._handle_exception(e)

    async def _handle_exception(self, exc: Exception):
        """Handle different types of exceptions."""
        if isinstance(exc, IntegrationError):
            error_info = self.error_mappings.get(
                exc.error_code,
                ("Unknown error", status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
            
            await self.telemetry.log_error(
                "integration_error",
                exc.message,
                {
                    "error_code": exc.error_code,
                    "details": exc.details
                }
            )
            
            raise HTTPException(
                status_code=error_info[1],
                detail=ErrorResponse(
                    error_code=exc.error_code,
                    message=error_info[0],
                    timestamp=datetime.utcnow(),
                    trace_id=UUID(self.telemetry.current_trace_id),
                    details=exc.details
                ).dict()
            )
        else:
            await self.telemetry.log_error(
                "unexpected_error",
                str(exc)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error_code="SYS001",
                    message="An unexpected error occurred",
                    timestamp=datetime.utcnow(),
                    trace_id=UUID(self.telemetry.current_trace_id)
                ).dict()
            )

    async def handle_failover(
        self,
        primary_func,
        backup_func,
        *args,
        **kwargs
    ):
        """Handle failover between primary and backup systems."""
        try:
            return await primary_func(*args, **kwargs)
        except Exception as primary_exc:
            await self.telemetry.log_warning(
                "failover_triggered",
                str(primary_exc)
            )
            try:
                return await backup_func(*args, **kwargs)
            except Exception as backup_exc:
                await self.telemetry.log_error(
                    "failover_failed",
                    str(backup_exc)
                )
                raise
