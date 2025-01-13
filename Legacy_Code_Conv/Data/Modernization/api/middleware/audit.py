"""Audit middleware for request logging."""
import time
from typing import Callable
from uuid import UUID
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.security.audit import AuditService

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging."""

    def __init__(
        self,
        app: ASGIApp,
        audit_service: AuditService,
        exclude_paths: set[str] = None
    ):
        """Initialize middleware.
        
        Args:
            app: ASGI application.
            audit_service: Audit service.
            exclude_paths: Paths to exclude from audit logging.
        """
        super().__init__(app)
        self.audit_service = audit_service
        self.exclude_paths = exclude_paths or {"/health", "/metrics"}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process request and log audit event.
        
        Args:
            request: HTTP request.
            call_next: Next middleware.
            
        Returns:
            HTTP response.
        """
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        start_time = time.time()
        
        # Get user ID from request state (set by auth middleware)
        user_id: UUID = getattr(request.state, "user_id", None)
        
        try:
            response = await call_next(request)
            
            # Log successful request
            await self.audit_service.log_event(
                event_type="API_REQUEST",
                entity_type="http_request",
                entity_id=str(request.url),
                user_id=user_id,
                action=request.method,
                metadata={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": round((time.time() - start_time) * 1000),
                    "client_ip": request.client.host,
                    "user_agent": request.headers.get("user-agent")
                }
            )
            
            return response
            
        except Exception as e:
            # Log failed request
            await self.audit_service.log_event(
                event_type="API_ERROR",
                entity_type="http_request",
                entity_id=str(request.url),
                user_id=user_id,
                action=request.method,
                metadata={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e),
                    "duration_ms": round((time.time() - start_time) * 1000),
                    "client_ip": request.client.host,
                    "user_agent": request.headers.get("user-agent")
                }
            )
            raise
