"""
Integration tests for specialized repositories.
Tests the repository implementations against a real PostgreSQL database.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import Database, DatabaseConfig
from ..core.unit_of_work import UnitOfWork
from ..repositories.models import (
    User, Company, Location, PriceList, PriceListItem, Role, UserRole
)
from ..repositories.user_repository import UserRepository
from ..repositories.company_repository import CompanyRepository
from ..repositories.price_repository import PriceRepository

# Test configuration
@pytest.fixture
def db_config():
    """Create test database configuration."""
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="test_db",
        user="test_user",
        password="test_password",
        min_pool_size=5,
        max_pool_size=20
    )

@pytest.fixture
async def database(db_config) -> AsyncGenerator[Database, None]:
    """Create test database instance."""
    db = Database(db_config)
    yield db
    await db.engine.dispose()

@pytest.fixture
async def session(database) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with database.session() as session:
        yield session

@pytest.fixture
async def company_repository(database) -> CompanyRepository:
    """Create company repository instance."""
    return CompanyRepository(database)

@pytest.fixture
async def user_repository(database) -> UserRepository:
    """Create user repository instance."""
    return UserRepository(database)

@pytest.fixture
async def price_repository(database) -> PriceRepository:
    """Create price repository instance."""
    return PriceRepository(database)

@pytest.fixture
async def test_company(company_repository) -> Company:
    """Create test company."""
    company = await company_repository.create(
        name="Test Company",
        code="TEST001",
        created_by="system",
        updated_by="system"
    )
    return company

@pytest.fixture
async def test_user(user_repository, test_company) -> User:
    """Create test user."""
    user = await user_repository.create(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        company_id=test_company.id,
        created_by="system",
        updated_by="system"
    )
    return user

@pytest.mark.asyncio
async def test_company_creation(company_repository):
    """Test company creation and retrieval."""
    company = await company_repository.create(
        name="New Company",
        code="NEW001",
        created_by="system",
        updated_by="system"
    )
    assert company.id is not None
    assert company.name == "New Company"
    assert company.code == "NEW001"

    # Test retrieval
    retrieved = await company_repository.get(company.id)
    assert retrieved is not None
    assert retrieved.id == company.id

@pytest.mark.asyncio
async def test_company_locations(company_repository, test_company):
    """Test company location management."""
    # Add location
    location = await company_repository.add_location(
        company_id=test_company.id,
        name="Main Office",
        address_line1="123 Main St",
        city="Test City",
        state="TX",
        zip_code="12345",
        created_by="system"
    )
    assert location.id is not None
    assert location.company_id == test_company.id

    # Get locations
    locations = await company_repository.get_locations(test_company.id)
    assert len(locations) == 1
    assert locations[0].name == "Main Office"

@pytest.mark.asyncio
async def test_user_management(user_repository, test_company):
    """Test user creation and role management."""
    # Create user
    user = await user_repository.create(
        username="roleuser",
        email="role@example.com",
        password_hash="hashed_password",
        company_id=test_company.id,
        created_by="system",
        updated_by="system"
    )
    assert user.id is not None

    # Create role
    async with user_repository.db.session() as session:
        role = Role(
            name="TEST_ROLE",
            description="Test role",
            created_by="system",
            updated_by="system"
        )
        session.add(role)
        await session.commit()

    # Add role to user
    await user_repository.add_role(user.id, role.id, "system")

    # Get user roles
    roles = await user_repository.get_user_roles(user.id)
    assert len(roles) == 1
    assert roles[0].name == "TEST_ROLE"

@pytest.mark.asyncio
async def test_price_list_management(price_repository, test_company):
    """Test price list and item management."""
    # Create price list
    price_list = await price_repository.create(
        company_id=test_company.id,
        name="Standard Prices",
        code="STD001",
        effective_date=datetime.utcnow(),
        created_by="system",
        updated_by="system"
    )
    assert price_list.id is not None

    # Add items
    async with price_repository.db.session() as session:
        items = [
            PriceListItem(
                price_list_id=price_list.id,
                item_code=f"ITEM{i}",
                description=f"Test Item {i}",
                unit_price=i * 1000,
                created_by="system",
                updated_by="system"
            )
            for i in range(1, 4)
        ]
        session.add_all(items)
        await session.commit()

    # Get items
    items = await price_repository.get_price_list_items(price_list.id)
    assert len(items) == 3

    # Get active price list
    active_list = await price_repository.get_active_price_list(test_company.id)
    assert active_list is not None
    assert active_list.id == price_list.id

@pytest.mark.asyncio
async def test_unit_of_work(database, test_company):
    """Test unit of work pattern with multiple operations."""
    async with UnitOfWork(database) as uow:
        # Create price list
        price_repo = uow.repository(PriceList)
        price_list = await price_repo.create(
            company_id=test_company.id,
            name="UOW Test Prices",
            code="UOW001",
            effective_date=datetime.utcnow(),
            created_by="system",
            updated_by="system"
        )

        # Create items
        item_repo = uow.repository(PriceListItem)
        for i in range(1, 4):
            await item_repo.create(
                price_list_id=price_list.id,
                item_code=f"UOW{i}",
                description=f"UOW Item {i}",
                unit_price=i * 1000,
                created_by="system",
                updated_by="system"
            )

    # Verify outside transaction
    price_repo = PriceRepository(database)
    items = await price_repo.get_price_list_items(price_list.id)
    assert len(items) == 3
