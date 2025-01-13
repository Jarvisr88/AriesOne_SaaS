"""SODA validation utilities module."""

import re
from typing import Optional

def validate_resource_id(resource_id: str) -> None:
    """Validate SODA resource ID (4x4)."""
    if not resource_id:
        raise ValueError("Resource ID is required")
    
    pattern = r'^[a-z0-9]{4}-[a-z0-9]{4}$'
    if not re.match(pattern, resource_id):
        raise ValueError(
            "Resource ID must be a valid Socrata (4x4) identifier"
        )
