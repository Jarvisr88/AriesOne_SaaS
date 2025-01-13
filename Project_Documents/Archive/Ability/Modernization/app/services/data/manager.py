"""
Data management orchestration service.
"""
from typing import Dict, Any, Optional, Type
from app.services.data.base import (
    DataService,
    EncryptionService,
    StorageService,
    ComplianceService
)
from app.services.data.encryption import FernetEncryptionService
from app.services.data.storage import S3StorageService
from app.services.data.compliance import GDPRComplianceService
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """
    Data management orchestrator that coordinates various data services.
    
    This class follows the Facade pattern to provide a simplified interface
    to the complex subsystem of data services. It also implements the
    Strategy pattern to allow runtime configuration of service implementations.
    """
    
    def __init__(
        self,
        encryption_service: Optional[Type[EncryptionService]] = None,
        storage_service: Optional[Type[StorageService]] = None,
        compliance_service: Optional[Type[ComplianceService]] = None
    ):
        # Initialize with default or provided service implementations
        self._encryption = (encryption_service or FernetEncryptionService)()
        self._storage = (storage_service or S3StorageService)()
        self._compliance = (compliance_service or GDPRComplianceService)()
        
        # Track service status
        self._services_status: Dict[str, bool] = {
            "encryption": False,
            "storage": False,
            "compliance": False
        }
    
    async def initialize(self) -> None:
        """Initialize all data services."""
        try:
            # Initialize encryption service
            self._encryption.initialize()
            self._services_status["encryption"] = True
            logger.info("Encryption service initialized")
            
            # Initialize storage service
            self._storage.initialize()
            self._services_status["storage"] = True
            logger.info("Storage service initialized")
            
            # Initialize compliance service
            self._compliance.initialize()
            self._services_status["compliance"] = True
            logger.info("Compliance service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize data services: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all data services."""
        return {
            "encryption": self._encryption.health_check(),
            "storage": self._storage.health_check(),
            "compliance": self._compliance.health_check(),
            "services_status": self._services_status
        }
    
    async def store_data(
        self,
        key: str,
        data: bytes,
        encrypt: bool = True
    ) -> bool:
        """Store data with optional encryption."""
        try:
            # Log the operation
            self._compliance.audit_log(
                "store_data",
                {"key": key, "encrypted": encrypt}
            )
            
            # Encrypt if requested
            if encrypt:
                data = self._encryption.encrypt(data)
            
            # Store the data
            success = self._storage.store(key, data)
            
            if success:
                logger.info(f"Successfully stored data for key: {key}")
            else:
                logger.error(f"Failed to store data for key: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error storing data: {str(e)}")
            raise
    
    async def retrieve_data(
        self,
        key: str,
        decrypt: bool = True
    ) -> Optional[bytes]:
        """Retrieve data with optional decryption."""
        try:
            # Log the operation
            self._compliance.audit_log(
                "retrieve_data",
                {"key": key, "decrypted": decrypt}
            )
            
            # Retrieve the data
            data = self._storage.retrieve(key)
            
            if data is None:
                logger.warning(f"No data found for key: {key}")
                return None
            
            # Decrypt if requested
            if decrypt:
                data = self._encryption.decrypt(data)
            
            logger.info(f"Successfully retrieved data for key: {key}")
            return data
            
        except Exception as e:
            logger.error(f"Error retrieving data: {str(e)}")
            raise
    
    async def delete_data(self, key: str) -> bool:
        """Delete data and log the operation."""
        try:
            # Log the operation
            self._compliance.audit_log(
                "delete_data",
                {"key": key}
            )
            
            # Delete the data
            success = self._storage.delete(key)
            
            if success:
                logger.info(f"Successfully deleted data for key: {key}")
            else:
                logger.error(f"Failed to delete data for key: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting data: {str(e)}")
            raise
    
    async def rotate_encryption_keys(self) -> None:
        """Rotate encryption keys and re-encrypt data."""
        try:
            # Log the operation
            self._compliance.audit_log(
                "rotate_keys",
                {"timestamp": "now()"}
            )
            
            # Perform key rotation
            self._encryption.rotate_keys()
            logger.info("Successfully rotated encryption keys")
            
        except Exception as e:
            logger.error(f"Error rotating encryption keys: {str(e)}")
            raise
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive compliance report."""
        try:
            report = self._compliance.generate_report()
            logger.info("Successfully generated compliance report")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            raise
