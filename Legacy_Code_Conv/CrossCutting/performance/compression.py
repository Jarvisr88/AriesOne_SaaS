"""Compression middleware module."""

from typing import Callable
import gzip
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for handling response compression."""
    
    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 500,
        compressible_types: set = None
    ):
        """Initialize compression middleware."""
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compressible_types = compressible_types or {
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'application/xml',
            'text/xml',
            'text/plain',
        }
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process the request."""
        # Check if client accepts gzip encoding
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' not in accept_encoding.lower():
            return await call_next(request)
        
        response = await call_next(request)
        
        # Check if response should be compressed
        content_type = response.headers.get('Content-Type', '').split(';')[0]
        content_encoding = response.headers.get('Content-Encoding', '')
        
        if (
            content_type in self.compressible_types
            and not content_encoding
            and len(response.body) >= self.minimum_size
        ):
            # Compress response
            compressed_body = gzip.compress(response.body)
            
            # Update headers
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = str(len(compressed_body))
            response.headers['Vary'] = 'Accept-Encoding'
            
            # Create new response with compressed body
            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        return response
