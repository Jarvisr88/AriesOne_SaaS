"""
Table service for the Core module.
Handles table definitions and schema management.
"""
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy import text

from .base_service import BaseService
from ..models.table_definitions import (
    TableDefinition, ColumnDefinition,
    TableDefinitionSchema, ColumnDefinitionSchema,
    TableType, DataType
)

class TableService(BaseService):
    """Service for handling table definitions and schema management."""

    async def create_table_definition(
        self,
        schema: TableDefinitionSchema
    ) -> TableDefinition:
        """Create a new table definition."""
        # Validate table name uniqueness
        existing = await self._get_table_by_name(schema.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Table with name '{schema.name}' already exists"
            )
        
        return await self.create(TableDefinition, schema)

    async def get_table_definition(
        self,
        table_id: int
    ) -> Optional[TableDefinition]:
        """Get table definition by ID."""
        table = await self.get(TableDefinition, table_id)
        if not table:
            raise HTTPException(
                status_code=404,
                detail=f"Table definition {table_id} not found"
            )
        return table

    async def update_table_definition(
        self,
        table_id: int,
        schema: TableDefinitionSchema
    ) -> TableDefinition:
        """Update table definition."""
        # Check if table exists
        existing = await self.get_table_definition(table_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Table definition {table_id} not found"
            )
        
        # Increment version
        schema.version = existing.version + 1
        
        return await self.update(TableDefinition, table_id, schema)

    async def get_columns(
        self,
        table_id: int
    ) -> List[ColumnDefinition]:
        """Get columns for a table."""
        query = select(ColumnDefinition).where(
            ColumnDefinition.table_definition_id == table_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_column(
        self,
        table_id: int,
        schema: ColumnDefinitionSchema
    ) -> ColumnDefinition:
        """Add a new column to a table."""
        # Validate table exists
        table = await self.get_table_definition(table_id)
        if not table:
            raise HTTPException(
                status_code=404,
                detail=f"Table definition {table_id} not found"
            )
        
        # Validate column name uniqueness
        existing_column = await self._get_column_by_name(table_id, schema.name)
        if existing_column:
            raise HTTPException(
                status_code=400,
                detail=f"Column '{schema.name}' already exists in table"
            )
        
        schema.table_definition_id = table_id
        return await self.create(ColumnDefinition, schema)

    async def generate_migration(
        self,
        table_id: int,
        target_version: Optional[int] = None
    ) -> str:
        """Generate database migration SQL."""
        table = await self.get_table_definition(table_id)
        if not table:
            raise HTTPException(
                status_code=404,
                detail=f"Table definition {table_id} not found"
            )

        try:
            migration_sql = []
            
            if not target_version or target_version > table.version:
                # Forward migration
                migration_sql.append(
                    await self._generate_create_table_sql(table)
                )
                
                # Add indexes
                if table.indexes:
                    for index in table.indexes:
                        migration_sql.append(
                            await self._generate_create_index_sql(
                                table.name,
                                index
                            )
                        )
                
                # Add foreign keys
                if table.foreign_keys:
                    for fk in table.foreign_keys:
                        migration_sql.append(
                            await self._generate_foreign_key_sql(
                                table.name,
                                fk
                            )
                        )
            
            else:
                # Backward migration (rollback)
                migration_sql.append(
                    f"DROP TABLE IF EXISTS {table.name};"
                )
            
            return "\n".join(migration_sql)

        except Exception as e:
            await self._log_error(
                str(e),
                "migration_generation_error",
                f"table_{table_id}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Error generating migration: {str(e)}"
            )

    async def validate_schema(
        self,
        schema: TableDefinitionSchema
    ) -> List[str]:
        """Validate table schema."""
        validation_errors = []
        
        try:
            # Validate table name
            if not schema.name.isidentifier():
                validation_errors.append(
                    "Table name must be a valid identifier"
                )
            
            # Validate primary key
            if not schema.primary_key in schema.schema:
                validation_errors.append(
                    f"Primary key '{schema.primary_key}' not found in schema"
                )
            
            # Validate foreign keys
            if schema.foreign_keys:
                for fk in schema.foreign_keys:
                    if not fk.column in schema.schema:
                        validation_errors.append(
                            f"Foreign key column '{fk.column}' not found in schema"
                        )
            
            # Validate indexes
            if schema.indexes:
                for index in schema.indexes:
                    for column in index.columns:
                        if not column in schema.schema:
                            validation_errors.append(
                                f"Index column '{column}' not found in schema"
                            )
            
            return validation_errors

        except Exception as e:
            await self._log_error(
                str(e),
                "schema_validation_error",
                schema.name
            )
            raise HTTPException(
                status_code=400,
                detail=f"Error validating schema: {str(e)}"
            )

    async def _get_table_by_name(
        self,
        name: str
    ) -> Optional[TableDefinition]:
        """Get table definition by name."""
        query = select(TableDefinition).where(TableDefinition.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_column_by_name(
        self,
        table_id: int,
        name: str
    ) -> Optional[ColumnDefinition]:
        """Get column definition by name."""
        query = select(ColumnDefinition).where(
            and_(
                ColumnDefinition.table_definition_id == table_id,
                ColumnDefinition.name == name
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_create_table_sql(
        self,
        table: TableDefinition
    ) -> str:
        """Generate CREATE TABLE SQL."""
        columns = []
        for name, column in table.schema.items():
            column_def = f"{name} {self._get_sql_type(column.data_type)}"
            
            if not column.is_nullable:
                column_def += " NOT NULL"
            
            if column.default_value is not None:
                column_def += f" DEFAULT {column.default_value}"
            
            if name == table.primary_key:
                column_def += " PRIMARY KEY"
            
            columns.append(column_def)
        
        return f"""
        CREATE TABLE {table.name} (
            {','.join(columns)}
        );
        """

    async def _generate_create_index_sql(
        self,
        table_name: str,
        index: Dict[str, Any]
    ) -> str:
        """Generate CREATE INDEX SQL."""
        unique = "UNIQUE " if index.get('unique', False) else ""
        columns = ', '.join(index['columns'])
        where = f" WHERE {index['where']}" if index.get('where') else ""
        
        return f"""
        CREATE {unique}INDEX {index['name']}
        ON {table_name} ({columns}){where};
        """

    async def _generate_foreign_key_sql(
        self,
        table_name: str,
        fk: Dict[str, Any]
    ) -> str:
        """Generate ALTER TABLE ADD FOREIGN KEY SQL."""
        on_delete = f" ON DELETE {fk['on_delete']}" if fk.get('on_delete') else ""
        on_update = f" ON UPDATE {fk['on_update']}" if fk.get('on_update') else ""
        
        return f"""
        ALTER TABLE {table_name}
        ADD CONSTRAINT fk_{table_name}_{fk['column']}
        FOREIGN KEY ({fk['column']})
        REFERENCES {fk['references_table']} ({fk['references_column']}){on_delete}{on_update};
        """

    def _get_sql_type(self, data_type: DataType) -> str:
        """Convert DataType to SQL type."""
        type_mapping = {
            DataType.STRING: "VARCHAR",
            DataType.INTEGER: "INTEGER",
            DataType.DECIMAL: "DECIMAL",
            DataType.BOOLEAN: "BOOLEAN",
            DataType.DATE: "DATE",
            DataType.DATETIME: "TIMESTAMP",
            DataType.JSON: "JSONB",
            DataType.BINARY: "BYTEA"
        }
        return type_mapping.get(data_type, "VARCHAR")
