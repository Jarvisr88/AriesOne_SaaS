"""
Button Service Module

This module provides services for managing form buttons.
"""
from typing import List, Optional, Dict
from ..models.buttons import ButtonDefinition, ButtonsAttribute
from .base_service import BaseService
from fastapi import HTTPException

class ButtonService(BaseService):
    """Service for managing form buttons"""
    
    def __init__(self):
        """Initialize button service"""
        self._form_buttons: Dict[str, ButtonsAttribute] = {}
    
    async def get_form_buttons(
        self,
        form_id: str,
        user_permissions: List[str]
    ) -> List[ButtonDefinition]:
        """
        Get visible buttons for a form based on user permissions.
        
        Args:
            form_id: The ID of the form
            user_permissions: List of user permissions
            
        Returns:
            List of visible button definitions
            
        Raises:
            HTTPException: If form buttons are not found
        """
        buttons_attr = await self._get_buttons_attribute(form_id)
        return buttons_attr.get_visible_buttons(user_permissions)
    
    async def update_button_state(
        self,
        form_id: str,
        button_id: str,
        visible: Optional[bool] = None,
        enabled: Optional[bool] = None
    ):
        """
        Update button state.
        
        Args:
            form_id: The ID of the form
            button_id: The ID of the button to update
            visible: Optional visibility state
            enabled: Optional enabled state
            
        Raises:
            HTTPException: If button update fails
        """
        buttons_attr = await self._get_buttons_attribute(form_id)
        
        if visible is not None:
            if visible:
                buttons_attr.show_button(button_id)
            else:
                buttons_attr.hide_button(button_id)
                
        if enabled is not None:
            if enabled:
                buttons_attr.enable_button(button_id)
            else:
                buttons_attr.disable_button(button_id)
                
        await self._save_buttons_attribute(form_id, buttons_attr)
    
    async def update_button_label(
        self,
        form_id: str,
        button_id: str,
        label: str
    ):
        """
        Update button label.
        
        Args:
            form_id: The ID of the form
            button_id: The ID of the button to update
            label: New label for the button
            
        Raises:
            HTTPException: If button update fails
        """
        buttons_attr = await self._get_buttons_attribute(form_id)
        buttons_attr.update_button_label(button_id, label)
        await self._save_buttons_attribute(form_id, buttons_attr)
    
    async def _get_buttons_attribute(self, form_id: str) -> ButtonsAttribute:
        """
        Get ButtonsAttribute for a form.
        
        Args:
            form_id: The ID of the form
            
        Returns:
            ButtonsAttribute instance
            
        Raises:
            HTTPException: If form buttons are not found
        """
        try:
            # In real implementation, fetch from database or cache
            if form_id not in self._form_buttons:
                # Create default buttons if not exists
                default_buttons = self._create_default_buttons()
                self._form_buttons[form_id] = ButtonsAttribute(default_buttons)
            return self._form_buttons[form_id]
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Form buttons not found: {str(e)}"
            )
    
    async def _save_buttons_attribute(
        self,
        form_id: str,
        buttons_attr: ButtonsAttribute
    ):
        """
        Save ButtonsAttribute for a form.
        
        Args:
            form_id: The ID of the form
            buttons_attr: ButtonsAttribute instance to save
            
        Raises:
            HTTPException: If save operation fails
        """
        try:
            # In real implementation, save to database
            self._form_buttons[form_id] = buttons_attr
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save button state: {str(e)}"
            )
    
    def _create_default_buttons(self) -> List[ButtonDefinition]:
        """
        Create default button definitions.
        
        Returns:
            List of default ButtonDefinition instances
        """
        from ..models.buttons import ButtonType
        
        return [
            ButtonDefinition(
                id="save",
                type=ButtonType.SAVE,
                label="Save",
                icon="save",
                order=1
            ),
            ButtonDefinition(
                id="cancel",
                type=ButtonType.CANCEL,
                label="Cancel",
                icon="cancel",
                order=2
            ),
            ButtonDefinition(
                id="delete",
                type=ButtonType.DELETE,
                label="Delete",
                icon="delete",
                permission="can_delete",
                order=3
            )
        ]
