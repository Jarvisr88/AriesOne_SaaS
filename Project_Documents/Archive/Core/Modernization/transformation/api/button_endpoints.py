"""
Button API Endpoints Module

This module provides FastAPI endpoints for managing form buttons.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.buttons import ButtonDefinition, ButtonsAttribute
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.get("/buttons/{form_id}", response_model=List[ButtonDefinition])
async def get_form_buttons(
    form_id: str,
    current_user: User = Depends(get_current_user)
) -> List[ButtonDefinition]:
    """
    Get visible buttons for a form based on user permissions.
    
    Args:
        form_id: The ID of the form
        current_user: The current authenticated user
        
    Returns:
        List of visible button definitions
    """
    try:
        # In real implementation, fetch buttons from form definition service
        buttons = get_form_buttons_from_service(form_id)
        buttons_attr = ButtonsAttribute(buttons)
        return buttons_attr.get_visible_buttons(current_user.permissions)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Form buttons not found: {str(e)}")

@router.patch("/buttons/{form_id}/{button_id}/state")
async def update_button_state(
    form_id: str,
    button_id: str,
    visible: bool = None,
    enabled: bool = None,
    current_user: User = Depends(get_current_user)
):
    """
    Update button state (visibility and enabled state).
    
    Args:
        form_id: The ID of the form
        button_id: The ID of the button to update
        visible: Optional visibility state
        enabled: Optional enabled state
        current_user: The current authenticated user
    """
    try:
        # In real implementation, update button state in form definition service
        buttons = get_form_buttons_from_service(form_id)
        buttons_attr = ButtonsAttribute(buttons)
        
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
                
        # Save updated buttons back to service
        save_form_buttons_to_service(form_id, buttons_attr.buttons)
        
        return {"message": "Button state updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Button update failed: {str(e)}")

@router.patch("/buttons/{form_id}/{button_id}/label")
async def update_button_label(
    form_id: str,
    button_id: str,
    label: str,
    current_user: User = Depends(get_current_user)
):
    """
    Update button label.
    
    Args:
        form_id: The ID of the form
        button_id: The ID of the button to update
        label: New label for the button
        current_user: The current authenticated user
    """
    try:
        # In real implementation, update button label in form definition service
        buttons = get_form_buttons_from_service(form_id)
        buttons_attr = ButtonsAttribute(buttons)
        buttons_attr.update_button_label(button_id, label)
        
        # Save updated buttons back to service
        save_form_buttons_to_service(form_id, buttons_attr.buttons)
        
        return {"message": "Button label updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Button update failed: {str(e)}")

# Helper functions (to be implemented based on actual services)
def get_form_buttons_from_service(form_id: str) -> List[ButtonDefinition]:
    """Get button definitions from form service"""
    raise NotImplementedError()

def save_form_buttons_to_service(form_id: str, buttons: List[ButtonDefinition]):
    """Save button definitions to form service"""
    raise NotImplementedError()
