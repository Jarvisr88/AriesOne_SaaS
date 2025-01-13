"""
Table Name API Endpoints Module

This module provides FastAPI endpoints for table names.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from ..models.table_name import (
    TableName,
    TableCategory,
    TableMetadata
)
from ..services.table_name_service import TableNameService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.get("/tables/{table_name}", response_model=TableMetadata)
async def get_table_metadata(
    table_name: TableName,
    current_user: User = Depends(get_current_user)
) -> TableMetadata:
    """
    Get table metadata.
    
    Args:
        table_name: Table name
        current_user: The current authenticated user
        
    Returns:
        Table metadata
    """
    service = TableNameService()
    return await service.get_table_metadata(table_name)

@router.get("/tables/category/{category}", response_model=List[TableMetadata])
async def get_tables_by_category(
    category: TableCategory,
    current_user: User = Depends(get_current_user)
) -> List[TableMetadata]:
    """
    Get tables by category.
    
    Args:
        category: Table category
        current_user: The current authenticated user
        
    Returns:
        List of table metadata
    """
    service = TableNameService()
    return await service.get_tables_by_category(category)

@router.get("/tables/normalize/{table_name}", response_model=str)
async def normalize_table_name(
    table_name: str,
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Normalize table name.
    
    Args:
        table_name: Table name to normalize
        current_user: The current authenticated user
        
    Returns:
        Normalized table name
    """
    service = TableNameService()
    return await service.normalize_table_name(table_name)

@router.put("/tables/{table_name}", response_model=TableMetadata)
async def update_table_metadata(
    table_name: TableName,
    description: Optional[str] = None,
    schema_version: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> TableMetadata:
    """
    Update table metadata.
    
    Args:
        table_name: Table name
        description: New description
        schema_version: New schema version
        current_user: The current authenticated user
        
    Returns:
        Updated table metadata
    """
    service = TableNameService()
    return await service.update_table_metadata(
        table_name,
        description,
        schema_version
    )

@router.get("/tables", response_model=List[TableMetadata])
async def get_all_tables(
    current_user: User = Depends(get_current_user)
) -> List[TableMetadata]:
    """
    Get all table metadata.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        List of all table metadata
    """
    service = TableNameService()
    return await service.get_all_tables()

@router.get("/tables/categories", response_model=List[TableCategory])
async def get_table_categories(
    current_user: User = Depends(get_current_user)
) -> List[TableCategory]:
    """
    Get all table categories.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        List of table categories
    """
    service = TableNameService()
    return await service.get_table_categories()
