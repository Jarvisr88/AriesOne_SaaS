"""
Buttons Model Module

This module provides the Button attribute and related functionality for form button management.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ButtonType(str, Enum):
    """Enumeration of button types"""
    SUBMIT = "submit"
    CANCEL = "cancel"
    DELETE = "delete"
    SAVE = "save"
    PRINT = "print"
    CUSTOM = "custom"

class ButtonDefinition(BaseModel):
    """Definition of a button's properties and behavior"""
    id: str
    type: ButtonType
    label: str
    icon: Optional[str] = None
    tooltip: Optional[str] = None
    disabled: bool = False
    visible: bool = True
    permission: Optional[str] = None
    order: int = 0
    custom_class: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "save_button",
                "type": ButtonType.SAVE,
                "label": "Save",
                "icon": "save",
                "tooltip": "Save changes",
                "disabled": False,
                "visible": True,
                "permission": "can_save",
                "order": 1,
                "custom_class": "primary-button"
            }
        }

class ButtonsAttribute:
    """
    A descriptor class for managing form buttons.
    Provides functionality similar to the original ButtonsAttribute but in a more Pythonic way.
    """
    def __init__(self, buttons: List[ButtonDefinition]):
        self.buttons = buttons
        self._validate_buttons()
    
    def _validate_buttons(self):
        """Validate button configurations"""
        seen_ids = set()
        seen_orders = set()
        
        for button in self.buttons:
            if button.id in seen_ids:
                raise ValueError(f"Duplicate button ID: {button.id}")
            if button.order in seen_orders:
                raise ValueError(f"Duplicate button order: {button.order}")
            
            seen_ids.add(button.id)
            seen_orders.add(button.order)
    
    def get_visible_buttons(self, user_permissions: List[str]) -> List[ButtonDefinition]:
        """Get visible buttons based on user permissions"""
        return [
            button for button in sorted(self.buttons, key=lambda x: x.order)
            if button.visible and (
                not button.permission or 
                button.permission in user_permissions
            )
        ]
    
    def enable_button(self, button_id: str):
        """Enable a specific button"""
        for button in self.buttons:
            if button.id == button_id:
                button.disabled = False
                break
    
    def disable_button(self, button_id: str):
        """Disable a specific button"""
        for button in self.buttons:
            if button.id == button_id:
                button.disabled = True
                break
    
    def show_button(self, button_id: str):
        """Show a specific button"""
        for button in self.buttons:
            if button.id == button_id:
                button.visible = True
                break
    
    def hide_button(self, button_id: str):
        """Hide a specific button"""
        for button in self.buttons:
            if button.id == button_id:
                button.visible = False
                break
    
    def update_button_label(self, button_id: str, label: str):
        """Update a button's label"""
        for button in self.buttons:
            if button.id == button_id:
                button.label = label
                break
