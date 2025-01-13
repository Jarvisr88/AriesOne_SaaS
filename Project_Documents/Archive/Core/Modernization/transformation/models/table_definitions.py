"""
Table definitions for the Core module.
Provides modern SQLAlchemy models for legacy table definitions.
"""
from enum import Enum
from typing import Dict, List, Optional
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, Boolean
from pydantic import BaseModel, Field

from .base import BaseDBModel, BaseSchema

class TableType(str, Enum):
    """Enumeration for table types."""
    MASTER = "master"
    TRANSACTION = "transaction"
    REFERENCE = "reference"
    AUDIT = "audit"
    SYSTEM = "system"

class TableDefinition(BaseDBModel):
    """Database model for table definitions."""
    __tablename__ = "core_table_definitions"

    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    table_type = Column(String(20), nullable=False)
    schema = Column(JSON, nullable=False)
    primary_key = Column(String(50), nullable=False)
    indexes = Column(JSON, nullable=True)
    foreign_keys = Column(JSON, nullable=True)
    permissions = Column(JSON, nullable=False)
    audit_enabled = Column(Boolean, nullable=False, default=True)
    cache_enabled = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=1)

class ColumnDefinition(BaseDBModel):
    """Database model for column definitions."""
    __tablename__ = "core_column_definitions"

    table_definition_id = Column(Integer, ForeignKey("core_table_definitions.id"), nullable=False)
    name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    data_type = Column(String(50), nullable=False)
    is_nullable = Column(Boolean, nullable=False, default=True)
    default_value = Column(String, nullable=True)
    max_length = Column(Integer, nullable=True)
    precision = Column(Integer, nullable=True)
    scale = Column(Integer, nullable=True)
    is_primary_key = Column(Boolean, nullable=False, default=False)
    is_foreign_key = Column(Boolean, nullable=False, default=False)
    foreign_key_table = Column(String(100), nullable=True)
    foreign_key_column = Column(String(100), nullable=True)
    validation_rules = Column(JSON, nullable=True)

# Pydantic Schemas

class DataType(str, Enum):
    """Enumeration for data types."""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    BINARY = "binary"

class IndexDefinition(BaseModel):
    """Schema for index definition."""
    name: str
    columns: List[str]
    unique: bool = False
    where: Optional[str] = None

class ForeignKeyDefinition(BaseModel):
    """Schema for foreign key definition."""
    column: str
    references_table: str
    references_column: str
    on_delete: Optional[str] = None
    on_update: Optional[str] = None

class ValidationRule(BaseModel):
    """Schema for column validation rule."""
    type: str
    params: Dict[str, Any]
    message: str
    severity: str = "error"

class ColumnDefinitionSchema(BaseSchema):
    """Schema for column definition."""
    table_definition_id: int
    name: str
    display_name: str
    description: Optional[str] = None
    data_type: DataType
    is_nullable: bool = True
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    validation_rules: Optional[List[ValidationRule]] = None

class TableDefinitionSchema(BaseSchema):
    """Schema for table definition."""
    name: str
    display_name: str
    description: Optional[str] = None
    table_type: TableType
    schema: Dict[str, ColumnDefinitionSchema]
    primary_key: str
    indexes: Optional[List[IndexDefinition]] = None
    foreign_keys: Optional[List[ForeignKeyDefinition]] = None
    permissions: Dict[str, List[str]]
    audit_enabled: bool = True
    cache_enabled: bool = False
    version: int = 1

# Legacy Table Mappings
LEGACY_TABLES = {
    "tbl_ability_eligibility_payer": TableDefinitionSchema(
        name="ability_eligibility_payer",
        display_name="Eligibility Payer",
        table_type=TableType.MASTER,
        schema={
            "id": ColumnDefinitionSchema(
                name="id",
                display_name="ID",
                data_type=DataType.INTEGER,
                is_primary_key=True
            ),
            # Add other columns based on legacy schema
        },
        primary_key="id",
        permissions={"read": ["*"], "write": ["admin"]}
    ),
    # Add other legacy table definitions
}
