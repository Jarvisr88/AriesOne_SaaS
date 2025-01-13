"""Authentication API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..models.auth import TokenRequest, TokenResponse, UserCreate, UserResponse, MFASetup
from ..services.auth_service import AuthService
from ..utils.security import verify_access_token, has_permission
from ..database import get_db
from ..config import get_settings

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    mfa_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Login endpoint to obtain access token."""
    auth_service = AuthService(db, get_settings())
    return await auth_service.authenticate_user(
        form_data.username,
        form_data.password,
        mfa_code
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    auth_service = AuthService(db, get_settings())
    return await auth_service.refresh_access_token(refresh_token)

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Register new user."""
    # Verify token and check permissions
    payload = verify_access_token(token, get_settings()["jwt_secret"])
    if not has_permission(payload.get("roles", []), "user_create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    auth_service = AuthService(db, get_settings())
    user = await auth_service.create_user(user_data)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_mfa_enabled=user.is_mfa_enabled,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@router.post("/mfa/setup", response_model=MFASetup)
async def setup_mfa(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Setup MFA for user."""
    # Verify token
    payload = verify_access_token(token, get_settings()["jwt_secret"])
    
    auth_service = AuthService(db, get_settings())
    return await auth_service.setup_mfa(payload["sub"])

@router.post("/mfa/verify")
async def verify_mfa(
    code: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Verify MFA code."""
    # Verify token
    payload = verify_access_token(token, get_settings()["jwt_secret"])
    
    auth_service = AuthService(db, get_settings())
    user = db.query(User).filter(User.email == payload["sub"]).first()
    
    if not user or not user.is_mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled for user"
        )
    
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    return {"message": "MFA code verified successfully"}
