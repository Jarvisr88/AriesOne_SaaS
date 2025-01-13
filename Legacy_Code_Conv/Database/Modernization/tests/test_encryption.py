"""Encryption tests."""
import pytest
from security.encryption import DatabaseEncryption, EncryptedType


@pytest.mark.asyncio
async def test_setup_column_encryption(test_session, test_encryption_key):
    """Test column encryption setup."""
    encryption = DatabaseEncryption(test_encryption_key)
    
    # Setup test table
    await test_session.execute("""
        CREATE TABLE test_table (
            id SERIAL PRIMARY KEY,
            sensitive_data TEXT
        )
    """)
    await test_session.commit()
    
    # Setup encryption
    result = await encryption.setup_column_encryption(
        table_name="test_table",
        column_name="sensitive_data"
    )
    
    assert result["status"] == "success"
    assert result["table"] == "test_table"
    assert result["column"] == "sensitive_data"


@pytest.mark.asyncio
async def test_rotate_encryption_key(test_session, test_encryption_key):
    """Test encryption key rotation."""
    encryption = DatabaseEncryption(test_encryption_key)
    
    # Rotate key
    result = await encryption.rotate_encryption_key(
        table_name="test_table",
        column_name="sensitive_data"
    )
    
    assert result["status"] == "success"
    assert result["table"] == "test_table"
    assert result["column"] == "sensitive_data"


@pytest.mark.asyncio
async def test_audit_encryption(test_session, test_encryption_key):
    """Test encryption audit."""
    encryption = DatabaseEncryption(test_encryption_key)
    
    # Audit specific table
    result = await encryption.audit_encryption(table_name="test_table")
    
    assert result["status"] == "success"
    assert len(result["columns"]) > 0


def test_encrypted_type(test_encryption_key):
    """Test SQLAlchemy encrypted type."""
    encrypted_type = EncryptedType(test_encryption_key)
    
    # Test encryption
    test_value = "sensitive data"
    encrypted = encrypted_type.process_bind_param(test_value, None)
    decrypted = encrypted_type.process_result_value(encrypted, None)
    
    assert decrypted == test_value
