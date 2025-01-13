from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import logging
import traceback
import json
from datetime import datetime

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)

class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )

class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            message=f"{resource} with id {resource_id} not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "id": resource_id}
        )

class UnauthorizedError(AppError):
    """Unauthorized access error"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )

class ForbiddenError(AppError):
    """Forbidden access error"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN"
        )

async def log_error(
    request: Request,
    error: Exception,
    error_id: str,
    status_code: int
) -> None:
    """Log error details"""
    error_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_id": error_id,
        "status_code": status_code,
        "path": str(request.url),
        "method": request.method,
        "client_ip": request.client.host,
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }

    # Add request details if available
    try:
        body = await request.body()
        if body:
            error_data["request_body"] = body.decode()
    except:
        pass

    # Log error
    if status_code >= 500:
        logger.error(json.dumps(error_data))
    else:
        logger.warning(json.dumps(error_data))

async def error_handler(
    request: Request,
    error: Exception
) -> JSONResponse:
    """Global error handler"""
    error_id = generate_error_id()
    status_code = 500
    error_response = {
        "error_id": error_id,
        "message": "Internal server error"
    }

    if isinstance(error, AppError):
        status_code = error.status_code
        error_response.update({
            "message": error.message,
            "error_code": error.error_code,
            "details": error.details
        })
    elif isinstance(error, RequestValidationError):
        status_code = 422
        error_response.update({
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "details": error.errors()
        })
    elif isinstance(error, HTTPException):
        status_code = error.status_code
        error_response.update({
            "message": error.detail,
            "error_code": f"HTTP_{status_code}"
        })
    elif isinstance(error, SQLAlchemyError):
        error_response.update({
            "message": "Database error",
            "error_code": "DATABASE_ERROR"
        })

    # Log error
    await log_error(request, error, error_id, status_code)

    # Only include error details in development
    if not settings.DEBUG:
        error_response.pop("details", None)

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

def generate_error_id() -> str:
    """Generate unique error ID"""
    import uuid
    return str(uuid.uuid4())

class ErrorTracker:
    """Track and analyze errors"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.error_key_prefix = "errors:"
        self.stats_key_prefix = "error_stats:"

    async def track_error(
        self,
        error_id: str,
        error_data: dict,
        ttl: int = 86400  # 24 hours
    ) -> None:
        """Track error occurrence"""
        # Store error details
        error_key = f"{self.error_key_prefix}{error_id}"
        self.redis.setex(
            error_key,
            ttl,
            json.dumps(error_data)
        )

        # Update error statistics
        error_type = error_data.get("error_type", "unknown")
        stats_key = f"{self.stats_key_prefix}{error_type}"
        pipe = self.redis.pipeline()
        pipe.incr(f"{stats_key}:count")
        pipe.zadd(
            f"{stats_key}:timeline",
            {error_id: error_data["timestamp"]}
        )
        pipe.execute()

    async def get_error(self, error_id: str) -> Optional[dict]:
        """Get error details"""
        error_key = f"{self.error_key_prefix}{error_id}"
        error_data = self.redis.get(error_key)
        return json.loads(error_data) if error_data else None

    async def get_error_stats(
        self,
        error_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """Get error statistics"""
        if error_type:
            return await self._get_type_stats(error_type, start_time, end_time)
        
        # Get stats for all error types
        all_stats = {}
        error_types = self._get_error_types()
        
        for error_type in error_types:
            all_stats[error_type] = await self._get_type_stats(
                error_type,
                start_time,
                end_time
            )
            
        return all_stats

    def _get_error_types(self) -> list:
        """Get all tracked error types"""
        keys = self.redis.keys(f"{self.stats_key_prefix}*:count")
        return [
            key.decode().split(":")[1]
            for key in keys
        ]

    async def _get_type_stats(
        self,
        error_type: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """Get statistics for specific error type"""
        stats_key = f"{self.stats_key_prefix}{error_type}"
        
        # Get total count
        count = int(self.redis.get(f"{stats_key}:count") or 0)
        
        # Get timeline data
        timeline_key = f"{stats_key}:timeline"
        if start_time and end_time:
            timeline = self.redis.zrangebyscore(
                timeline_key,
                start_time.timestamp(),
                end_time.timestamp()
            )
        else:
            timeline = self.redis.zrange(timeline_key, 0, -1)
            
        return {
            "count": count,
            "timeline": [error_id.decode() for error_id in timeline]
        }

    async def cleanup_old_errors(
        self,
        max_age_days: int = 30
    ) -> int:
        """Clean up old error data"""
        cutoff_time = (
            datetime.utcnow() - timedelta(days=max_age_days)
        ).timestamp()
        
        cleaned = 0
        for error_type in self._get_error_types():
            timeline_key = f"{self.stats_key_prefix}{error_type}:timeline"
            old_errors = self.redis.zrangebyscore(
                timeline_key,
                0,
                cutoff_time
            )
            
            if old_errors:
                # Remove from timeline
                self.redis.zremrangebyscore(timeline_key, 0, cutoff_time)
                
                # Remove error details
                self.redis.delete(*[
                    f"{self.error_key_prefix}{error_id.decode()}"
                    for error_id in old_errors
                ])
                
                cleaned += len(old_errors)
                
        return cleaned
