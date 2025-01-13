from typing import Dict, List, Optional
from datetime import datetime
import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.mobile import (
    BiometricDevice,
    BiometricSession,
    BiometricLog
)

class BiometricService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.supported_types = ["fingerprint", "face", "iris"]
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.session_duration = 3600  # 1 hour

    async def register_device(
        self,
        user_id: str,
        device_data: Dict
    ) -> Dict:
        """Register device for biometric auth"""
        try:
            # Validate device data
            self._validate_device_data(device_data)
            
            # Check existing device
            existing_device = await BiometricDevice.get(
                device_id=device_data["device_id"],
                user_id=user_id
            )
            
            if existing_device:
                # Update device
                for key, value in device_data.items():
                    setattr(existing_device, key, value)
                existing_device.updated_at = datetime.now()
                await existing_device.save()
                
                return {
                    "status": "updated",
                    "device_id": str(existing_device.id)
                }
            
            # Create new device
            device = await BiometricDevice.create(
                user_id=user_id,
                device_id=device_data["device_id"],
                device_name=device_data["device_name"],
                biometric_type=device_data["biometric_type"],
                public_key=device_data["public_key"],
                is_active=True,
                created_at=datetime.now()
            )
            
            return {
                "status": "registered",
                "device_id": str(device.id)
            }
        except Exception as e:
            logger.error(f"Device registration failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def authenticate(
        self,
        device_id: str,
        signature: str,
        challenge: str
    ) -> Dict:
        """Authenticate using biometrics"""
        try:
            # Get device
            device = await BiometricDevice.get(
                device_id=device_id,
                is_active=True
            )
            if not device:
                raise ValueError("Device not found or inactive")
            
            # Verify signature
            is_valid = await self._verify_signature(
                device.public_key,
                signature,
                challenge
            )
            
            if not is_valid:
                # Log failed attempt
                await BiometricLog.create(
                    device_id=device_id,
                    user_id=device.user_id,
                    status="failed",
                    error="Invalid signature",
                    created_at=datetime.now()
                )
                raise ValueError("Invalid biometric signature")
            
            # Create session
            session = await self._create_session(device)
            
            # Log successful attempt
            await BiometricLog.create(
                device_id=device_id,
                user_id=device.user_id,
                status="success",
                session_id=session.id,
                created_at=datetime.now()
            )
            
            return {
                "status": "success",
                "session_token": session.token,
                "expires_at": session.expires_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Biometric authentication failed: {str(e)}")
            raise HTTPException(status_code=401, detail=str(e))

    async def verify_session(
        self,
        token: str
    ) -> Dict:
        """Verify biometric session"""
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"]
            )
            
            # Get session
            session = await BiometricSession.get(
                id=payload["session_id"],
                is_active=True
            )
            
            if not session:
                raise ValueError("Session not found or inactive")
            
            # Check expiration
            if session.expires_at < datetime.now():
                session.is_active = False
                await session.save()
                raise ValueError("Session expired")
            
            return {
                "status": "valid",
                "user_id": session.user_id,
                "device_id": session.device_id,
                "expires_at": session.expires_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Session verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail=str(e))

    async def revoke_device(
        self,
        device_id: str,
        user_id: str
    ) -> Dict:
        """Revoke biometric device"""
        try:
            # Get device
            device = await BiometricDevice.get(
                device_id=device_id,
                user_id=user_id
            )
            if not device:
                raise ValueError("Device not found")
            
            # Deactivate device
            device.is_active = False
            device.revoked_at = datetime.now()
            await device.save()
            
            # Revoke active sessions
            await BiometricSession.filter(
                device_id=device_id,
                is_active=True
            ).update(is_active=False)
            
            return {
                "status": "revoked",
                "device_id": device_id
            }
        except Exception as e:
            logger.error(f"Device revocation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _create_session(
        self,
        device: BiometricDevice
    ) -> BiometricSession:
        """Create biometric session"""
        try:
            # Create session record
            session = await BiometricSession.create(
                user_id=device.user_id,
                device_id=device.device_id,
                is_active=True,
                created_at=datetime.now(),
                expires_at=datetime.now().timestamp() + self.session_duration
            )
            
            # Generate JWT token
            token = jwt.encode(
                {
                    "session_id": str(session.id),
                    "user_id": device.user_id,
                    "device_id": device.device_id,
                    "exp": session.expires_at.timestamp()
                },
                self.jwt_secret,
                algorithm="HS256"
            )
            
            session.token = token
            await session.save()
            
            return session
        except Exception as e:
            logger.error(f"Session creation failed: {str(e)}")
            raise

    async def _verify_signature(
        self,
        public_key: str,
        signature: str,
        challenge: str
    ) -> bool:
        """Verify biometric signature"""
        try:
            # Implement signature verification logic
            # This would typically use platform-specific crypto libraries
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False

    def _validate_device_data(self, device_data: Dict) -> None:
        """Validate device registration data"""
        required_fields = [
            "device_id",
            "device_name",
            "biometric_type",
            "public_key"
        ]
        for field in required_fields:
            if field not in device_data:
                raise ValueError(f"Missing required field: {field}")
        
        if device_data["biometric_type"] not in self.supported_types:
            raise ValueError(
                f"Unsupported biometric type: {device_data['biometric_type']}"
            )
