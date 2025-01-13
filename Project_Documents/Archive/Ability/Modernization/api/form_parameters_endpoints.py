"""
Form Parameters API Endpoints Module

This module provides FastAPI endpoints for form parameters.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from ..models.form_parameters import (
    FormParameters,
    Parameter,
    ParameterType,
    FormParameterized
)
from ..services.form_parameters_service import FormParametersService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/form-parameters", response_model=str)
async def create_form_parameters(
    query: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Create form parameters.
    
    Args:
        query: Optional query string to initialize parameters
        current_user: The current authenticated user
        
    Returns:
        Parameters ID
    """
    service = FormParametersService()
    return await service.create_parameters(query)

@router.get("/form-parameters/{parameters_id}", response_model=FormParameters)
async def get_form_parameters(
    parameters_id: str,
    current_user: User = Depends(get_current_user)
) -> FormParameters:
    """
    Get form parameters.
    
    Args:
        parameters_id: ID of the parameters
        current_user: The current authenticated user
        
    Returns:
        Form parameters
    """
    service = FormParametersService()
    return await service.get_parameters(parameters_id)

@router.put("/form-parameters/{parameters_id}/parameter")
async def set_parameter(
    parameters_id: str,
    key: str,
    value: Any,
    parameter_type: Optional[ParameterType] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Set parameter value.
    
    Args:
        parameters_id: ID of the parameters
        key: Parameter key
        value: Parameter value
        parameter_type: Parameter type
        current_user: The current authenticated user
    """
    service = FormParametersService()
    await service.set_parameter(parameters_id, key, value, parameter_type)

@router.get("/form-parameters/{parameters_id}/parameter/{key}")
async def get_parameter(
    parameters_id: str,
    key: str,
    default: Any = None,
    parameter_type: Optional[ParameterType] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get parameter value.
    
    Args:
        parameters_id: ID of the parameters
        key: Parameter key
        default: Default value if parameter not found
        parameter_type: Expected parameter type
        current_user: The current authenticated user
        
    Returns:
        Parameter value
    """
    service = FormParametersService()
    return await service.get_parameter(parameters_id, key, default, parameter_type)

@router.post("/form-parameters/{parameters_id}/clear")
async def clear_parameters(
    parameters_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Clear all parameters.
    
    Args:
        parameters_id: ID of the parameters
        current_user: The current authenticated user
    """
    service = FormParametersService()
    await service.clear_parameters(parameters_id)

@router.post("/form-parameters/{parameters_id}/readonly")
async def set_readonly(
    parameters_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Make parameters readonly.
    
    Args:
        parameters_id: ID of the parameters
        current_user: The current authenticated user
    """
    service = FormParametersService()
    await service.set_readonly(parameters_id)

@router.post("/parameterized-objects", response_model=str)
async def create_parameterized_object(
    parameters: Optional[FormParameters] = None,
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Create a parameterized object.
    
    Args:
        parameters: Optional form parameters
        current_user: The current authenticated user
        
    Returns:
        Object ID
    """
    service = FormParametersService()
    return await service.create_parameterized_object(parameters)

@router.get("/parameterized-objects/{object_id}", response_model=FormParameterized)
async def get_parameterized_object(
    object_id: str,
    current_user: User = Depends(get_current_user)
) -> FormParameterized:
    """
    Get parameterized object.
    
    Args:
        object_id: ID of the object
        current_user: The current authenticated user
        
    Returns:
        Parameterized object
    """
    service = FormParametersService()
    return await service.get_parameterized_object(object_id)

@router.put("/parameterized-objects/{object_id}/parameters")
async def set_object_parameters(
    object_id: str,
    parameters: FormParameters,
    current_user: User = Depends(get_current_user)
):
    """
    Set parameters for a parameterized object.
    
    Args:
        object_id: ID of the object
        parameters: Form parameters
        current_user: The current authenticated user
    """
    service = FormParametersService()
    await service.set_object_parameters(object_id, parameters)
