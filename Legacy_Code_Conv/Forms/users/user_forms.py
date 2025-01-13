"""
User management forms using FastAPI and Pydantic.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, Field
from fastapi import Form, HTTPException, Depends
import re
from datetime import datetime
from passlib.context import CryptContext
from ...repositories.models import User, Role
from ...repositories.user_repository import UserRepository
from ..auth.login_form import pwd_context

class UserCreateForm(BaseModel):
    """User creation form with validation."""
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    company_id: int
    roles: List[int] = []
    is_active: bool = True

    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username format."""
        if not re.match("^[a-zA-Z0-9_-]+$", v):
            raise ValueError('Username must be alphanumeric')
        return v

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search("[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search("[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search("[0-9]", v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validate password confirmation."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        company_id: int = Form(...),
        roles: List[int] = Form([]),
        is_active: bool = Form(True)
    ):
        """Convert form data to model."""
        return cls(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            company_id=company_id,
            roles=roles,
            is_active=is_active
        )

class UserUpdateForm(BaseModel):
    """User update form."""
    email: Optional[EmailStr]
    is_active: Optional[bool]
    roles: Optional[List[int]]

    @classmethod
    def as_form(
        cls,
        email: Optional[str] = Form(None),
        is_active: Optional[bool] = Form(None),
        roles: Optional[List[int]] = Form(None)
    ):
        """Convert form data to model."""
        return cls(
            email=email,
            is_active=is_active,
            roles=roles
        )

class PasswordResetForm(BaseModel):
    """Password reset form."""
    current_password: str
    new_password: str
    confirm_password: str

    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search("[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search("[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search("[0-9]", v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validate password confirmation."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @classmethod
    def as_form(
        cls,
        current_password: str = Form(...),
        new_password: str = Form(...),
        confirm_password: str = Form(...)
    ):
        """Convert form data to model."""
        return cls(
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password
        )

class RoleAssignmentForm(BaseModel):
    """Role assignment form."""
    user_id: int
    role_ids: List[int]
    
    @classmethod
    def as_form(
        cls,
        user_id: int = Form(...),
        role_ids: List[int] = Form(...)
    ):
        """Convert form data to model."""
        return cls(
            user_id=user_id,
            role_ids=role_ids
        )

class UserManager:
    """Handle user management operations."""
    
    def __init__(self, database):
        self.database = database
        self.user_repository = UserRepository(database)

    async def create_user(self, form_data: UserCreateForm, created_by: str):
        """Create new user."""
        # Check if username exists
        existing_user = await self.user_repository.get_by_username(form_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        # Create user
        user = await self.user_repository.create(
            username=form_data.username,
            email=form_data.email,
            password_hash=pwd_context.hash(form_data.password),
            company_id=form_data.company_id,
            is_active=form_data.is_active,
            created_by=created_by,
            updated_by=created_by
        )

        # Assign roles
        if form_data.roles:
            for role_id in form_data.roles:
                await self.user_repository.add_role(
                    user.id,
                    role_id,
                    created_by
                )

        return user

    async def update_user(
        self,
        user_id: int,
        form_data: UserUpdateForm,
        updated_by: str
    ):
        """Update user details."""
        update_data = form_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        return await self.user_repository.update(
            user_id,
            update_data,
            updated_by
        )

    async def reset_password(
        self,
        user_id: int,
        form_data: PasswordResetForm,
        updated_by: str
    ):
        """Reset user password."""
        user = await self.user_repository.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify current password
        if not pwd_context.verify(form_data.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Incorrect password")

        # Update password
        return await self.user_repository.update(
            user_id,
            {"password_hash": pwd_context.hash(form_data.new_password)},
            updated_by
        )

    async def assign_roles(
        self,
        form_data: RoleAssignmentForm,
        updated_by: str
    ):
        """Assign roles to user."""
        user = await self.user_repository.get(form_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Remove existing roles
        await self.user_repository.remove_all_roles(user.id)

        # Assign new roles
        for role_id in form_data.role_ids:
            await self.user_repository.add_role(
                user.id,
                role_id,
                updated_by
            )

        return await self.user_repository.get_user_roles(user.id)
