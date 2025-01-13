"""
Audit Model for PriceUtilities Module.
Handles tracking of all price-related changes and operations.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class AuditActionType(Enum):
    """Enumeration of possible audit action types"""
    PRICE_CREATE = "price_create"
    PRICE_UPDATE = "price_update"
    PRICE_DELETE = "price_delete"
    ICD_CODE_LINK = "icd_code_link"
    PARAMETER_CHANGE = "parameter_change"
    BULK_UPDATE = "bulk_update"

@dataclass
class AuditEntry:
    """
    Represents a single audit entry in the system.
    Tracks all changes to pricing data with complete metadata.
    """
    id: Optional[int] = None
    action_type: AuditActionType = None
    entity_type: str = None
    entity_id: str = None
    user_id: str = None
    timestamp: datetime = None
    old_value: Dict[str, Any] = None
    new_value: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    ip_address: str = None
    
    def __post_init__(self):
        """Initialize default values if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary format"""
        return {
            'id': self.id,
            'action_type': self.action_type.value if self.action_type else None,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'metadata': self.metadata,
            'ip_address': self.ip_address
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Create an audit entry from dictionary data"""
        if 'action_type' in data and data['action_type']:
            data['action_type'] = AuditActionType(data['action_type'])
        if 'timestamp' in data and data['timestamp']:
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
