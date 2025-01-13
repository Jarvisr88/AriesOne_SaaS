"""
Services for the Controls module.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import aiohttp
import json
from .models import Address, NameFormat, ChangeTracker, ValidationResult
from ..Core.monitoring.logger import Logger

class AddressService:
    """Service for address validation and management."""
    
    def __init__(self, config: Dict[str, Any], logger: Logger):
        self.config = config
        self.logger = logger
        self.mapping_api_key = config['mapping_api_key']
        self.validation_api_url = config['validation_api_url']
    
    async def validate_address(self, address: Address) -> ValidationResult:
        """Validate address using external service."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.validation_api_url,
                    json=address.dict(),
                    headers={'X-API-Key': self.mapping_api_key}
                ) as response:
                    data = await response.json()
                    
                    result = ValidationResult(
                        is_valid=data['is_valid'],
                        errors=data.get('errors', []),
                        warnings=data.get('warnings', []),
                        suggestions=data.get('suggestions', []),
                        metadata=data.get('metadata', {})
                    )
                    
                    if result.is_valid:
                        address.validated = True
                        address.validation_date = datetime.utcnow()
                        if 'coordinates' in data:
                            address.latitude = data['coordinates']['lat']
                            address.longitude = data['coordinates']['lng']
                    
                    return result
                    
        except Exception as e:
            self.logger.error(f"Address validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation service error: {str(e)}"]
            )
    
    async def get_coordinates(self, address: Address) -> Tuple[Optional[float], Optional[float]]:
        """Get coordinates for address."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config['geocoding_api_url']}",
                    params={
                        'address': f"{address.street1}, {address.city}, {address.state} {address.zip_code}",
                        'key': self.mapping_api_key
                    }
                ) as response:
                    data = await response.json()
                    
                    if data['status'] == 'OK':
                        location = data['results'][0]['geometry']['location']
                        return location['lat'], location['lng']
                    else:
                        self.logger.warning(f"Geocoding failed: {data['status']}")
                        return None, None
                        
        except Exception as e:
            self.logger.error(f"Geocoding failed: {str(e)}")
            return None, None

class NameFormatService:
    """Service for name formatting and validation."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def validate_name(self, name: NameFormat) -> ValidationResult:
        """Validate name format."""
        errors = []
        warnings = []
        
        # Check for common issues
        if any(char.isdigit() for char in name.first_name):
            errors.append("First name should not contain numbers")
        
        if any(char.isdigit() for char in name.last_name):
            errors.append("Last name should not contain numbers")
        
        if name.middle_name and len(name.middle_name) == 1:
            warnings.append("Consider using full middle name instead of initial")
        
        if name.prefix and name.prefix.lower() not in ['mr', 'mrs', 'ms', 'dr', 'prof']:
            warnings.append("Unusual name prefix")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def standardize_name(self, name: NameFormat) -> NameFormat:
        """Standardize name format."""
        # Capitalize first letters
        name.first_name = name.first_name.title()
        name.last_name = name.last_name.title()
        if name.middle_name:
            name.middle_name = name.middle_name.title()
        
        # Standardize prefix
        if name.prefix:
            name.prefix = name.prefix.lower()
            if name.prefix in ['mr.', 'mr']:
                name.prefix = 'Mr.'
            elif name.prefix in ['mrs.', 'mrs']:
                name.prefix = 'Mrs.'
            elif name.prefix in ['ms.', 'ms']:
                name.prefix = 'Ms.'
            elif name.prefix in ['dr.', 'dr']:
                name.prefix = 'Dr.'
            elif name.prefix in ['prof.', 'prof']:
                name.prefix = 'Prof.'
        
        return name

class ChangeTrackingService:
    """Service for tracking changes to data."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    async def track_change(
        self,
        entity_type: str,
        entity_id: str,
        changes: List[ChangeTracker]
    ) -> None:
        """Track changes to an entity."""
        try:
            # Log changes
            for change in changes:
                self.logger.info(
                    f"Change tracked for {entity_type} {entity_id}",
                    entity_type=entity_type,
                    entity_id=entity_id,
                    field=change.field_name,
                    old_value=change.old_value,
                    new_value=change.new_value,
                    changed_by=change.changed_by,
                    reason=change.reason
                )
            
            # Store changes in database
            # This would be implemented based on your storage solution
            pass
            
        except Exception as e:
            self.logger.error(
                f"Failed to track changes: {str(e)}",
                entity_type=entity_type,
                entity_id=entity_id,
                error=str(e)
            )
            raise
    
    async def get_change_history(
        self,
        entity_type: str,
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ChangeTracker]:
        """Get change history for an entity."""
        try:
            # Retrieve changes from database
            # This would be implemented based on your storage solution
            changes: List[ChangeTracker] = []
            return changes
            
        except Exception as e:
            self.logger.error(
                f"Failed to get change history: {str(e)}",
                entity_type=entity_type,
                entity_id=entity_id,
                error=str(e)
            )
            raise
