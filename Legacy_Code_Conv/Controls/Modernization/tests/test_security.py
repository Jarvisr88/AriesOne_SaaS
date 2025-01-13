import pytest
import jwt
from datetime import datetime, timedelta
from security.auth_service import AuthService, SecurityContext
from security.encryption_service import EncryptionService
from security.audit_service import AuditService
from unittest.mock import patch, MagicMock

@pytest.fixture
def auth_service():
    """Create test instance of AuthService"""
    return AuthService(
        secret_key="test_secret",
        token_expiry=3600,
        refresh_token_expiry=86400
    )

@pytest.fixture
def encryption_service():
    """Create test instance of EncryptionService"""
    return EncryptionService(
        key_vault_url="https://test-vault.azure.net",
        key_name="test-key"
    )

@pytest.fixture
def audit_service():
    """Create test instance of AuditService"""
    return AuditService(
        db_url="postgresql://test:test@localhost/test_db",
        log_level="DEBUG"
    )

class TestAuthService:
    """Test authentication and authorization functionality"""

    def test_password_hashing(self, auth_service):
        """Test password hashing and verification"""
        password = "SecurePassword123!"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("WrongPassword", hashed)

    def test_token_generation(self, auth_service):
        """Test JWT token generation and validation"""
        user_data = {
            "user_id": "U123",
            "role": "admin",
            "permissions": ["read", "write"]
        }

        # Generate tokens
        access_token = auth_service.generate_access_token(user_data)
        refresh_token = auth_service.generate_refresh_token(user_data)

        # Verify tokens
        decoded_access = auth_service.verify_token(access_token)
        assert decoded_access["user_id"] == user_data["user_id"]
        assert decoded_access["role"] == user_data["role"]

        decoded_refresh = auth_service.verify_token(refresh_token)
        assert decoded_refresh["user_id"] == user_data["user_id"]
        assert "refresh" in decoded_refresh["type"]

    def test_token_expiry(self, auth_service):
        """Test token expiration handling"""
        user_data = {"user_id": "U123"}

        # Create expired token
        expired_token = jwt.encode(
            {
                **user_data,
                "exp": datetime.utcnow() - timedelta(hours=1)
            },
            auth_service.secret_key,
            algorithm="HS256"
        )

        # Verify expired token handling
        with pytest.raises(jwt.ExpiredSignatureError):
            auth_service.verify_token(expired_token)

    def test_role_based_access(self, auth_service):
        """Test role-based access control"""
        admin_context = SecurityContext(
            user_id="U123",
            role="admin",
            permissions=["read", "write", "delete"]
        )

        user_context = SecurityContext(
            user_id="U456",
            role="user",
            permissions=["read"]
        )

        # Test admin permissions
        assert auth_service.check_permission(admin_context, "delete")
        assert auth_service.check_permission(admin_context, "write")

        # Test user permissions
        assert auth_service.check_permission(user_context, "read")
        assert not auth_service.check_permission(user_context, "write")

class TestEncryptionService:
    """Test data encryption functionality"""

    def test_data_encryption(self, encryption_service):
        """Test data encryption and decryption"""
        sensitive_data = "sensitive-info-123"
        
        # Encrypt data
        encrypted = encryption_service.encrypt(sensitive_data)
        assert encrypted != sensitive_data

        # Decrypt data
        decrypted = encryption_service.decrypt(encrypted)
        assert decrypted == sensitive_data

    def test_key_rotation(self, encryption_service):
        """Test encryption key rotation"""
        # Mock key vault operations
        with patch("azure.keyvault.keys.KeyClient") as mock_client:
            mock_client.return_value.create_key.return_value = MagicMock(
                id="https://test-vault.azure.net/keys/test-key/new-version"
            )

            # Rotate key
            new_key_version = encryption_service.rotate_key()
            assert "new-version" in new_key_version

            # Verify old data can still be decrypted
            old_encrypted_data = b"old-encrypted-data"
            assert encryption_service.decrypt(
                old_encrypted_data,
                key_version="old-version"
            )

class TestAuditService:
    """Test audit logging functionality"""

    def test_audit_logging(self, audit_service):
        """Test audit log creation and retrieval"""
        # Create audit log
        audit_data = {
            "user_id": "U123",
            "action": "data_access",
            "resource": "patient_records",
            "details": {"record_id": "P789"}
        }

        log_id = audit_service.log_event(**audit_data)
        assert log_id

        # Retrieve audit log
        log_entry = audit_service.get_event(log_id)
        assert log_entry["user_id"] == audit_data["user_id"]
        assert log_entry["action"] == audit_data["action"]

    def test_audit_search(self, audit_service):
        """Test audit log searching and filtering"""
        # Create multiple audit logs
        for i in range(5):
            audit_service.log_event(
                user_id=f"U{i}",
                action="login",
                resource="system",
                details={"ip": f"192.168.1.{i}"}
            )

        # Search logs
        logs = audit_service.search_events(
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow(),
            action="login"
        )

        assert len(logs) == 5
        assert all(log["action"] == "login" for log in logs)

def test_security_integration(auth_service, encryption_service, audit_service):
    """Test integration between security services"""
    # User authentication
    user_data = {
        "user_id": "U123",
        "role": "admin"
    }
    access_token = auth_service.generate_access_token(user_data)

    # Encrypt sensitive data
    sensitive_data = "PHI-data-123"
    encrypted_data = encryption_service.encrypt(sensitive_data)

    # Log access
    audit_service.log_event(
        user_id=user_data["user_id"],
        action="data_access",
        resource="encrypted_data",
        details={
            "data_id": "D123",
            "access_type": "write"
        }
    )

    # Verify flow
    assert auth_service.verify_token(access_token)
    assert encryption_service.decrypt(encrypted_data) == sensitive_data

if __name__ == "__main__":
    pytest.main([__file__])
