"""Security middleware module."""

from typing import Optional, Callable
from fastapi import Request, Response
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp
from app.core.config import settings
from .services import SecurityService

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for handling security concerns."""
    
    def __init__(
        self,
        app: ASGIApp,
        security_service: SecurityService,
        exclude_paths: Optional[list] = None
    ):
        """Initialize security middleware."""
        super().__init__(app)
        self.security_service = security_service
        self.exclude_paths = exclude_paths or []
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process the request."""
        # Skip security checks for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Extract and validate token
        token = await self._get_token(request)
        if token:
            try:
                user = await self.security_service.get_current_user(token)
                request.state.user = user
            except Exception:
                return Response(
                    status_code=401,
                    content="Invalid authentication credentials"
                )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        
        return response
    
    async def _get_token(self, request: Request) -> Optional[str]:
        """Extract token from request."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            return None
        
        return token

def setup_security_middleware(app: ASGIApp) -> None:
    """Setup security middleware."""
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add rate limiting middleware
    if settings.RATE_LIMIT_ENABLED:
        from .rate_limit import RateLimitMiddleware
        app.add_middleware(
            RateLimitMiddleware,
            rate_limit=settings.RATE_LIMIT,
            rate_limit_period=settings.RATE_LIMIT_PERIOD,
        )
    
    # Add security middleware
    app.add_middleware(
        SecurityMiddleware,
        security_service=SecurityService,
        exclude_paths=[
            "/docs",
            "/redoc",
            "/openapi.json",
            "/token",
        ],
    )
