"""Authentication schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token data schema."""
    user_id: str

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr

class PasswordUpdateRequest(BaseModel):
    """Password update request schema."""
    current_password: str
    new_password: str
