"""
Tests for the database abstraction layer.
"""
import pytest
import asyncio
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from ..core.database import Base, Database, DatabaseConfig, Repository
from ..core.unit_of_work import UnitOfWork

# Test model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Test configuration
@pytest.fixture
def db_config():
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="test_db",
        user="test_user",
        password="test_password",
        echo=True
    )

@pytest.fixture
def database(db_config):
    return Database(db_config)

@pytest.fixture
def user_repository(database):
    return Repository(database, User)

@pytest.mark.asyncio
async def test_database_health_check(database):
    """Test database health check."""
    is_healthy = await database.health_check()
    assert is_healthy == True

@pytest.mark.asyncio
async def test_create_user(user_repository):
    """Test user creation."""
    user = await user_repository.create(
        username="testuser",
        email="test@example.com"
    )
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_user(user_repository):
    """Test user retrieval."""
    # Create test user
    user = await user_repository.create(
        username="getuser",
        email="get@example.com"
    )
    
    # Retrieve user
    retrieved_user = await user_repository.get(user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.username == "getuser"

@pytest.mark.asyncio
async def test_update_user(user_repository):
    """Test user update."""
    # Create test user
    user = await user_repository.create(
        username="updateuser",
        email="update@example.com"
    )
    
    # Update user
    updated_user = await user_repository.update(
        user.id,
        email="updated@example.com"
    )
    assert updated_user is not None
    assert updated_user.email == "updated@example.com"

@pytest.mark.asyncio
async def test_delete_user(user_repository):
    """Test user deletion."""
    # Create test user
    user = await user_repository.create(
        username="deleteuser",
        email="delete@example.com"
    )
    
    # Delete user
    deleted = await user_repository.delete(user.id)
    assert deleted == True
    
    # Verify deletion
    retrieved_user = await user_repository.get(user.id)
    assert retrieved_user is None

@pytest.mark.asyncio
async def test_list_users(user_repository):
    """Test user listing."""
    # Create test users
    users = []
    for i in range(5):
        user = await user_repository.create(
            username=f"listuser{i}",
            email=f"list{i}@example.com"
        )
        users.append(user)
    
    # List users
    retrieved_users = await user_repository.list(skip=0, limit=10)
    assert len(retrieved_users) >= 5

@pytest.mark.asyncio
async def test_unit_of_work(database):
    """Test unit of work pattern."""
    async with UnitOfWork(database) as uow:
        # Create user within transaction
        user_repo = uow.repository(User)
        user = await user_repo.create(
            username="uowuser",
            email="uow@example.com"
        )
        assert user.id is not None
        
        # Verify user exists after commit
        retrieved_user = await user_repo.get(user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == "uowuser"
