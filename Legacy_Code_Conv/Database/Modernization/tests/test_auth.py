"""Authentication tests."""
import pytest
from security.auth import DatabaseAuth


@pytest.mark.asyncio
async def test_create_role(test_session):
    """Test role creation."""
    auth = DatabaseAuth()
    
    # Create test role
    result = await auth.create_role(
        role_name="test_role",
        permissions=["SELECT", "INSERT"],
        description="Test role"
    )
    
    assert result["status"] == "success"
    assert result["role"] == "test_role"


@pytest.mark.asyncio
async def test_create_user(test_session):
    """Test user creation."""
    auth = DatabaseAuth()
    
    # Create test user
    result = await auth.create_user(
        username="test_user",
        password="Test123!@#",
        roles=["test_role"],
        connection_limit=5
    )
    
    assert result["status"] == "success"
    assert result["username"] == "test_user"
    assert result["roles"] == ["test_role"]


@pytest.mark.asyncio
async def test_update_user_password(test_session):
    """Test password update."""
    auth = DatabaseAuth()
    
    # Update password
    result = await auth.update_user_password(
        username="test_user",
        new_password="NewTest123!@#"
    )
    
    assert result["status"] == "success"
    assert result["username"] == "test_user"


@pytest.mark.asyncio
async def test_revoke_user_access(test_session):
    """Test access revocation."""
    auth = DatabaseAuth()
    
    # Revoke specific role
    result = await auth.revoke_user_access(
        username="test_user",
        roles=["test_role"]
    )
    
    assert result["status"] == "success"
    assert result["username"] == "test_user"
    assert result["roles_revoked"] == ["test_role"]


@pytest.mark.asyncio
async def test_audit_user_access(test_session):
    """Test access auditing."""
    auth = DatabaseAuth()
    
    # Audit specific user
    result = await auth.audit_user_access(username="test_user")
    
    assert result["status"] == "success"
    assert len(result["users"]) > 0
