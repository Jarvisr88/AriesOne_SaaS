"""
Update Processing Service for PriceUtilities Module.
Handles bulk updates and processing of price-related changes.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..models.price_list import PriceList
from ..models.audit import AuditEntry, AuditActionType
from ..repositories.price_list import PriceListRepository
from ..repositories.parameters import ParameterRepository
from ..services.validation_service import ValidationService
from ..services.audit_service import AuditService

class UpdateProcessingService:
    """Service for handling bulk updates and processing changes"""
    
    def __init__(
        self,
        price_list_repo: PriceListRepository,
        parameter_repo: ParameterRepository,
        validation_service: ValidationService,
        audit_service: AuditService,
        max_workers: int = 4
    ):
        self.price_list_repo = price_list_repo
        self.parameter_repo = parameter_repo
        self.validation_service = validation_service
        self.audit_service = audit_service
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def process_bulk_update(
        self,
        updates: List[Dict[str, Any]],
        user_id: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Process bulk updates to price list items
        
        Args:
            updates: List of update operations
            user_id: ID of user performing the update
            ip_address: IP address of the request
            
        Returns:
            Dictionary containing success and failure counts
        """
        results = {
            'total': len(updates),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Validate all updates first
        validation_tasks = [
            self.validation_service.validate_price_update(update)
            for update in updates
        ]
        
        validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Process valid updates
        for update, validation_result in zip(updates, validation_results):
            try:
                if isinstance(validation_result, Exception):
                    raise validation_result
                    
                # Process the update
                await self._process_single_update(update, user_id, ip_address)
                results['successful'] += 1
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'item_id': update.get('item_id'),
                    'error': str(e)
                })
                
        return results
        
    async def _process_single_update(
        self,
        update: Dict[str, Any],
        user_id: str,
        ip_address: str
    ) -> None:
        """Process a single price update operation"""
        item_id = update['item_id']
        old_item = await self.price_list_repo.get_by_id(item_id)
        
        if not old_item:
            raise ValueError(f"Item {item_id} not found")
            
        # Create new item with updates
        new_item = PriceList(
            **{**old_item.to_dict(), **update}
        )
        
        # Save the update
        await self.price_list_repo.update(new_item)
        
        # Create audit entry
        audit_entry = AuditEntry(
            action_type=AuditActionType.PRICE_UPDATE,
            entity_type='price_list',
            entity_id=item_id,
            user_id=user_id,
            old_value=old_item.to_dict(),
            new_value=new_item.to_dict(),
            ip_address=ip_address
        )
        
        await self.audit_service.log_entry(audit_entry)
        
    async def schedule_future_update(
        self,
        update: Dict[str, Any],
        effective_date: datetime,
        user_id: str
    ) -> str:
        """Schedule a price update for future application"""
        # Validate the update
        await self.validation_service.validate_price_update(update)
        
        # Store the scheduled update in parameters
        parameter = {
            'type': 'SCHEDULED_UPDATE',
            'effective_date': effective_date,
            'update_data': update,
            'status': 'PENDING',
            'created_by': user_id
        }
        
        parameter_id = await self.parameter_repo.create(parameter)
        return parameter_id
        
    async def process_scheduled_updates(self) -> Dict[str, int]:
        """Process any scheduled updates that are due"""
        current_time = datetime.utcnow()
        
        # Get all due updates
        due_updates = await self.parameter_repo.get_due_updates(current_time)
        
        results = {
            'processed': 0,
            'failed': 0
        }
        
        for update in due_updates:
            try:
                await self._process_single_update(
                    update['update_data'],
                    update['created_by'],
                    'SYSTEM'
                )
                await self.parameter_repo.mark_update_complete(update['id'])
                results['processed'] += 1
                
            except Exception:
                await self.parameter_repo.mark_update_failed(update['id'])
                results['failed'] += 1
                
        return results
