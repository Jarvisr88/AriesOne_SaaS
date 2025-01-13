"""
Table Management Service Module

This module provides services for table management and metadata.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4
from fastapi import HTTPException
from pydantic import BaseModel, Field

class TableType(str, Enum):
    """Table type enumeration"""
    SYSTEM = "system"
    USER = "user"
    REFERENCE = "reference"
    TRANSACTION = "transaction"
    AUDIT = "audit"
    ARCHIVE = "archive"

class TableMetadata(BaseModel):
    """Table metadata"""
    schema_name: str
    table_name: str
    display_name: str
    description: Optional[str] = None
    table_type: TableType
    primary_key: List[str]
    columns: Dict[str, Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    permissions: Dict[str, List[str]]
    audit_enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TableManagementService:
    """Service for table management"""
    
    def __init__(self):
        """Initialize table management service"""
        self._tables: Dict[str, TableMetadata] = {}
        self._event_handlers: Dict[str, List[callable]] = {}
    
    async def register_table(
        self,
        schema_name: str,
        table_name: str,
        display_name: str,
        table_type: TableType,
        primary_key: List[str],
        columns: Dict[str, Dict[str, Any]],
        description: Optional[str] = None,
        indexes: Optional[List[Dict[str, Any]]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
        relationships: Optional[List[Dict[str, Any]]] = None,
        permissions: Optional[Dict[str, List[str]]] = None,
        audit_enabled: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TableMetadata:
        """
        Register a new table.
        
        Args:
            schema_name: Database schema name
            table_name: Table name
            display_name: Display name
            table_type: Table type
            primary_key: Primary key columns
            columns: Column definitions
            description: Optional description
            indexes: Optional index definitions
            constraints: Optional constraint definitions
            relationships: Optional relationship definitions
            permissions: Optional permission definitions
            audit_enabled: Enable auditing
            metadata: Optional metadata
            
        Returns:
            Table metadata
            
        Raises:
            HTTPException: If table already exists
        """
        table_key = f"{schema_name}.{table_name}"
        if table_key in self._tables:
            raise HTTPException(
                status_code=400,
                detail=f"Table already exists: {table_key}"
            )
        
        # Create metadata
        table_metadata = TableMetadata(
            schema_name=schema_name,
            table_name=table_name,
            display_name=display_name,
            description=description,
            table_type=table_type,
            primary_key=primary_key,
            columns=columns,
            indexes=indexes or [],
            constraints=constraints or [],
            relationships=relationships or [],
            permissions=permissions or {},
            audit_enabled=audit_enabled,
            metadata=metadata or {}
        )
        
        # Store metadata
        self._tables[table_key] = table_metadata
        
        # Notify handlers
        await self._notify_handlers(
            'table_registered',
            table_key,
            table_metadata
        )
        
        return table_metadata
    
    async def update_table(
        self,
        schema_name: str,
        table_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        columns: Optional[Dict[str, Dict[str, Any]]] = None,
        indexes: Optional[List[Dict[str, Any]]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
        relationships: Optional[List[Dict[str, Any]]] = None,
        permissions: Optional[Dict[str, List[str]]] = None,
        audit_enabled: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TableMetadata:
        """
        Update table metadata.
        
        Args:
            schema_name: Database schema name
            table_name: Table name
            display_name: Optional new display name
            description: Optional new description
            columns: Optional new column definitions
            indexes: Optional new index definitions
            constraints: Optional new constraint definitions
            relationships: Optional new relationship definitions
            permissions: Optional new permission definitions
            audit_enabled: Optional audit setting
            metadata: Optional new metadata
            
        Returns:
            Updated table metadata
            
        Raises:
            HTTPException: If table not found
        """
        table_key = f"{schema_name}.{table_name}"
        table_metadata = self._tables.get(table_key)
        if not table_metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Table not found: {table_key}"
            )
        
        # Update metadata
        if display_name is not None:
            table_metadata.display_name = display_name
        if description is not None:
            table_metadata.description = description
        if columns is not None:
            table_metadata.columns = columns
        if indexes is not None:
            table_metadata.indexes = indexes
        if constraints is not None:
            table_metadata.constraints = constraints
        if relationships is not None:
            table_metadata.relationships = relationships
        if permissions is not None:
            table_metadata.permissions = permissions
        if audit_enabled is not None:
            table_metadata.audit_enabled = audit_enabled
        if metadata:
            table_metadata.metadata.update(metadata)
        
        table_metadata.updated_at = datetime.utcnow()
        
        # Notify handlers
        await self._notify_handlers(
            'table_updated',
            table_key,
            table_metadata
        )
        
        return table_metadata
    
    async def delete_table(
        self,
        schema_name: str,
        table_name: str
    ):
        """
        Delete table metadata.
        
        Args:
            schema_name: Database schema name
            table_name: Table name
            
        Raises:
            HTTPException: If table not found
        """
        table_key = f"{schema_name}.{table_name}"
        table_metadata = self._tables.get(table_key)
        if not table_metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Table not found: {table_key}"
            )
        
        # Delete metadata
        del self._tables[table_key]
        
        # Notify handlers
        await self._notify_handlers(
            'table_deleted',
            table_key,
            table_metadata
        )
    
    async def get_table(
        self,
        schema_name: str,
        table_name: str
    ) -> TableMetadata:
        """
        Get table metadata.
        
        Args:
            schema_name: Database schema name
            table_name: Table name
            
        Returns:
            Table metadata
            
        Raises:
            HTTPException: If table not found
        """
        table_key = f"{schema_name}.{table_name}"
        table_metadata = self._tables.get(table_key)
        if not table_metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Table not found: {table_key}"
            )
        return table_metadata
    
    async def get_tables(
        self,
        schema_name: Optional[str] = None,
        table_type: Optional[TableType] = None
    ) -> List[TableMetadata]:
        """
        Get table metadata matching criteria.
        
        Args:
            schema_name: Optional schema filter
            table_type: Optional type filter
            
        Returns:
            List of table metadata
        """
        tables = self._tables.values()
        
        if schema_name:
            tables = [t for t in tables if t.schema_name == schema_name]
        if table_type:
            tables = [t for t in tables if t.table_type == table_type]
            
        return list(tables)
    
    async def subscribe(
        self,
        event_type: str,
        handler: callable
    ):
        """
        Subscribe to table events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    async def unsubscribe(
        self,
        event_type: str,
        handler: callable
    ):
        """
        Unsubscribe from table events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type in self._event_handlers and handler in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(handler)
    
    async def _notify_handlers(
        self,
        event_type: str,
        table_key: str,
        metadata: TableMetadata
    ):
        """
        Notify event handlers.
        
        Args:
            event_type: Type of event
            table_key: Table key
            metadata: Table metadata
        """
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    await handler(table_key, metadata)
                except Exception as e:
                    # Log error but continue notifying other handlers
                    print(f"Error in table event handler: {e}")
                    continue
