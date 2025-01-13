"""
User management routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from .user_forms import (
    UserCreateForm,
    UserUpdateForm,
    PasswordResetForm,
    RoleAssignmentForm,
    UserManager
)
from ..auth.login_form import LoginManager
from ...core.database import get_database

router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="templates")

@router.get("/create", response_class=HTMLResponse)
async def create_user_page(request: Request):
    """Render user creation page."""
    return templates.TemplateResponse(
        "user_create.html",
        {"request": request}
    )

@router.get("/edit/{user_id}", response_class=HTMLResponse)
async def edit_user_page(request: Request, user_id: int):
    """Render user edit page."""
    return templates.TemplateResponse(
        "user_edit.html",
        {"request": request, "user_id": user_id}
    )

@router.post("/")
async def create_user(
    form_data: UserCreateForm = Depends(UserCreateForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Create new user."""
    user_manager = UserManager(db)
    return await user_manager.create_user(form_data, current_user.username)

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    form_data: UserUpdateForm = Depends(UserUpdateForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Update user details."""
    user_manager = UserManager(db)
    return await user_manager.update_user(
        user_id,
        form_data,
        current_user.username
    )

@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    form_data: PasswordResetForm = Depends(PasswordResetForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Reset user password."""
    user_manager = UserManager(db)
    return await user_manager.reset_password(
        user_id,
        form_data,
        current_user.username
    )

@router.post("/{user_id}/roles")
async def assign_roles(
    user_id: int,
    form_data: RoleAssignmentForm = Depends(RoleAssignmentForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Assign roles to user."""
    user_manager = UserManager(db)
    return await user_manager.assign_roles(
        form_data,
        current_user.username
    )
