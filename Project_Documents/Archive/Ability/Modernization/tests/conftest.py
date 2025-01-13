import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.db.base import Base
from app.core.config import settings
from app.models.core import (
    Tenant,
    Company,
    User,
    TenantStatus,
    SubscriptionTier,
    AuthProvider
)

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection
    )
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides = {}
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def test_tenant(db) -> Tenant:
    tenant = Tenant(
        name="Test Tenant",
        domain="test.example.com",
        status=TenantStatus.ACTIVE,
        subscription_tier=SubscriptionTier.PROFESSIONAL,
        settings={},
        features={}
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

@pytest.fixture(scope="function")
def test_company(db, test_tenant) -> Company:
    company = Company(
        tenant_id=test_tenant.id,
        name="Test Company",
        domain="company.test.example.com",
        settings={},
        features={}
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@pytest.fixture(scope="function")
def test_user(db, test_company) -> User:
    user = User(
        company_id=test_company.id,
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        status="active",
        auth_provider=AuthProvider.LOCAL
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(db, test_company) -> User:
    admin = User(
        company_id=test_company.id,
        email="admin@example.com",
        full_name="Test Admin",
        hashed_password="hashed_password",
        status="active",
        auth_provider=AuthProvider.LOCAL,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def token_headers(test_user) -> Dict[str, str]:
    access_token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def admin_token_headers(test_admin) -> Dict[str, str]:
    access_token = create_access_token(
        data={"sub": str(test_admin.id)},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
