"""
Schema validation tests for the database models.
Ensures that all models are properly configured and constraints are enforced.
"""
import pytest
from sqlalchemy import inspect, text
from ..repositories.models import (
    Base, User, Company, Location, PriceList, 
    PriceListItem, Role, UserRole
)

def get_table_names(engine):
    """Get all table names from the database."""
    return inspect(engine).get_table_names()

def get_foreign_keys(engine, table_name):
    """Get foreign key constraints for a table."""
    insp = inspect(engine)
    return insp.get_foreign_keys(table_name)

def get_indexes(engine, table_name):
    """Get indexes for a table."""
    insp = inspect(engine)
    return insp.get_indexes(table_name)

def get_unique_constraints(engine, table_name):
    """Get unique constraints for a table."""
    insp = inspect(engine)
    return insp.get_unique_constraints(table_name)

@pytest.mark.asyncio
async def test_all_tables_created(database):
    """Test that all models are properly mapped to database tables."""
    async with database.engine.begin() as conn:
        tables = await conn.run_sync(get_table_names)
        
        expected_tables = {
            "users",
            "companies",
            "locations",
            "price_lists",
            "price_list_items",
            "roles",
            "user_roles"
        }
        
        assert set(tables) == expected_tables

@pytest.mark.asyncio
async def test_user_constraints(database):
    """Test User model constraints."""
    async with database.engine.begin() as conn:
        # Check foreign keys
        fks = await conn.run_sync(lambda sync_conn: get_foreign_keys(sync_conn, "users"))
        assert any(fk["referred_table"] == "companies" for fk in fks)
        
        # Check unique constraints
        uniques = await conn.run_sync(lambda sync_conn: get_unique_constraints(sync_conn, "users"))
        unique_columns = {c for u in uniques for c in u["column_names"]}
        assert "username" in unique_columns
        assert "email" in unique_columns

@pytest.mark.asyncio
async def test_company_constraints(database):
    """Test Company model constraints."""
    async with database.engine.begin() as conn:
        # Check unique constraints
        uniques = await conn.run_sync(lambda sync_conn: get_unique_constraints(sync_conn, "companies"))
        unique_columns = {c for u in uniques for c in u["column_names"]}
        assert "code" in unique_columns

@pytest.mark.asyncio
async def test_location_constraints(database):
    """Test Location model constraints."""
    async with database.engine.begin() as conn:
        # Check foreign keys
        fks = await conn.run_sync(lambda sync_conn: get_foreign_keys(sync_conn, "locations"))
        assert any(fk["referred_table"] == "companies" for fk in fks)

@pytest.mark.asyncio
async def test_price_list_constraints(database):
    """Test PriceList model constraints."""
    async with database.engine.begin() as conn:
        # Check foreign keys
        fks = await conn.run_sync(lambda sync_conn: get_foreign_keys(sync_conn, "price_lists"))
        assert any(fk["referred_table"] == "companies" for fk in fks)
        
        # Check unique constraints
        uniques = await conn.run_sync(lambda sync_conn: get_unique_constraints(sync_conn, "price_lists"))
        unique_columns = {c for u in uniques for c in u["column_names"]}
        assert "code" in unique_columns

@pytest.mark.asyncio
async def test_price_list_item_constraints(database):
    """Test PriceListItem model constraints."""
    async with database.engine.begin() as conn:
        # Check foreign keys
        fks = await conn.run_sync(lambda sync_conn: get_foreign_keys(sync_conn, "price_list_items"))
        assert any(fk["referred_table"] == "price_lists" for fk in fks)

@pytest.mark.asyncio
async def test_user_role_constraints(database):
    """Test UserRole model constraints."""
    async with database.engine.begin() as conn:
        # Check foreign keys
        fks = await conn.run_sync(lambda sync_conn: get_foreign_keys(sync_conn, "user_roles"))
        assert any(fk["referred_table"] == "users" for fk in fks)
        assert any(fk["referred_table"] == "roles" for fk in fks)

@pytest.mark.asyncio
async def test_audit_fields(database):
    """Test that audit fields are present on all tables."""
    async with database.engine.begin() as conn:
        tables = await conn.run_sync(get_table_names)
        
        for table in tables:
            # Get column info
            result = await conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
            """))
            columns = {row[0] for row in result}
            
            # Check audit columns
            assert "created_at" in columns
            assert "updated_at" in columns
            assert "created_by" in columns
            assert "updated_by" in columns

@pytest.mark.asyncio
async def test_indexes(database):
    """Test that required indexes are present."""
    async with database.engine.begin() as conn:
        # Check price_list_items indexes
        indexes = await conn.run_sync(lambda sync_conn: get_indexes(sync_conn, "price_list_items"))
        index_columns = {tuple(idx["column_names"]) for idx in indexes}
        
        assert ("price_list_id", "item_code") in index_columns
        
        # Check price_lists indexes
        indexes = await conn.run_sync(lambda sync_conn: get_indexes(sync_conn, "price_lists"))
        index_columns = {tuple(idx["column_names"]) for idx in indexes}
        
        assert ("effective_date",) in index_columns
        assert ("company_id", "is_active") in index_columns
