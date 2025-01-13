from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.core.config.manager import config_manager
from app.core.security import get_current_admin
from app.core.logging import logger

router = APIRouter()

class ConfigUpdate(BaseModel):
    """Configuration update request"""
    key: str
    value: Any

class ConfigResponse(BaseModel):
    """Configuration response"""
    key: str
    value: Any
    updated_at: str

@router.get(
    "/config/{key}",
    response_model=ConfigResponse,
    summary="Get configuration value",
    description="Get configuration value by key"
)
async def get_config(
    key: str,
    current_admin = Depends(get_current_admin)
):
    """
    Get configuration value with:
    1. Authentication check
    2. Access logging
    3. Error handling
    """
    try:
        value = await config_manager.get_config(key)
        if value is None:
            raise HTTPException(
                status_code=404,
                detail=f"Configuration key '{key}' not found"
            )
            
        return ConfigResponse(
            key=key,
            value=value,
            updated_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Config retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.put(
    "/config",
    response_model=ConfigResponse,
    summary="Update configuration",
    description="Update configuration value"
)
async def update_config(
    update: ConfigUpdate,
    current_admin = Depends(get_current_admin)
):
    """
    Update configuration value with:
    1. Authentication check
    2. Validation
    3. Audit logging
    """
    try:
        await config_manager.set_config(update.key, update.value)
        return ConfigResponse(
            key=update.key,
            value=update.value,
            updated_at=datetime.utcnow().isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Config update error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get(
    "/config/metrics",
    summary="Get configuration metrics",
    description="Get configuration system metrics"
)
async def get_metrics(
    current_admin = Depends(get_current_admin)
):
    """
    Get configuration metrics:
    1. Update counts
    2. Error rates
    3. Cache performance
    4. Validation errors
    """
    try:
        return await config_manager.get_metrics()
    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
