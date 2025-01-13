"""
Table Name Service Module

This module provides services for managing table names and metadata.
"""
from typing import Dict, List, Optional
from ..models.table_name import (
    TableName,
    TableCategory,
    TableMetadata,
    TableRegistry,
    initialize_table_metadata
)
from .base_service import BaseService
from fastapi import HTTPException
from datetime import datetime

class TableNameService(BaseService):
    """Service for managing table names and metadata"""
    
    def __init__(self):
        """Initialize table name service"""
        # Initialize table metadata if not already initialized
        if not TableRegistry._registry:
            initialize_table_metadata()
    
    async def get_table_metadata(
        self,
        table_name: TableName
    ) -> TableMetadata:
        """
        Get table metadata.
        
        Args:
            table_name: Table name
            
        Returns:
            Table metadata
            
        Raises:
            HTTPException: If table metadata not found
        """
        metadata = TableRegistry.get(table_name)
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Table metadata not found: {table_name}"
            )
        return metadata
    
    async def get_tables_by_category(
        self,
        category: TableCategory
    ) -> List[TableMetadata]:
        """
        Get tables by category.
        
        Args:
            category: Table category
            
        Returns:
            List of table metadata
        """
        return [
            metadata
            for metadata in TableRegistry._registry.values()
            if metadata.category == category
        ]
    
    async def normalize_table_name(
        self,
        table_name: str
    ) -> str:
        """
        Normalize table name.
        
        Args:
            table_name: Table name to normalize
            
        Returns:
            Normalized table name
            
        Raises:
            HTTPException: If table name is None
        """
        try:
            return TableRegistry.normalize(table_name)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    
    async def update_table_metadata(
        self,
        table_name: TableName,
        description: Optional[str] = None,
        schema_version: Optional[str] = None
    ) -> TableMetadata:
        """
        Update table metadata.
        
        Args:
            table_name: Table name
            description: New description
            schema_version: New schema version
            
        Returns:
            Updated table metadata
            
        Raises:
            HTTPException: If table metadata not found
        """
        metadata = await self.get_table_metadata(table_name)
        
        if description is not None:
            metadata.description = description
        
        if schema_version is not None:
            metadata.schema_version = schema_version
        
        metadata.updated_at = datetime.utcnow()
        TableRegistry.register(metadata)
        
        return metadata
    
    async def get_all_tables(self) -> List[TableMetadata]:
        """
        Get all table metadata.
        
        Returns:
            List of all table metadata
        """
        return list(TableRegistry._registry.values())
    
    async def get_table_categories(self) -> List[TableCategory]:
        """
        Get all table categories.
        
        Returns:
            List of table categories
        """
        return list(TableCategory)
