"""
Middleware components for PriceUtilities API.
"""
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import jwt
from datetime import datetime

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication and user context"""
    
    def __init__(
        self,
        app,
        secret_key: str,
        exclude_paths: list[str] = None
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.exclude_paths = exclude_paths or []
        
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process each request for authentication"""
        
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
            
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid authentication token"}
            )
            
        token = auth_header.split(' ')[1]
        
        try:
            # Verify and decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            # Add user information to request state
            request.state.user_id = payload.get('sub')
            request.state.user_roles = payload.get('roles', [])
            
            return await call_next(request)
            
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"error": "Token has expired"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Log request and response details"""
        
        start_time = time.time()
        
        # Generate request ID
        request_id = f"{int(start_time)}-{id(request)}"
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'client_host': request.client.host,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Response {request_id}: {response.status_code} ({process_time:.3f}s)",
                extra={
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'process_time': process_time,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Add processing time header
            response.headers['X-Process-Time'] = str(process_time)
            return response
            
        except Exception as e:
            logger.error(
                f"Error processing request {request_id}: {str(e)}",
                extra={
                    'request_id': request_id,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                },
                exc_info=True
            )
            raise

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling"""
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Handle errors and return consistent response format"""
        
        try:
            return await call_next(request)
            
        except Exception as e:
            # Log the error
            logger.error(
                f"Unhandled error: {str(e)}",
                extra={
                    'path': request.url.path,
                    'method': request.method,
                    'timestamp': datetime.utcnow().isoformat()
                },
                exc_info=True
            )
            
            # Determine status code
            status_code = 500
            if hasattr(e, 'status_code'):
                status_code = e.status_code
                
            # Create error response
            error_response = {
                "error": str(e),
                "code": f"ERR_{status_code}",
                "request_id": getattr(request.state, 'request_id', None)
            }
            
            return JSONResponse(
                status_code=status_code,
                content=error_response
            )
