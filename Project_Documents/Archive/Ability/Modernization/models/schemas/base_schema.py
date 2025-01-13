from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class BaseSchema(BaseModel):
    """Base Pydantic model with common configuration and fields."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model parsing
        validate_assignment=True,  # Validate during assignment
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    id: Optional[int] = Field(None, description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    is_active: bool = Field(True, description="Active status flag")

class BaseSchemaCreate(BaseModel):
    """Base model for creation operations."""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "is_active": True
            }
        }
    )
    
    is_active: bool = Field(True, description="Active status flag")

class BaseSchemaUpdate(BaseModel):
    """Base model for update operations."""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "is_active": True
            }
        }
    )
    
    is_active: Optional[bool] = Field(None, description="Active status flag")
