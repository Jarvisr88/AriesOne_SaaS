from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ChangeType(str, Enum):
    """Enumeration of change types"""
    MODIFIED = "modified"
    ADDED = "added"
    REMOVED = "removed"

class FieldChange(BaseModel):
    """Model for tracking individual field changes"""
    field_name: str = Field(..., description="Name of the changed field")
    old_value: Optional[Any] = Field(None, description="Previous field value")
    new_value: Optional[Any] = Field(None, description="New field value")
    change_type: ChangeType = Field(..., description="Type of change")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the change occurred")
    user_id: Optional[str] = Field(None, description="ID of user making the change")

class ChangeTracker(BaseModel):
    """
    Model for tracking changes to form controls
    Includes audit trail capabilities
    """
    control_id: str = Field(..., description="Unique identifier for the control")
    control_type: str = Field(..., description="Type of control being tracked")
    changes: Dict[str, FieldChange] = Field(
        default_factory=dict,
        description="Map of field names to their changes"
    )
    
    def track_change(
        self,
        field_name: str,
        old_value: Any,
        new_value: Any,
        user_id: Optional[str] = None
    ) -> None:
        """Record a change to a field"""
        if old_value != new_value:
            change_type = (
                ChangeType.ADDED if old_value is None
                else ChangeType.REMOVED if new_value is None
                else ChangeType.MODIFIED
            )
            
            self.changes[field_name] = FieldChange(
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                change_type=change_type,
                user_id=user_id
            )
    
    def get_changes(self) -> Dict[str, FieldChange]:
        """Get all tracked changes"""
        return self.changes
    
    def has_changes(self) -> bool:
        """Check if there are any tracked changes"""
        return len(self.changes) > 0
    
    def clear_changes(self) -> None:
        """Clear all tracked changes"""
        self.changes.clear()
