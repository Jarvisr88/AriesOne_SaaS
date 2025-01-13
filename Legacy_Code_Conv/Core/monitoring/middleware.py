"""
Monitoring middleware module.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time
import uuid
from .logger import Logger
from ..auth.login_form import LoginManager

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for request monitoring and logging."""
    
    def __init__(self, app, logger: Logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Response:
        """Process request and log details."""
        # Generate request ID if not present
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Get current user if authenticated
        try:
            user = await LoginManager.get_current_user(request)
            username = user.username if user else None
        except:
            username = None
        
        # Add request ID to response headers
        response = Response()
        response.headers['X-Request-ID'] = request_id
        
        # Log request and response
        return await self.logger.log_request(
            request,
            response,
            username
        )
