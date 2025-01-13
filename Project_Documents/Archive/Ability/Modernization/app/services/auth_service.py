from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from jose import jwt, JWTError
import bcrypt
import pyotp
import secrets
import json

from app.core.config import settings
from app.models.core import (
    User,
    UserStatus,
    AuthProvider,
    UserSession,
    MFAMethod,
    MFAType,
    CoreAuditLog,
    AuditLogType
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash
)

class AuthenticationError(Exception):
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def authenticate_user(
        self,
        email: str,
        password: str,
        request: Request
    ) -> Tuple[User, UserSession]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(
            User.email == email,
            User.auth_provider == AuthProvider.LOCAL
        ).first()

        if not user or not verify_password(password, user.hashed_password):
            await self._log_auth_event(
                None,
                "login_attempt",
                "failure",
                request,
                error_message="Invalid credentials"
            )
            raise AuthenticationError(
                "Invalid email or password",
                "INVALID_CREDENTIALS"
            )

        if user.status != UserStatus.ACTIVE:
            await self._log_auth_event(
                user.id,
                "login_attempt",
                "failure",
                request,
                error_message=f"User status: {user.status}"
            )
            raise AuthenticationError(
                f"Account is {user.status}",
                "ACCOUNT_INACTIVE"
            )

        # Create session
        session = await self._create_session(user, request)
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()

        await self._log_auth_event(
            user.id,
            "login",
            "success",
            request
        )

        return user, session

    async def authenticate_sso(
        self,
        auth_provider: AuthProvider,
        token_info: Dict[str, Any],
        request: Request
    ) -> Tuple[User, UserSession]:
        """Authenticate user with SSO provider"""
        provider_id = token_info.get("sub")
        email = token_info.get("email")

        if not provider_id or not email:
            raise AuthenticationError(
                "Invalid SSO token",
                "INVALID_TOKEN"
            )

        user = self.db.query(User).filter(
            User.auth_provider == auth_provider,
            User.auth_provider_id == provider_id
        ).first()

        if not user:
            # Auto-create user if enabled for the provider
            if auth_provider in settings.AUTO_CREATE_SSO_USERS:
                user = await self._create_sso_user(auth_provider, token_info)
            else:
                raise AuthenticationError(
                    "User not found",
                    "USER_NOT_FOUND"
                )

        if user.status != UserStatus.ACTIVE:
            await self._log_auth_event(
                user.id,
                "sso_login_attempt",
                "failure",
                request,
                error_message=f"User status: {user.status}"
            )
            raise AuthenticationError(
                f"Account is {user.status}",
                "ACCOUNT_INACTIVE"
            )

        # Create session
        session = await self._create_session(user, request)
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()

        await self._log_auth_event(
            user.id,
            "sso_login",
            "success",
            request
        )

        return user, session

    async def verify_mfa(
        self,
        user_id: int,
        session_id: int,
        mfa_type: MFAType,
        code: str,
        request: Request
    ) -> bool:
        """Verify MFA code"""
        session = self.db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == user_id
        ).first()

        if not session:
            raise AuthenticationError(
                "Invalid session",
                "INVALID_SESSION"
            )

        mfa_method = self.db.query(MFAMethod).filter(
            MFAMethod.user_id == user_id,
            MFAMethod.type == mfa_type,
            MFAMethod.is_enabled == True
        ).first()

        if not mfa_method:
            raise AuthenticationError(
                "MFA method not found",
                "MFA_NOT_FOUND"
            )

        is_valid = False
        if mfa_type == MFAType.TOTP:
            totp = pyotp.TOTP(mfa_method.secret)
            is_valid = totp.verify(code)
        elif mfa_type == MFAType.SMS or mfa_type == MFAType.EMAIL:
            # Verify code from cache/storage
            pass
        elif mfa_type == MFAType.HARDWARE_KEY:
            # Verify hardware key signature
            pass

        if is_valid:
            session.is_mfa_completed = True
            mfa_method.last_used = datetime.now(timezone.utc)
            self.db.commit()

            await self._log_auth_event(
                user_id,
                "mfa_verification",
                "success",
                request
            )
        else:
            await self._log_auth_event(
                user_id,
                "mfa_verification",
                "failure",
                request,
                error_message="Invalid MFA code"
            )

        return is_valid

    async def refresh_session(
        self,
        refresh_token: str,
        request: Request
    ) -> Tuple[UserSession, str, str]:
        """Refresh user session"""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            session_id = payload.get("session_id")
        except JWTError:
            raise AuthenticationError(
                "Invalid refresh token",
                "INVALID_TOKEN"
            )

        session = self.db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.refresh_token == refresh_token
        ).first()

        if not session or session.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError(
                "Invalid or expired session",
                "INVALID_SESSION"
            )

        # Create new tokens
        new_access_token = create_access_token(
            data={"sub": str(session.user_id), "session_id": session_id}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(session.user_id), "session_id": session_id}
        )

        # Update session
        session.refresh_token = new_refresh_token
        session.last_activity = datetime.now(timezone.utc)
        self.db.commit()

        await self._log_auth_event(
            session.user_id,
            "session_refresh",
            "success",
            request
        )

        return session, new_access_token, new_refresh_token

    async def logout(
        self,
        session_id: int,
        request: Request
    ) -> None:
        """Log out user session"""
        session = self.db.query(UserSession).filter(
            UserSession.id == session_id
        ).first()

        if session:
            await self._log_auth_event(
                session.user_id,
                "logout",
                "success",
                request
            )
            self.db.delete(session)
            self.db.commit()

    async def setup_mfa(
        self,
        user_id: int,
        mfa_type: MFAType,
        identifier: str,
        request: Request
    ) -> Dict[str, Any]:
        """Set up new MFA method"""
        # Check if MFA method already exists
        existing = self.db.query(MFAMethod).filter(
            MFAMethod.user_id == user_id,
            MFAMethod.type == mfa_type,
            MFAMethod.identifier == identifier
        ).first()

        if existing:
            raise AuthenticationError(
                "MFA method already exists",
                "MFA_EXISTS"
            )

        result = {}
        if mfa_type == MFAType.TOTP:
            # Generate TOTP secret
            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret)
            result = {
                "secret": secret,
                "uri": totp.provisioning_uri(identifier, issuer_name=settings.APP_NAME)
            }
        elif mfa_type in [MFAType.SMS, MFAType.EMAIL]:
            # Send verification code
            result = {"code_sent": True}
        elif mfa_type == MFAType.HARDWARE_KEY:
            # Generate registration options
            pass

        # Create MFA method
        mfa_method = MFAMethod(
            user_id=user_id,
            type=mfa_type,
            identifier=identifier,
            secret=result.get("secret"),
            is_primary=not self._has_mfa_methods(user_id)
        )
        self.db.add(mfa_method)
        self.db.commit()

        await self._log_auth_event(
            user_id,
            "mfa_setup",
            "success",
            request,
            metadata={"type": mfa_type}
        )

        return result

    async def _create_session(
        self,
        user: User,
        request: Request
    ) -> UserSession:
        """Create new user session"""
        # Clean up expired sessions
        self.db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.expires_at < datetime.now(timezone.utc)
        ).delete()

        # Check max concurrent sessions
        active_sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user.id
        ).count()

        if active_sessions >= settings.MAX_CONCURRENT_SESSIONS:
            # Delete oldest session
            oldest_session = self.db.query(UserSession).filter(
                UserSession.user_id == user.id
            ).order_by(UserSession.created_at).first()
            self.db.delete(oldest_session)

        # Create new session
        session_token = secrets.token_urlsafe(32)
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )

        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.SESSION_DURATION_DAYS),
            last_activity=datetime.now(timezone.utc),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            device_info=self._get_device_info(request)
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    async def _create_sso_user(
        self,
        auth_provider: AuthProvider,
        token_info: Dict[str, Any]
    ) -> User:
        """Create new user from SSO data"""
        user = User(
            email=token_info["email"],
            full_name=token_info.get("name", ""),
            auth_provider=auth_provider,
            auth_provider_id=token_info["sub"],
            status=UserStatus.ACTIVE
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _has_mfa_methods(self, user_id: int) -> bool:
        """Check if user has any MFA methods"""
        return self.db.query(MFAMethod).filter(
            MFAMethod.user_id == user_id,
            MFAMethod.is_enabled == True
        ).count() > 0

    def _get_device_info(self, request: Request) -> Dict[str, Any]:
        """Extract device information from request"""
        return {
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "headers": dict(request.headers)
        }

    async def _log_auth_event(
        self,
        user_id: Optional[int],
        action: str,
        status: str,
        request: Request,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log authentication event"""
        log = CoreAuditLog(
            user_id=user_id,
            log_type=AuditLogType.AUTH,
            action=action,
            status=status,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            request_id=request.state.request_id,
            metadata=metadata,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()
