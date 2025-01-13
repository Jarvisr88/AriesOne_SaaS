"""
Table endpoints for the Core module.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...services.table_service import TableService
from ...models.table_definitions import (
    TableDefinition, ColumnDefinition,
    TableDefinitionSchema, ColumnDefinitionSchema
)
from ...database import get_session
from ...dependencies import get_current_active_user, check_permission
from ...auth.models import UserInDB

router = APIRouter(prefix="/tables", tags=["tables"])

@router.post("/", response_model=TableDefinition)
async def create_table(
    table_schema: TableDefinitionSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("tables:create"))
) -> TableDefinition:
    """Create a new table definition."""
    table_service = TableService(session)
    
    # Validate schema
    validation_errors = await table_service.validate_schema(table_schema)
    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"validation_errors": validation_errors}
        )
    
    return await table_service.create_table_definition(table_schema)

@router.get("/{table_id}", response_model=TableDefinition)
async def get_table(
    table_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("tables:read"))
) -> TableDefinition:
    """Get table definition by ID."""
    table_service = TableService(session)
    table = await table_service.get_table_definition(table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table {table_id} not found"
        )
    return table

@router.put("/{table_id}", response_model=TableDefinition)
async def update_table(
    table_id: int,
    table_schema: TableDefinitionSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("tables:update"))
) -> TableDefinition:
    """Update table definition."""
    table_service = TableService(session)
    
    # Validate schema
    validation_errors = await table_service.validate_schema(table_schema)
    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"validation_errors": validation_errors}
        )
    
    return await table_service.update_table_definition(table_id, table_schema)

@router.get("/{table_id}/columns", response_model=List[ColumnDefinition])
async def get_columns(
    table_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("tables:read"))
) -> List[ColumnDefinition]:
    """Get columns for a table."""
    table_service = TableService(session)
    return await table_service.get_columns(table_id)

@router.post("/{table_id}/columns", response_model=ColumnDefinition)
async def add_column(
    table_id: int,
    column_schema: ColumnDefinitionSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("tables:update"))
) -> ColumnDefinition:
    """Add a new column to a table."""
    table_service = TableService(session)
    return await table_service.add_column(table_id, column_schema)

@router.get("/{table_id}/migration")
async def generate_migration(
    table_id: int,
    target_version: int = None,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("tables:migrate"))
) -> dict:
    """Generate database migration SQL."""
    table_service = TableService(session)
    migration_sql = await table_service.generate_migration(
        table_id,
        target_version
    )
    return {"migration_sql": migration_sql}
