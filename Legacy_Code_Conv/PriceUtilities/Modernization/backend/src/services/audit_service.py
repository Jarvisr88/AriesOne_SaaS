"""
Audit Service for PriceUtilities Module.
Handles logging and retrieval of audit records.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from ..models.audit import AuditEntry, AuditActionType
from ..repositories.base import BaseRepository

class AuditService:
    """Service for handling audit logging and retrieval"""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
        
    async def log_entry(self, entry: AuditEntry) -> str:
        """
        Log an audit entry
        
        Args:
            entry: AuditEntry object to log
            
        Returns:
            ID of the created audit entry
        """
        # Convert entry to dictionary format
        entry_dict = entry.to_dict()
        
        # Add additional metadata
        entry_dict['metadata'].update({
            'logged_at': datetime.utcnow().isoformat(),
            'version': '1.0'
        })
        
        # Store the entry
        entry_id = await self.repository.create(entry_dict)
        return entry_id
        
    async def get_entries(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action_type: Optional[AuditActionType] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEntry]:
        """
        Retrieve audit entries based on various filters
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
            action_type: Optional action type filter
            user_id: Optional user ID filter
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of AuditEntry objects matching the filters
        """
        # Build query filters
        filters = {}
        
        if start_date:
            filters['timestamp__gte'] = start_date
            
        if end_date:
            filters['timestamp__lte'] = end_date
            
        if entity_type:
            filters['entity_type'] = entity_type
            
        if entity_id:
            filters['entity_id'] = entity_id
            
        if action_type:
            filters['action_type'] = action_type.value
            
        if user_id:
            filters['user_id'] = user_id
            
        # Retrieve entries
        entries = await self.repository.find(
            filters,
            limit=limit,
            offset=offset,
            sort_by='timestamp',
            sort_direction='desc'
        )
        
        # Convert to AuditEntry objects
        return [AuditEntry.from_dict(entry) for entry in entries]
        
    async def get_entry_by_id(self, entry_id: str) -> Optional[AuditEntry]:
        """Retrieve a specific audit entry by ID"""
        entry_dict = await self.repository.get_by_id(entry_id)
        if entry_dict:
            return AuditEntry.from_dict(entry_dict)
        return None
        
    async def get_changes_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get change history for a specific entity
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of changes with before/after values
        """
        entries = await self.get_entries(
            start_date=start_date,
            end_date=end_date,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        changes = []
        for entry in entries:
            if entry.old_value and entry.new_value:
                change = {
                    'timestamp': entry.timestamp,
                    'user_id': entry.user_id,
                    'action_type': entry.action_type.value,
                    'changes': self._compute_changes(
                        entry.old_value,
                        entry.new_value
                    )
                }
                changes.append(change)
                
        return changes
        
    def _compute_changes(
        self,
        old_value: Dict[str, Any],
        new_value: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Compute the differences between old and new values"""
        changes = []
        
        all_keys = set(old_value.keys()) | set(new_value.keys())
        
        for key in all_keys:
            old_val = old_value.get(key)
            new_val = new_value.get(key)
            
            if old_val != new_val:
                changes.append({
                    'field': key,
                    'old_value': old_val,
                    'new_value': new_val
                })
                
        return changes
