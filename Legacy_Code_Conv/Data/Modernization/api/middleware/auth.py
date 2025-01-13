"""Authentication middleware."""
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import jwt

from core.security.access_control import AccessControlService, Permission, Resource

class AuthSettings:
    """Authentication settings."""
    
    JWT_SECRET: str = "your-secret-key"  # Should be in environment variables
    JWT_ALGORITHM: str = "HS256"
    TOKEN_TYPE: str = "Bearer"

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication and authorization."""

    def __init__(
        self,
        app: ASGIApp,
        settings: AuthSettings,
        access_control: AccessControlService,
        public_paths: set[str] = None
    ):
        """Initialize middleware.
        
        Args:
            app: ASGI application.
            settings: Auth settings.
            access_control: Access control service.
            public_paths: Public paths that don't require auth.
        """
        super().__init__(app)
        self.settings = settings
        self.access_control = access_control
        self.public_paths = public_paths or {"/health", "/metrics", "/docs"}
        self.security = HTTPBearer()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process request and verify authentication.
        
        Args:
            request: HTTP request.
            call_next: Next middleware.
            
        Returns:
            HTTP response.
        """
        if request.url.path in self.public_paths:
            return await call_next(request)

        try:
            # Get token from header
            auth: Optional[HTTPAuthorizationCredentials] = await self.security(request)
            if not auth:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated"
                )

            # Verify token
            payload = jwt.decode(
                auth.credentials,
                self.settings.JWT_SECRET,
                algorithms=[self.settings.JWT_ALGORITHM]
            )

            # Store user info in request state
            request.state.user_id = payload["sub"]
            request.state.user_roles = payload.get("roles", [])

            # Check permissions
            resource = self._get_resource_from_path(request.url.path)
            permission = self._get_permission_from_method(request.method)

            if not await self.access_control.has_permission(
                user_id=request.state.user_id,
                resource=resource,
                permission=permission
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized"
                )

            return await call_next(request)

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

    def _get_resource_from_path(self, path: str) -> Resource:
        """Get resource type from path.
        
        Args:
            path: Request path.
            
        Returns:
            Resource type.
        """
        # Example path mapping
        if "/companies" in path:
            return Resource.COMPANY
        if "/locations" in path:
            return Resource.LOCATION
        if "/sessions" in path:
            return Resource.SESSION
        return Resource.USER

    def _get_permission_from_method(self, method: str) -> Permission:
        """Get permission type from HTTP method.
        
        Args:
            method: HTTP method.
            
        Returns:
            Permission type.
        """
        method_map = {
            "GET": Permission.READ,
            "POST": Permission.WRITE,
            "PUT": Permission.WRITE,
            "PATCH": Permission.WRITE,
            "DELETE": Permission.DELETE
        }
        return method_map.get(method, Permission.READ)
