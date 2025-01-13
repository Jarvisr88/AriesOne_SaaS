"""
Base classes for data management services.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataService(ABC):
    """Base class for all data services."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate service configuration."""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        pass

class EncryptionService(DataService):
    """Base class for encryption services."""
    
    @abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data."""
        pass
    
    @abstractmethod
    def decrypt(self, data: bytes) -> bytes:
        """Decrypt data."""
        pass
    
    @abstractmethod
    def rotate_keys(self) -> None:
        """Rotate encryption keys."""
        pass

class StorageService(DataService):
    """Base class for storage services."""
    
    @abstractmethod
    def store(self, key: str, data: bytes) -> bool:
        """Store data."""
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve data."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data."""
        pass

class ComplianceService(DataService):
    """Base class for compliance services."""
    
    @abstractmethod
    def audit_log(self, action: str, details: Dict[str, Any]) -> None:
        """Log compliance-related actions."""
        pass
    
    @abstractmethod
    def validate_compliance(self) -> Dict[str, bool]:
        """Validate compliance requirements."""
        pass
    
    @abstractmethod
    def generate_report(self) -> Dict[str, Any]:
        """Generate compliance report."""
        pass
