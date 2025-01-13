"""Authentication service module."""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import jwt
import pyotp
import qrcode
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from ..models.auth import User, Role, Permission, RefreshToken, UserCreate, TokenResponse
from ..utils.security import create_access_token, create_refresh_token, verify_refresh_token

class AuthService:
    """Service for handling authentication and authorization."""

    def __init__(self, db: Session, settings: Dict[str, Any]):
        """Initialize auth service."""
        self.db = db
        self.settings = settings
        
        # Initialize Azure Key Vault client
        credential = DefaultAzureCredential()
        self.key_vault = SecretClient(
            vault_url=settings['key_vault_url'],
            credential=credential
        )

    async def authenticate_user(
        self,
        email: str,
        password: str,
        mfa_code: Optional[str] = None
    ) -> TokenResponse:
        """Authenticate user and return tokens."""
        # Find user
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not user.verify_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )

        # Verify MFA if enabled
        if user.is_mfa_enabled:
            if not mfa_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="MFA code required"
                )
            
            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(mfa_code):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code"
                )

        # Generate tokens
        access_token = create_access_token(
            data={"sub": user.email, "roles": [role.name for role in user.roles]},
            secret_key=await self._get_secret("jwt-secret"),
            expires_delta=timedelta(minutes=15)
        )

        refresh_token = create_refresh_token()
        
        # Store refresh token
        db_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        self.db.add(db_token)
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create refresh token"
            )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=900  # 15 minutes
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        # Verify refresh token
        db_token = verify_refresh_token(self.db, refresh_token)
        
        # Generate new access token
        user = db_token.user
        access_token = create_access_token(
            data={"sub": user.email, "roles": [role.name for role in user.roles]},
            secret_key=await self._get_secret("jwt-secret"),
            expires_delta=timedelta(minutes=15)
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=900  # 15 minutes
        )

    async def setup_mfa(self, user_id: int) -> Dict[str, Any]:
        """Setup MFA for user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Generate secret
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        provisioning_uri = totp.provisioning_uri(
            user.email,
            issuer_name="AriesOne"
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Generate backup codes
        backup_codes = [os.urandom(5).hex() for _ in range(10)]
        
        # Store secret and backup codes
        user.mfa_secret = secret
        user.is_mfa_enabled = True
        
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not setup MFA"
            )

        return {
            "secret": secret,
            "qr_code": qr_image,
            "backup_codes": backup_codes
        }

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user."""
        # Create user
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        user.set_password(user_data.password)
        
        # Add roles
        for role_name in user_data.roles:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if role:
                user.roles.append(role)
        
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

    async def _get_secret(self, secret_name: str) -> str:
        """Get secret from Azure Key Vault."""
        try:
            secret = await self.key_vault.get_secret(secret_name)
            return secret.value
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not retrieve secret: {str(e)}"
            )
