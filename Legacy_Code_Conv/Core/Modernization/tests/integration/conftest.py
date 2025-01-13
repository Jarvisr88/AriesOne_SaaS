"""
Integration Test Configuration Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
import asyncio
import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                  async_sessionmaker, create_async_engine)

from core.auth import AuthMiddleware
from core.auth.dependencies import get_session
from core.database import Base
from core.database.models import Tenant, User
from core.utils.config import get_settings
from core.utils.security import get_password_hash

settings = get_settings()

# Test database URL
TEST_DB_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create database engine."""
    engine = create_async_engine(TEST_DB_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create session factory."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


@pytest_asyncio.fixture
async def session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """Create database session."""
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def app(session_factory: async_sessionmaker[AsyncSession]) -> FastAPI:
    """Create FastAPI application."""
    from core.api import inventory_router, order_router, tenant_router
    from core.auth.routes import router as auth_router

    app = FastAPI(title="Core API")
    
    # Add middleware
    app.add_middleware(AuthMiddleware)
    
    # Override session dependency
    async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session
    
    app.dependency_overrides[get_session] = get_test_session
    
    # Add routers
    app.include_router(auth_router)
    app.include_router(tenant_router)
    app.include_router(inventory_router)
    app.include_router(order_router)
    
    return app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_tenant(session: AsyncSession) -> Tenant:
    """Create test tenant."""
    tenant = Tenant(
        name="Test Tenant",
        slug="test-tenant",
        subscription_plan="premium",
        max_users=10,
        max_storage=1073741824,  # 1GB
        used_storage=0
    )
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    return tenant


@pytest_asyncio.fixture
async def test_superuser(session: AsyncSession, test_tenant: Tenant) -> User:
    """Create test superuser."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        tenant_id=test_tenant.id,
        first_name="Admin",
        last_name="User"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user(session: AsyncSession, test_tenant: Tenant) -> User:
    """Create test user."""
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("user123"),
        is_active=True,
        is_superuser=False,
        tenant_id=test_tenant.id,
        first_name="Test",
        last_name="User"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def superuser_token(client: AsyncClient, test_superuser: User) -> str:
    """Get superuser token."""
    response = await client.post(
        "/auth/token",
        data={
            "username": test_superuser.email,
            "password": "admin123"
        }
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def user_token(client: AsyncClient, test_user: User) -> str:
    """Get user token."""
    response = await client.post(
        "/auth/token",
        data={
            "username": test_user.email,
            "password": "user123"
        }
    )
    return response.json()["access_token"]
