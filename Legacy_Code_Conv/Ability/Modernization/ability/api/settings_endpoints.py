"""
Settings API Endpoints Module

This module provides FastAPI endpoints for integration settings.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.settings import IntegrationSettings
from ..services.settings_service import SettingsService
from ..dependencies import (
    get_db,
    get_current_user,
    get_settings_service,
    verify_api_key
)

router = APIRouter(prefix="/api/v1/ability/settings", tags=["settings"])

@router.post("/", response_model=IntegrationSettings)
async def create_settings(
    settings: IntegrationSettings,
    current_user = Depends(get_current_user),
    api_key: str = Security(verify_api_key),
    settings_service: SettingsService = Depends(get_settings_service),
    db: AsyncSession = Depends(get_db)
) -> IntegrationSettings:
    """Create new integration settings."""
    try:
        return await settings_service.create_settings(settings, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{settings_id}", response_model=IntegrationSettings)
async def get_settings(
    settings_id: UUID,
    current_user = Depends(get_current_user),
    api_key: str = Security(verify_api_key),
    settings_service: SettingsService = Depends(get_settings_service),
    db: AsyncSession = Depends(get_db)
) -> IntegrationSettings:
    """Get integration settings by ID."""
    settings = await settings_service.get_settings(settings_id, db)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

@router.put("/{settings_id}", response_model=IntegrationSettings)
async def update_settings(
    settings_id: UUID,
    settings: IntegrationSettings,
    current_user = Depends(get_current_user),
    api_key: str = Security(verify_api_key),
    settings_service: SettingsService = Depends(get_settings_service),
    db: AsyncSession = Depends(get_db)
) -> IntegrationSettings:
    """Update integration settings."""
    try:
        return await settings_service.update_settings(settings_id, settings, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{settings_id}")
async def delete_settings(
    settings_id: UUID,
    current_user = Depends(get_current_user),
    api_key: str = Security(verify_api_key),
    settings_service: SettingsService = Depends(get_settings_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete integration settings."""
    try:
        await settings_service.delete_settings(settings_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
