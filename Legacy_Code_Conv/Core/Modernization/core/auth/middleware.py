"""
Authentication Middleware Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from typing import Optional
from uuid import UUID

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..database import get_session
from ..security import AuthenticationService
from ..utils.config import get_settings

settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through middleware."""
        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)

        # Get token from header
        token = self._get_token_from_header(request)
        if not token:
            return await call_next(request)

        # Verify token
        user = await self._verify_token(token)
        if user:
            # Attach user to request state
            request.state.user = user
            request.state.token = token

        return await call_next(request)

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public."""
        public_paths = [
            "/auth/register",
            "/auth/token",
            "/auth/refresh",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        return any(path.startswith(p) for p in public_paths)

    def _get_token_from_header(self, request: Request) -> Optional[str]:
        """Extract token from Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header.split(" ")[1]

    async def _verify_token(self, token: str) -> Optional[UUID]:
        """Verify JWT token."""
        async with get_session() as session:
            auth_service = AuthenticationService(session)
            return await auth_service.verify_token(token)
