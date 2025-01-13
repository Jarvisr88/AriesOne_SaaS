"""
Configuration management routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from pathlib import Path
from .config_manager import ConfigManager, EnvironmentConfig
from ..auth.login_form import LoginManager
import yaml

router = APIRouter(prefix="/config", tags=["configuration"])
config_manager = ConfigManager("config")

@router.get("/environments/{env_name}")
async def get_environment_config(
    env_name: str,
    current_user = Depends(LoginManager.check_admin_user)
) -> EnvironmentConfig:
    """Get configuration for specified environment."""
    return config_manager.load_config(env_name)

@router.post("/environments")
async def save_environment_config(
    config: Dict[str, Any],
    current_user = Depends(LoginManager.check_admin_user)
):
    """Save environment configuration."""
    config_manager.save_config(config)
    return {"message": "Configuration saved successfully"}

@router.post("/migrate-odbc")
async def migrate_odbc_config(
    odbc_file: UploadFile = File(...),
    current_user = Depends(LoginManager.check_admin_user)
):
    """Migrate ODBC configuration to new format."""
    try:
        # Save uploaded file temporarily
        temp_file = Path("temp_odbc.ini")
        with open(temp_file, "wb") as f:
            f.write(await odbc_file.read())

        # Migrate configuration
        config_manager.migrate_odbc_config(str(temp_file))

        # Clean up
        temp_file.unlink()

        return {"message": "ODBC configuration migrated successfully"}

    except Exception as e:
        if temp_file.exists():
            temp_file.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to migrate ODBC configuration: {str(e)}"
        )

@router.get("/database-url/{env_name}")
async def get_database_url(
    env_name: str,
    current_user = Depends(LoginManager.check_admin_user)
) -> str:
    """Get database URL for specified environment."""
    return config_manager.get_database_url(env_name)

@router.get("/connection-pool/{env_name}")
async def get_connection_pool_config(
    env_name: str,
    current_user = Depends(LoginManager.check_admin_user)
) -> Dict[str, Any]:
    """Get connection pool configuration."""
    return config_manager.get_connection_pool_config(env_name)
