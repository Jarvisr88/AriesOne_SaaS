from typing import Dict, Optional, List
import asyncio
from datetime import datetime, timedelta
import uuid
import jwt
import pyotp
import hashlib
from sqlalchemy.orm import Session
from app.core.config import config_manager
from app.core.logging import logger
from app.core.monitoring import metrics
from app.core.events import event_bus
from app.core.security import (
    hash_password,
    verify_password,
    encrypt_data,
    decrypt_data
)
from app.models.auth import (
    User,
    BiometricData,
    TwoFactorAuth,
    SecurityAudit,
    AuthenticationAttempt
)

class AuthMetrics:
    """Authentication metrics tracking"""
    def __init__(self):
        self.login_attempts = metrics.counter(
            "auth_login_attempts_total",
            "Total login attempts"
        )
        self.failed_attempts = metrics.counter(
            "auth_failed_attempts_total",
            "Total failed login attempts"
        )
        self.biometric_attempts = metrics.counter(
            "auth_biometric_attempts_total",
            "Total biometric authentication attempts"
        )
        self.twofa_attempts = metrics.counter(
            "auth_2fa_attempts_total",
            "Total 2FA attempts"
        )
        self.auth_time = metrics.histogram(
            "auth_processing_time_seconds",
            "Authentication processing time"
        )

class AuthenticationService:
    """Authentication service implementation"""
    def __init__(self, db: Session):
        self.db = db
        self.metrics = AuthMetrics()
        self._setup_service()

    def _setup_service(self):
        """Setup authentication service"""
        self.jwt_secret = config_manager.get("JWT_SECRET")
        self.jwt_algorithm = config_manager.get("JWT_ALGORITHM", "HS256")
        self.token_expiry = config_manager.get("TOKEN_EXPIRY", 3600)
        self.max_attempts = config_manager.get("MAX_LOGIN_ATTEMPTS", 3)
        self.lockout_time = config_manager.get("ACCOUNT_LOCKOUT_TIME", 300)
        self.biometric_threshold = config_manager.get("BIOMETRIC_THRESHOLD", 0.85)
        self.twofa_expiry = config_manager.get("2FA_EXPIRY", 300)

    async def register_user(
        self,
        username: str,
        password: str,
        email: str,
        biometric_data: Optional[Dict] = None
    ) -> User:
        """Register new user"""
        try:
            # Hash password
            password_hash = hash_password(password)
            
            # Create user
            user = User(
                username=username,
                password_hash=password_hash,
                email=email,
                status="ACTIVE"
            )
            
            # Store biometric data if provided
            if biometric_data:
                encrypted_data = encrypt_data(biometric_data)
                bio = BiometricData(
                    user=user,
                    data_type=biometric_data["type"],
                    data=encrypted_data
                )
                self.db.add(bio)
            
            # Setup 2FA if enabled
            twofa = TwoFactorAuth(
                user=user,
                secret=pyotp.random_base32(),
                enabled=False
            )
            
            self.db.add(user)
            self.db.add(twofa)
            self.db.commit()
            
            # Emit event
            await event_bus.emit({
                "type": "user_registered",
                "data": {
                    "user_id": str(user.id),
                    "username": username,
                    "email": email
                }
            })
            
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"User registration error: {e}")
            raise

    async def authenticate(
        self,
        username: str,
        password: str,
        biometric_data: Optional[Dict] = None,
        twofa_code: Optional[str] = None
    ) -> Dict:
        """Authenticate user"""
        start_time = datetime.utcnow()
        self.metrics.login_attempts.inc()
        
        try:
            # Get user
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                self.metrics.failed_attempts.inc()
                raise ValueError("Invalid credentials")
                
            # Check account status
            if user.status == "LOCKED":
                if user.locked_until and user.locked_until > datetime.utcnow():
                    raise ValueError("Account is locked")
                user.status = "ACTIVE"
                user.locked_until = None
                
            # Verify password
            if not verify_password(password, user.password_hash):
                await self._handle_failed_attempt(user)
                raise ValueError("Invalid credentials")
                
            # Verify biometric data if provided
            if biometric_data:
                self.metrics.biometric_attempts.inc()
                if not await self._verify_biometric(user, biometric_data):
                    await self._handle_failed_attempt(user)
                    raise ValueError("Biometric verification failed")
                    
            # Verify 2FA if enabled
            if user.twofa.enabled:
                self.metrics.twofa_attempts.inc()
                if not twofa_code:
                    return {
                        "requires_2fa": True,
                        "temp_token": self._create_temp_token(user)
                    }
                if not await self._verify_2fa(user, twofa_code):
                    await self._handle_failed_attempt(user)
                    raise ValueError("Invalid 2FA code")
                    
            # Create session
            token = self._create_token(user)
            
            # Clear failed attempts
            user.failed_attempts = 0
            self.db.commit()
            
            # Track metrics
            auth_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.auth_time.observe(auth_time)
            
            # Emit event
            await event_bus.emit({
                "type": "user_authenticated",
                "data": {
                    "user_id": str(user.id),
                    "username": username,
                    "auth_time": auth_time
                }
            })
            
            return {
                "token": token,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "twofa_enabled": user.twofa.enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise

    async def _handle_failed_attempt(self, user: User):
        """Handle failed authentication attempt"""
        # Increment failed attempts
        user.failed_attempts += 1
        
        # Create audit entry
        audit = SecurityAudit(
            user=user,
            action="FAILED_LOGIN",
            details=f"Failed attempt {user.failed_attempts} of {self.max_attempts}"
        )
        self.db.add(audit)
        
        # Lock account if max attempts exceeded
        if user.failed_attempts >= self.max_attempts:
            user.status = "LOCKED"
            user.locked_until = datetime.utcnow() + timedelta(seconds=self.lockout_time)
            
            # Emit event
            await event_bus.emit({
                "type": "account_locked",
                "data": {
                    "user_id": str(user.id),
                    "username": user.username,
                    "locked_until": user.locked_until.isoformat()
                }
            })
            
        self.db.commit()
        self.metrics.failed_attempts.inc()

    async def _verify_biometric(
        self,
        user: User,
        biometric_data: Dict
    ) -> bool:
        """Verify biometric data"""
        try:
            # Get stored biometric data
            stored = user.biometric_data.filter(
                BiometricData.data_type == biometric_data["type"]
            ).first()
            if not stored:
                return False
                
            # Decrypt stored data
            stored_data = decrypt_data(stored.data)
            
            # Compare biometric data
            similarity = self._compare_biometric(
                stored_data,
                biometric_data["data"]
            )
            return similarity >= self.biometric_threshold
            
        except Exception as e:
            logger.error(f"Biometric verification error: {e}")
            return False

    def _compare_biometric(
        self,
        stored_data: Dict,
        input_data: Dict
    ) -> float:
        """Compare biometric data and return similarity score"""
        # Implement biometric comparison logic
        # This is a placeholder - use appropriate biometric library
        return 0.9

    async def _verify_2fa(
        self,
        user: User,
        code: str
    ) -> bool:
        """Verify 2FA code"""
        try:
            totp = pyotp.TOTP(user.twofa.secret)
            return totp.verify(code)
        except Exception as e:
            logger.error(f"2FA verification error: {e}")
            return False

    def _create_token(self, user: User) -> str:
        """Create authentication token"""
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry)
        }
        return jwt.encode(
            payload,
            self.jwt_secret,
            algorithm=self.jwt_algorithm
        )

    def _create_temp_token(self, user: User) -> str:
        """Create temporary token for 2FA"""
        payload = {
            "sub": str(user.id),
            "temp": True,
            "exp": datetime.utcnow() + timedelta(seconds=self.twofa_expiry)
        }
        return jwt.encode(
            payload,
            self.jwt_secret,
            algorithm=self.jwt_algorithm
        )

    async def setup_2fa(
        self,
        user_id: uuid.UUID
    ) -> Dict:
        """Setup 2FA for user"""
        try:
            user = self.db.query(User).get(user_id)
            if not user:
                raise ValueError("User not found")
                
            # Generate new secret
            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret)
            
            # Update user's 2FA
            user.twofa.secret = secret
            user.twofa.enabled = True
            
            # Create audit entry
            audit = SecurityAudit(
                user=user,
                action="2FA_ENABLED",
                details="Two-factor authentication enabled"
            )
            self.db.add(audit)
            self.db.commit()
            
            # Emit event
            await event_bus.emit({
                "type": "2fa_enabled",
                "data": {
                    "user_id": str(user.id),
                    "username": user.username
                }
            })
            
            return {
                "secret": secret,
                "qr_code": totp.provisioning_uri(
                    user.email,
                    issuer_name="AriesOne"
                )
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"2FA setup error: {e}")
            raise

    async def register_biometric(
        self,
        user_id: uuid.UUID,
        biometric_data: Dict
    ) -> BiometricData:
        """Register biometric data for user"""
        try:
            user = self.db.query(User).get(user_id)
            if not user:
                raise ValueError("User not found")
                
            # Encrypt biometric data
            encrypted_data = encrypt_data(biometric_data["data"])
            
            # Create biometric entry
            bio = BiometricData(
                user=user,
                data_type=biometric_data["type"],
                data=encrypted_data
            )
            
            # Create audit entry
            audit = SecurityAudit(
                user=user,
                action="BIOMETRIC_REGISTERED",
                details=f"Registered {biometric_data['type']} biometric"
            )
            
            self.db.add(bio)
            self.db.add(audit)
            self.db.commit()
            
            # Emit event
            await event_bus.emit({
                "type": "biometric_registered",
                "data": {
                    "user_id": str(user.id),
                    "username": user.username,
                    "biometric_type": biometric_data["type"]
                }
            })
            
            return bio
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Biometric registration error: {e}")
            raise

    async def get_metrics(self) -> Dict:
        """Get authentication metrics"""
        return {
            "login_attempts": self.metrics.login_attempts._value.get(),
            "failed_attempts": self.metrics.failed_attempts._value.get(),
            "biometric_attempts": self.metrics.biometric_attempts._value.get(),
            "twofa_attempts": self.metrics.twofa_attempts._value.get(),
            "auth_time": self.metrics.auth_time._value.get()
        }

# Create authentication service factory
def get_auth_service(db: Session) -> AuthenticationService:
    return AuthenticationService(db)
