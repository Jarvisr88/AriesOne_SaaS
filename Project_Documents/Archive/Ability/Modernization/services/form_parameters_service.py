"""
Form Parameters Service Module

This module provides services for form parameters.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar
from ..models.form_parameters import (
    FormParameters,
    Parameter,
    ParameterType,
    FormParameterized
)
from .base_service import BaseService
from fastapi import HTTPException
import uuid
from datetime import datetime

T = TypeVar('T')

class FormParametersService(BaseService, Generic[T]):
    """Service for handling form parameters"""
    
    def __init__(self):
        """Initialize form parameters service"""
        self._parameters: Dict[str, FormParameters] = {}
        self._parameterized_objects: Dict[str, FormParameterized[T]] = {}
    
    async def create_parameters(
        self,
        query: Optional[str] = None
    ) -> str:
        """
        Create form parameters.
        
        Args:
            query: Optional query string to initialize parameters
            
        Returns:
            Parameters ID
        """
        parameters_id = str(uuid.uuid4())
        
        # Create parameters from query string if provided
        if query:
            self._parameters[parameters_id] = FormParameters.from_query_string(query)
        else:
            self._parameters[parameters_id] = FormParameters()
        
        return parameters_id
    
    async def get_parameters(
        self,
        parameters_id: str
    ) -> FormParameters:
        """
        Get form parameters.
        
        Args:
            parameters_id: ID of the parameters
            
        Returns:
            Form parameters
            
        Raises:
            HTTPException: If parameters are not found
        """
        parameters = self._parameters.get(parameters_id)
        if not parameters:
            raise HTTPException(
                status_code=404,
                detail=f"Parameters not found: {parameters_id}"
            )
        return parameters
    
    async def set_parameter(
        self,
        parameters_id: str,
        key: str,
        value: Any,
        parameter_type: Optional[ParameterType] = None
    ):
        """
        Set parameter value.
        
        Args:
            parameters_id: ID of the parameters
            key: Parameter key
            value: Parameter value
            parameter_type: Parameter type
            
        Raises:
            HTTPException: If parameters are not found or are readonly
        """
        parameters = await self.get_parameters(parameters_id)
        try:
            parameters.set(key, value, parameter_type)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    
    async def get_parameter(
        self,
        parameters_id: str,
        key: str,
        default: Any = None,
        parameter_type: Optional[ParameterType] = None
    ) -> Any:
        """
        Get parameter value.
        
        Args:
            parameters_id: ID of the parameters
            key: Parameter key
            default: Default value if parameter not found
            parameter_type: Expected parameter type
            
        Returns:
            Parameter value
            
        Raises:
            HTTPException: If parameters are not found or parameter type doesn't match
        """
        parameters = await self.get_parameters(parameters_id)
        try:
            return parameters.get(key, default, parameter_type)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    
    async def clear_parameters(
        self,
        parameters_id: str
    ):
        """
        Clear all parameters.
        
        Args:
            parameters_id: ID of the parameters
            
        Raises:
            HTTPException: If parameters are not found or are readonly
        """
        parameters = await self.get_parameters(parameters_id)
        try:
            parameters.clear()
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    
    async def set_readonly(
        self,
        parameters_id: str
    ):
        """
        Make parameters readonly.
        
        Args:
            parameters_id: ID of the parameters
            
        Raises:
            HTTPException: If parameters are not found
        """
        parameters = await self.get_parameters(parameters_id)
        parameters.set_readonly()
    
    async def create_parameterized_object(
        self,
        parameters: Optional[FormParameters] = None
    ) -> str:
        """
        Create a parameterized object.
        
        Args:
            parameters: Optional form parameters
            
        Returns:
            Object ID
        """
        object_id = str(uuid.uuid4())
        self._parameterized_objects[object_id] = FormParameterized[T](
            parameters=parameters or FormParameters()
        )
        return object_id
    
    async def get_parameterized_object(
        self,
        object_id: str
    ) -> FormParameterized[T]:
        """
        Get parameterized object.
        
        Args:
            object_id: ID of the object
            
        Returns:
            Parameterized object
            
        Raises:
            HTTPException: If object is not found
        """
        obj = self._parameterized_objects.get(object_id)
        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"Parameterized object not found: {object_id}"
            )
        return obj
    
    async def set_object_parameters(
        self,
        object_id: str,
        parameters: FormParameters
    ):
        """
        Set parameters for a parameterized object.
        
        Args:
            object_id: ID of the object
            parameters: Form parameters
            
        Raises:
            HTTPException: If object is not found
        """
        obj = await self.get_parameterized_object(object_id)
        obj.set_parameters(parameters)
