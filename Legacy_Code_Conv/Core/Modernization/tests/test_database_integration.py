"""
Database Integration Tests
Version: 1.0.0
Last Updated: 2025-01-10
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.integrations.database import DatabaseIntegration
from core.utils.config import get_settings

settings = get_settings()

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"


@pytest.fixture
async def test_db_session():
    """Create test database session."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
    
    await engine.dispose()


@pytest.fixture
def db_integration(test_db_session):
    """Create database integration instance."""
    return DatabaseIntegration(test_db_session)


@pytest.mark.asyncio
async def test_health_check(db_integration):
    """Test database health check."""
    result = await db_integration.health_check()
    assert result["status"] == "healthy"
    assert "message" in result


@pytest.mark.asyncio
async def test_get_metrics(db_integration):
    """Test database metrics collection."""
    metrics = await db_integration.get_metrics()
    assert "pool_size" in metrics
    assert "checked_out" in metrics
    assert "overflow" in metrics


@pytest.mark.asyncio
async def test_backup_restore(db_integration):
    """Test table backup and restore."""
    # Create test table
    async with db_integration.transaction() as session:
        await session.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name TEXT
            )
        """)
        await session.execute("""
            INSERT INTO test_table (name) VALUES ('test')
        """)
    
    # Test backup
    backup_result = await db_integration.backup_table("test_table")
    assert backup_result is True
    
    # Modify original table
    async with db_integration.transaction() as session:
        await session.execute("""
            UPDATE test_table SET name = 'modified'
        """)
    
    # Test restore
    restore_result = await db_integration.restore_table("test_table")
    assert restore_result is True
    
    # Verify restore
    async with db_integration.transaction() as session:
        result = await session.execute("""
            SELECT name FROM test_table LIMIT 1
        """)
        name = result.scalar()
        assert name == "test"


@pytest.mark.asyncio
async def test_get_table_schema(db_integration):
    """Test schema retrieval."""
    # Create test table
    async with db_integration.transaction() as session:
        await session.execute("""
            CREATE TABLE IF NOT EXISTS test_schema_table (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    schema = await db_integration.get_table_schema("test_schema_table")
    assert schema is not None
    assert schema["table_name"] == "test_schema_table"
    assert len(schema["columns"]) == 3
    
    # Verify column details
    columns = {col["name"]: col for col in schema["columns"]}
    assert "id" in columns
    assert "name" in columns
    assert "created_at" in columns
    assert columns["name"]["nullable"] == "NO"


@pytest.mark.asyncio
async def test_transaction_rollback(db_integration):
    """Test transaction rollback on error."""
    # Create test table
    async with db_integration.transaction() as session:
        await session.execute("""
            CREATE TABLE IF NOT EXISTS test_rollback (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
    
    # Test transaction rollback
    with pytest.raises(Exception):
        async with db_integration.transaction() as session:
            await session.execute("""
                INSERT INTO test_rollback (name) VALUES ('test')
            """)
            raise Exception("Test rollback")
    
    # Verify rollback
    async with db_integration.transaction() as session:
        result = await session.execute("""
            SELECT COUNT(*) FROM test_rollback
        """)
        count = result.scalar()
        assert count == 0


@pytest.mark.asyncio
async def test_get_related_entities(db_integration):
    """Test related entities retrieval."""
    # Create test tables
    async with db_integration.transaction() as session:
        await session.execute("""
            CREATE TABLE IF NOT EXISTS test_parent (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        await session.execute("""
            CREATE TABLE IF NOT EXISTS test_child (
                id SERIAL PRIMARY KEY,
                parent_id INTEGER REFERENCES test_parent(id),
                name TEXT NOT NULL
            )
        """)
        
        # Insert test data
        await session.execute("""
            INSERT INTO test_parent (name) VALUES ('parent')
            RETURNING id
        """)
        parent_id = (await session.execute(
            "SELECT lastval()"
        )).scalar()
        
        await session.execute("""
            INSERT INTO test_child (parent_id, name)
            VALUES (:parent_id, 'child')
        """, {"parent_id": parent_id})
    
    # Test related entities retrieval
    parent = await db_integration.get_related_entities(
        parent_id,
        ["test_child"]
    )
    assert parent is not None
    assert len(parent.children) == 1
    assert parent.children[0].name == "child"
