"""Application startup module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .core.logging import setup_logging
from .config.settings import get_settings
from .api.v1.api import api_router

settings = get_settings()

def create_app() -> FastAPI:
    """Create FastAPI application."""
    # Configure logging
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs" if settings.ENABLE_DOCS else None,
        redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENABLE_DOCS else None,
    )
    
    # Configure CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add security middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        same_site="lax",
        https_only=True
    )
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.on_event("startup")
    async def startup_event():
        """Handle startup events."""
        # Initialize database
        from .core.database import Base, engine
        Base.metadata.create_all(bind=engine)
        
        # Initialize Redis connection
        from redis import Redis
        app.state.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Initialize background tasks
        from .core.tasks import init_background_tasks
        await init_background_tasks()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Handle shutdown events."""
        # Close Redis connection
        await app.state.redis.close()
        
        # Close database connections
        from .core.database import engine
        engine.dispose()
    
    return app
