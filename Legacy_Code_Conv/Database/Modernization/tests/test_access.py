"""Access control tests."""
import pytest
from security.access import DatabaseAccess


@pytest.mark.asyncio
async def test_enable_row_level_security(test_session):
    """Test RLS enablement."""
    access = DatabaseAccess()
    
    # Setup test table
    await test_session.execute("""
        CREATE TABLE test_rls (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            data TEXT
        )
    """)
    await test_session.commit()
    
    # Enable RLS
    result = await access.enable_row_level_security(
        table_name="test_rls",
        policy_name="user_policy",
        policy="user_id = current_user",
        roles=["test_role"]
    )
    
    assert result["status"] == "success"
    assert result["table"] == "test_rls"
    assert result["policy"] == "user_policy"


@pytest.mark.asyncio
async def test_set_schema_permissions(test_session):
    """Test schema permission setup."""
    access = DatabaseAccess()
    
    # Set permissions
    result = await access.set_schema_permissions(
        schema_name="public",
        role="test_role",
        permissions=["SELECT", "INSERT"]
    )
    
    assert result["status"] == "success"
    assert result["schema"] == "public"
    assert result["role"] == "test_role"
    assert result["permissions"] == ["SELECT", "INSERT"]


@pytest.mark.asyncio
async def test_transfer_ownership(test_session):
    """Test object ownership transfer."""
    access = DatabaseAccess()
    
    # Transfer ownership
    result = await access.transfer_ownership(
        object_type="TABLE",
        object_name="test_rls",
        new_owner="test_role"
    )
    
    assert result["status"] == "success"
    assert result["object_type"] == "TABLE"
    assert result["object_name"] == "test_rls"
    assert result["new_owner"] == "test_role"


@pytest.mark.asyncio
async def test_set_connection_limits(test_session):
    """Test connection limit setting."""
    access = DatabaseAccess()
    
    # Set limits
    result = await access.set_connection_limits(
        role="test_role",
        connection_limit=5
    )
    
    assert result["status"] == "success"
    assert result["role"] == "test_role"
    assert result["connection_limit"] == 5


@pytest.mark.asyncio
async def test_audit_permissions(test_session):
    """Test permission auditing."""
    access = DatabaseAccess()
    
    # Audit specific object
    result = await access.audit_permissions(object_name="test_rls")
    
    assert result["status"] == "success"
    assert len(result["permissions"]) > 0
