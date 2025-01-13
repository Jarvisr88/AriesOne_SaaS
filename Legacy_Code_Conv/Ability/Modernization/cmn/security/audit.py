"""
Security Audit Module

Performs security checks and audits on network components.
"""
import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import aiohttp
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import HTTPException, status
import jwt

from ..config import get_settings
from ..monitoring.telemetry_service import TelemetryService

settings = get_settings()
telemetry = TelemetryService()

class SecurityVulnerability:
    """Represents a security vulnerability."""
    
    def __init__(
        self,
        severity: str,
        description: str,
        component: str,
        recommendation: str
    ):
        """Initialize vulnerability."""
        self.severity = severity
        self.description = description
        self.component = component
        self.recommendation = recommendation
        self.timestamp = datetime.utcnow()

class SecurityAudit:
    """Performs security audits on network components."""

    def __init__(self):
        """Initialize security audit."""
        self.vulnerabilities: List[SecurityVulnerability] = []

    async def audit_ssl_configuration(
        self,
        hostname: str,
        port: int = 443
    ) -> List[SecurityVulnerability]:
        """
        Audit SSL/TLS configuration.
        
        Args:
            hostname: Target hostname
            port: Target port
            
        Returns:
            List of identified vulnerabilities
        """
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(
                    sock,
                    server_hostname=hostname
                ) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    # Check certificate
                    if not cert:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                "HIGH",
                                "No SSL certificate found",
                                "SSL/TLS",
                                "Install valid SSL certificate"
                            )
                        )
                    
                    # Check protocol version
                    if ssock.version() < "TLSv1_2":
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                "HIGH",
                                "Outdated TLS version",
                                "SSL/TLS",
                                "Enable TLS 1.2 or higher"
                            )
                        )
                    
                    # Check cipher strength
                    if cipher[2] < 128:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                "MEDIUM",
                                "Weak cipher strength",
                                "SSL/TLS",
                                "Use stronger ciphers (128-bit or higher)"
                            )
                        )
            
        except Exception as e:
            self.vulnerabilities.append(
                SecurityVulnerability(
                    "HIGH",
                    f"SSL configuration error: {str(e)}",
                    "SSL/TLS",
                    "Fix SSL configuration issues"
                )
            )
        
        return self.vulnerabilities

    async def audit_certificate(
        self,
        cert_data: bytes
    ) -> List[SecurityVulnerability]:
        """
        Audit certificate properties.
        
        Args:
            cert_data: Certificate data
            
        Returns:
            List of identified vulnerabilities
        """
        try:
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # Check expiration
            if cert.not_valid_after < datetime.utcnow():
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        "HIGH",
                        "Certificate expired",
                        "Certificate",
                        "Renew certificate immediately"
                    )
                )
            
            # Check if nearing expiration
            if cert.not_valid_after < datetime.utcnow() + timedelta(days=30):
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        "MEDIUM",
                        "Certificate nearing expiration",
                        "Certificate",
                        "Plan certificate renewal"
                    )
                )
            
            # Check key size
            public_key = cert.public_key()
            key_size = public_key.key_size
            if key_size < 2048:
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        "HIGH",
                        "Weak key size",
                        "Certificate",
                        "Use key size of at least 2048 bits"
                    )
                )
            
            # Check signature algorithm
            sig_alg = cert.signature_algorithm_oid
            if sig_alg.dotted_string in ["1.2.840.113549.1.1.4"]:  # MD5
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        "HIGH",
                        "Weak signature algorithm",
                        "Certificate",
                        "Use SHA-256 or stronger"
                    )
                )
                
        except Exception as e:
            self.vulnerabilities.append(
                SecurityVulnerability(
                    "HIGH",
                    f"Certificate analysis error: {str(e)}",
                    "Certificate",
                    "Fix certificate configuration"
                )
            )
        
        return self.vulnerabilities

    async def audit_network_security(
        self,
        endpoint: str
    ) -> List[SecurityVulnerability]:
        """
        Audit network security configuration.
        
        Args:
            endpoint: Target endpoint
            
        Returns:
            List of identified vulnerabilities
        """
        async with aiohttp.ClientSession() as session:
            try:
                # Check HTTPS
                if not endpoint.startswith("https://"):
                    self.vulnerabilities.append(
                        SecurityVulnerability(
                            "HIGH",
                            "Non-HTTPS endpoint",
                            "Network",
                            "Enable HTTPS"
                        )
                    )
                
                # Check security headers
                async with session.get(endpoint) as response:
                    headers = response.headers
                    
                    # Check HSTS
                    if "Strict-Transport-Security" not in headers:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                "MEDIUM",
                                "HSTS not enabled",
                                "Network",
                                "Enable HSTS"
                            )
                        )
                    
                    # Check XSS protection
                    if "X-XSS-Protection" not in headers:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                "LOW",
                                "XSS protection not configured",
                                "Network",
                                "Enable X-XSS-Protection header"
                            )
                        )
                    
                    # Check content security policy
                    if "Content-Security-Policy" not in headers:
                        self.vulnerabilities.append(
                            SecurityVulnerability(
                                "MEDIUM",
                                "CSP not configured",
                                "Network",
                                "Configure Content Security Policy"
                            )
                        )
                    
            except Exception as e:
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        "HIGH",
                        f"Network security check error: {str(e)}",
                        "Network",
                        "Fix network security configuration"
                    )
                )
        
        return self.vulnerabilities

    async def generate_audit_report(self) -> Dict:
        """Generate comprehensive security audit report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "high_severity": len([
                    v for v in self.vulnerabilities
                    if v.severity == "HIGH"
                ]),
                "medium_severity": len([
                    v for v in self.vulnerabilities
                    if v.severity == "MEDIUM"
                ]),
                "low_severity": len([
                    v for v in self.vulnerabilities
                    if v.severity == "LOW"
                ])
            },
            "vulnerabilities": [
                {
                    "severity": v.severity,
                    "description": v.description,
                    "component": v.component,
                    "recommendation": v.recommendation,
                    "timestamp": v.timestamp.isoformat()
                }
                for v in self.vulnerabilities
            ]
        }
        
        # Log report to monitoring system
        await telemetry.log_event(
            "security_audit_completed",
            "Security audit report generated",
            {"vulnerabilities": report["summary"]}
        )
        
        return report

security_audit = SecurityAudit()
