"""
AbilityCredentials Mapping Module
This module provides mapping logic between C# and Python implementations.
"""
from typing import Dict, Any
from ..models.ability_credentials_model import AbilityCredentials

def map_cs_to_python(cs_data: Dict[str, Any]) -> AbilityCredentials:
    """
    Map C# credential data to Python model.
    
    Args:
        cs_data (Dict[str, Any]): C# credential data
        
    Returns:
        AbilityCredentials: Python credential model
        
    Raises:
        ValueError: If mapping fails
    """
    try:
        return AbilityCredentials(
            sender_id=cs_data.get("SenderId") or cs_data.get("sender-id"),
            username=cs_data.get("Username") or cs_data.get("username"),
            password=cs_data.get("Password") or cs_data.get("password")
        )
    except Exception as e:
        raise ValueError(f"Failed to map C# credentials: {e}")

def map_python_to_cs(credentials: AbilityCredentials) -> Dict[str, Any]:
    """
    Map Python credential model to C# format.
    
    Args:
        credentials (AbilityCredentials): Python credential model
        
    Returns:
        Dict[str, Any]: C# credential data
    """
    return {
        "SenderId": credentials.sender_id,
        "Username": credentials.username,
        "Password": credentials.password.get_secret_value()
    }

def map_xml_to_python(xml_str: str) -> AbilityCredentials:
    """
    Map XML credential data to Python model.
    
    Args:
        xml_str (str): XML credential data
        
    Returns:
        AbilityCredentials: Python credential model
        
    Raises:
        ValueError: If mapping fails
    """
    return AbilityCredentials.from_xml(xml_str)

def map_python_to_xml(credentials: AbilityCredentials) -> str:
    """
    Map Python credential model to XML format.
    
    Args:
        credentials (AbilityCredentials): Python credential model
        
    Returns:
        str: XML credential data
    """
    return credentials.to_xml()

# Field mappings for reference
FIELD_MAPPINGS = {
    "C# to Python": {
        "SenderId": "sender_id",
        "Username": "username",
        "Password": "password"
    },
    "XML to Python": {
        "sender-id": "sender_id",
        "username": "username",
        "password": "password"
    }
}
