"""
UI Attribute Service Module

This module provides services for handling UI attributes and button configurations.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4
from fastapi import HTTPException
from pydantic import BaseModel, Field

class ButtonConfig(BaseModel):
    """Button configuration"""
    id: str
    text: str
    icon: Optional[str] = None
    tooltip: Optional[str] = None
    enabled: bool = True
    visible: bool = True
    primary: bool = False
    order: int = 0
    action: str
    action_params: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ButtonAttribute(BaseModel):
    """Button attribute configuration"""
    component_id: UUID
    buttons: List[ButtonConfig]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UIAttributeService:
    """Service for handling UI attributes"""
    
    def __init__(self):
        """Initialize UI attribute service"""
        self._button_attributes: Dict[UUID, ButtonAttribute] = {}
        self._event_handlers: Dict[str, List[callable]] = {}
    
    async def create_button_attribute(
        self,
        buttons: List[ButtonConfig],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ButtonAttribute:
        """
        Create a new button attribute.
        
        Args:
            buttons: List of button configurations
            metadata: Optional metadata
            
        Returns:
            Button attribute
        """
        component_id = uuid4()
        
        # Create attribute
        attribute = ButtonAttribute(
            component_id=component_id,
            buttons=buttons,
            metadata=metadata or {}
        )
        
        # Store attribute
        self._button_attributes[component_id] = attribute
        
        # Notify handlers
        await self._notify_handlers(
            'button_attribute_created',
            component_id,
            attribute
        )
        
        return attribute
    
    async def update_button_attribute(
        self,
        component_id: UUID,
        buttons: Optional[List[ButtonConfig]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ButtonAttribute:
        """
        Update a button attribute.
        
        Args:
            component_id: Component ID
            buttons: Optional list of button configurations
            metadata: Optional metadata
            
        Returns:
            Updated button attribute
            
        Raises:
            HTTPException: If attribute not found
        """
        attribute = self._button_attributes.get(component_id)
        if not attribute:
            raise HTTPException(
                status_code=404,
                detail=f"Button attribute not found: {component_id}"
            )
        
        # Update attribute
        if buttons is not None:
            attribute.buttons = buttons
        if metadata:
            attribute.metadata.update(metadata)
        attribute.updated_at = datetime.utcnow()
        
        # Notify handlers
        await self._notify_handlers(
            'button_attribute_updated',
            component_id,
            attribute
        )
        
        return attribute
    
    async def delete_button_attribute(
        self,
        component_id: UUID
    ):
        """
        Delete a button attribute.
        
        Args:
            component_id: Component ID
            
        Raises:
            HTTPException: If attribute not found
        """
        attribute = self._button_attributes.get(component_id)
        if not attribute:
            raise HTTPException(
                status_code=404,
                detail=f"Button attribute not found: {component_id}"
            )
        
        # Delete attribute
        del self._button_attributes[component_id]
        
        # Notify handlers
        await self._notify_handlers(
            'button_attribute_deleted',
            component_id,
            attribute
        )
    
    async def get_button_attribute(
        self,
        component_id: UUID
    ) -> ButtonAttribute:
        """
        Get a button attribute.
        
        Args:
            component_id: Component ID
            
        Returns:
            Button attribute
            
        Raises:
            HTTPException: If attribute not found
        """
        attribute = self._button_attributes.get(component_id)
        if not attribute:
            raise HTTPException(
                status_code=404,
                detail=f"Button attribute not found: {component_id}"
            )
        return attribute
    
    async def get_button_attributes(
        self
    ) -> List[ButtonAttribute]:
        """
        Get all button attributes.
        
        Returns:
            List of button attributes
        """
        return list(self._button_attributes.values())
    
    async def subscribe(
        self,
        event_type: str,
        handler: callable
    ):
        """
        Subscribe to UI attribute events.
        
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
        Unsubscribe from UI attribute events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type in self._event_handlers and handler in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(handler)
    
    async def _notify_handlers(
        self,
        event_type: str,
        component_id: UUID,
        attribute: ButtonAttribute
    ):
        """
        Notify event handlers.
        
        Args:
            event_type: Type of event
            component_id: Component ID
            attribute: Button attribute
        """
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    await handler(component_id, attribute)
                except Exception as e:
                    # Log error but continue notifying other handlers
                    print(f"Error in UI attribute event handler: {e}")
                    continue
