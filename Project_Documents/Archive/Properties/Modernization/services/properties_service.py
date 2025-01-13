"""Properties services."""
import base64
from datetime import datetime
import locale
from io import BytesIO
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.properties_models import (
    Resource,
    ResourceHistory,
    Setting,
    SettingHistory,
    ResourceType,
    ResourceCreate,
    ResourceUpdate,
    SettingCreate,
    SettingUpdate
)


class ResourceService:
    """Resource service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_resources(
        self,
        culture: Optional[str] = None
    ) -> List[Resource]:
        """Get all resources.
        
        Args:
            culture: Culture code
            
        Returns:
            List of resources
        """
        query = select(Resource)
        if culture:
            query = query.where(Resource.culture == culture)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_resource(
        self,
        name: str,
        culture: Optional[str] = None
    ) -> Optional[Resource]:
        """Get resource by name.
        
        Args:
            name: Resource name
            culture: Culture code
            
        Returns:
            Resource if found
        """
        query = select(Resource).where(Resource.name == name)
        if culture:
            query = query.where(Resource.culture == culture)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_resource(
        self,
        data: ResourceCreate,
        user_id: int
    ) -> Resource:
        """Create resource.
        
        Args:
            data: Resource data
            user_id: Creating user ID
            
        Returns:
            Created resource
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate culture
        if data.culture:
            try:
                locale.setlocale(locale.LC_ALL, data.culture)
            except locale.Error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid culture code: {data.culture}"
                )
        
        # Process value based on type
        if data.type == ResourceType.IMAGE:
            try:
                image_data = base64.b64decode(data.value)
                img = Image.open(BytesIO(image_data))
                
                if img.format not in {'PNG', 'JPEG', 'GIF'}:
                    raise ValueError("Unsupported image format")
                
                binary_value = image_data
                string_value = None
                metadata = {
                    'width': img.size[0],
                    'height': img.size[1],
                    'format': img.format
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid image: {str(e)}"
                )
        else:
            binary_value = None
            string_value = data.value
            metadata = data.metadata
        
        resource = Resource(
            name=data.name,
            type=data.type,
            culture=data.culture,
            string_value=string_value,
            binary_value=binary_value,
            metadata=metadata,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.session.add(resource)
        await self.session.commit()
        return resource
    
    async def update_resource(
        self,
        name: str,
        data: ResourceUpdate,
        user_id: int
    ) -> Resource:
        """Update resource.
        
        Args:
            name: Resource name
            data: Update data
            user_id: Updating user ID
            
        Returns:
            Updated resource
            
        Raises:
            HTTPException: If not found
        """
        resource = await self.get_resource(name)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
        
        # Create history record
        history = ResourceHistory(
            resource_id=resource.id,
            type=resource.type,
            culture=resource.culture,
            string_value=resource.string_value,
            binary_value=resource.binary_value,
            metadata=resource.metadata,
            created_by=user_id,
            reason=data.reason
        )
        self.session.add(history)
        
        # Process value based on type
        if data.type == ResourceType.IMAGE:
            try:
                image_data = base64.b64decode(data.value)
                img = Image.open(BytesIO(image_data))
                
                if img.format not in {'PNG', 'JPEG', 'GIF'}:
                    raise ValueError("Unsupported image format")
                
                resource.binary_value = image_data
                resource.string_value = None
                resource.metadata = {
                    'width': img.size[0],
                    'height': img.size[1],
                    'format': img.format
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid image: {str(e)}"
                )
        else:
            resource.binary_value = None
            resource.string_value = data.value
            resource.metadata = data.metadata
        
        resource.type = data.type
        resource.culture = data.culture
        resource.updated_by = user_id
        
        await self.session.commit()
        return resource
    
    async def get_resource_history(
        self,
        name: str
    ) -> List[ResourceHistory]:
        """Get resource history.
        
        Args:
            name: Resource name
            
        Returns:
            List of history records
        """
        resource = await self.get_resource(name)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
        
        query = select(ResourceHistory).where(
            ResourceHistory.resource_id == resource.id
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class SettingService:
    """Setting service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_settings(self) -> List[Setting]:
        """Get all settings.
        
        Returns:
            List of settings
        """
        query = select(Setting)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_setting(self, key: str) -> Optional[Setting]:
        """Get setting by key.
        
        Args:
            key: Setting key
            
        Returns:
            Setting if found
        """
        query = select(Setting).where(Setting.key == key)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_setting(
        self,
        data: SettingCreate,
        user_id: int
    ) -> Setting:
        """Create setting.
        
        Args:
            data: Setting data
            user_id: Creating user ID
            
        Returns:
            Created setting
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate value
        if data.validation:
            try:
                self._validate_value(data.value, data.validation)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        setting = Setting(
            key=data.key,
            value=data.value,
            type=data.type,
            description=data.description,
            validation=data.validation,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.session.add(setting)
        await self.session.commit()
        return setting
    
    async def update_setting(
        self,
        key: str,
        data: SettingUpdate,
        user_id: int
    ) -> Setting:
        """Update setting.
        
        Args:
            key: Setting key
            data: Update data
            user_id: Updating user ID
            
        Returns:
            Updated setting
            
        Raises:
            HTTPException: If not found
        """
        setting = await self.get_setting(key)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setting not found"
            )
        
        # Validate value
        if data.validation or setting.validation:
            try:
                self._validate_value(
                    data.value,
                    data.validation or setting.validation
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        # Create history record
        history = SettingHistory(
            setting_id=setting.id,
            value=setting.value,
            created_by=user_id,
            reason=data.reason
        )
        self.session.add(history)
        
        # Update setting
        setting.value = data.value
        if data.description is not None:
            setting.description = data.description
        if data.validation is not None:
            setting.validation = data.validation
        setting.updated_by = user_id
        
        await self.session.commit()
        return setting
    
    async def get_setting_history(
        self,
        key: str
    ) -> List[SettingHistory]:
        """Get setting history.
        
        Args:
            key: Setting key
            
        Returns:
            List of history records
        """
        setting = await self.get_setting(key)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setting not found"
            )
        
        query = select(SettingHistory).where(
            SettingHistory.setting_id == setting.id
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    def _validate_value(self, value: Any, validation: str) -> None:
        """Validate setting value.
        
        Args:
            value: Value to validate
            validation: Validation rule
            
        Raises:
            ValueError: If validation fails
        """
        # Add validation rules here
        if validation == "positive_integer":
            if not isinstance(value, int) or value <= 0:
                raise ValueError("Value must be a positive integer")
        
        elif validation == "email":
            if not isinstance(value, str) or '@' not in value:
                raise ValueError("Value must be a valid email")
        
        elif validation == "url":
            if not isinstance(value, str) or not value.startswith(('http://', 'https://')):
                raise ValueError("Value must be a valid URL")
        
        elif validation == "boolean":
            if not isinstance(value, bool):
                raise ValueError("Value must be a boolean")
        
        elif validation.startswith("range:"):
            try:
                min_val, max_val = map(float, validation[6:].split(','))
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    raise ValueError(f"Value must be between {min_val} and {max_val}")
            except ValueError:
                raise ValueError("Invalid range validation")
