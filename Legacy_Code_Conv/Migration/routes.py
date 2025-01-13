"""
Database migration routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
from .migration_manager import MigrationManager
from ..Config.config_manager import ConfigManager
from ..auth.login_form import LoginManager

router = APIRouter(prefix="/migration", tags=["migration"])

@router.post("/tables")
async def migrate_tables(
    odbc_string: str,
    tables: List[str],
    env_name: Optional[str] = "development",
    current_user = Depends(LoginManager.check_admin_user)
):
    """Migrate specified tables from ODBC to PostgreSQL."""
    try:
        config_manager = ConfigManager("config")
        migration_manager = MigrationManager(
            config_manager,
            "migrations"
        )
        
        await migration_manager.migrate_database(
            odbc_string,
            tables,
            env_name
        )
        
        return {"message": "Migration completed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Migration failed: {str(e)}"
        )

@router.get("/verify/{table_name}")
async def verify_migration(
    table_name: str,
    env_name: Optional[str] = "development",
    current_user = Depends(LoginManager.check_admin_user)
):
    """Verify migrated data for specified table."""
    try:
        config_manager = ConfigManager("config")
        migration_manager = MigrationManager(
            config_manager,
            "migrations"
        )
        
        # Load checksum
        checksums = {}
        if migration_manager.checksum_file.exists():
            with open(migration_manager.checksum_file, 'r') as f:
                checksums = json.load(f)
        
        if table_name not in checksums:
            raise HTTPException(
                status_code=404,
                detail=f"No migration record found for table: {table_name}"
            )
        
        return checksums[table_name]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )
