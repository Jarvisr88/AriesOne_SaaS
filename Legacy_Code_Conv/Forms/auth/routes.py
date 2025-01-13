"""
Authentication routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from .login_form import LoginForm, LoginManager, Token
from ...core.database import get_database

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@router.post("/login")
async def login(
    form_data: LoginForm = Depends(LoginForm.as_form),
    db = Depends(get_database)
) -> Token:
    """Process login request."""
    login_manager = LoginManager(db)
    return await login_manager.login(form_data)

@router.get("/me")
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_database)
):
    """Get current user info."""
    login_manager = LoginManager(db)
    return await login_manager.get_current_user(token)

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme)
):
    """Handle logout."""
    # In a stateless JWT system, client just needs to remove the token
    # Could implement a token blacklist here if needed
    return {"message": "Successfully logged out"}
