"""
Certificate Manager Module

Handles SSL/TLS certificate operations with automatic renewal.
"""
from datetime import datetime, timedelta
import ssl
from pathlib import Path
from typing import Dict, Optional
import asyncio
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi import HTTPException, status
from azure.keyvault.certificates import CertificateClient
from azure.identity import DefaultAzureCredential

from ..config import get_settings
from ..utils.monitoring import get_logger

logger = get_logger(__name__)
settings = get_settings()

class CertificateManager:
    """Manages SSL/TLS certificates with Azure Key Vault integration."""
    
    def __init__(self):
        """Initialize certificate manager."""
        self.cert_cache: Dict[str, tuple[bytes, datetime]] = {}
        self._lock = asyncio.Lock()
        self.credential = DefaultAzureCredential()
        self.cert_client = CertificateClient(
            vault_url=settings.AZURE_VAULT_URL,
            credential=self.credential
        )

    async def get_certificate(self, cert_name: str) -> ssl.SSLContext:
        """
        Get SSL context with certificate from Azure Key Vault.
        
        Args:
            cert_name: Name of certificate in Key Vault
            
        Returns:
            Configured SSL context
            
        Raises:
            HTTPException: If certificate retrieval fails
        """
        try:
            async with self._lock:
                # Check cache first
                if cert_name in self.cert_cache:
                    cert_data, expiry = self.cert_cache[cert_name]
                    if datetime.utcnow() < expiry - timedelta(days=7):
                        return self._create_ssl_context(cert_data)

                # Fetch from Key Vault
                cert = await asyncio.to_thread(
                    self.cert_client.get_certificate,
                    cert_name
                )
                
                cert_data = await asyncio.to_thread(
                    self.cert_client.get_certificate_version,
                    cert_name,
                    cert.properties.version
                )

                # Cache certificate
                self.cert_cache[cert_name] = (
                    cert_data.cer,
                    cert.properties.expires_on
                )
                
                return self._create_ssl_context(cert_data.cer)

        except Exception as e:
            logger.error(f"Failed to get certificate {cert_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Certificate retrieval failed: {str(e)}"
            )

    def _create_ssl_context(self, cert_data: bytes) -> ssl.SSLContext:
        """Create SSL context from certificate data."""
        context = ssl.create_default_context()
        context.load_verify_locations(cadata=cert_data.decode())
        return context

    async def create_self_signed_cert(
        self,
        common_name: str,
        output_dir: Path,
        days_valid: int = 365
    ):
        """
        Create self-signed certificate for development/testing.
        
        Args:
            common_name: Certificate common name
            output_dir: Directory to save certificate files
            days_valid: Number of days certificate is valid
        """
        # Generate key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name)
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=days_valid)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        ).sign(private_key, hashes.SHA256())

        # Save certificate and private key
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        with open(output_dir / "key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

    async def start_renewal_monitor(
        self,
        check_interval: int = 24 * 60 * 60  # 24 hours
    ):
        """
        Start background task to monitor and renew certificates.
        
        Args:
            check_interval: Interval between checks in seconds
        """
        while True:
            try:
                await self._check_and_renew_certificates()
            except Exception as e:
                logger.error(f"Certificate renewal check failed: {str(e)}")
            await asyncio.sleep(check_interval)

    async def _check_and_renew_certificates(self):
        """Check and renew certificates nearing expiration."""
        async with self._lock:
            for cert_name, (_, expiry) in self.cert_cache.items():
                if datetime.utcnow() > expiry - timedelta(days=30):
                    try:
                        logger.info(f"Renewing certificate {cert_name}")
                        await asyncio.to_thread(
                            self.cert_client.begin_create_certificate,
                            cert_name,
                            settings.CERTIFICATE_POLICY
                        )
                        # Remove from cache to force refresh on next use
                        del self.cert_cache[cert_name]
                    except Exception as e:
                        logger.error(
                            f"Failed to renew certificate {cert_name}: {str(e)}"
                        )

certificate_manager = CertificateManager()
