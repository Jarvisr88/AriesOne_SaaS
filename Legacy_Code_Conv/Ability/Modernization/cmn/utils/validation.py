"""
Validation Module

This module provides validation utilities for CMN operations.
"""
from typing import Optional

from pydantic import ValidationError

from ..models.cmn_models import CmnRequest, CmnSearchCriteria

def validate_request(request: CmnRequest) -> None:
    """
    Validate a CMN request.
    
    Args:
        request: The request to validate
    
    Raises:
        ValueError: If validation fails
    """
    try:
        # Validate search criteria
        validate_search_criteria(request.search_criteria)

        # Validate mainframe config
        if not request.medicare_mainframe.carrier_id:
            raise ValueError("Carrier ID is required")
        if not request.medicare_mainframe.facility_id:
            raise ValueError("Facility ID is required")
        if not request.medicare_mainframe.user_id:
            raise ValueError("User ID is required")
        if not request.medicare_mainframe.password:
            raise ValueError("Password is required")

    except ValidationError as e:
        raise ValueError(f"Request validation failed: {str(e)}")

def validate_search_criteria(criteria: CmnSearchCriteria) -> None:
    """
    Validate search criteria.
    
    Args:
        criteria: The criteria to validate
    
    Raises:
        ValueError: If validation fails
    """
    # Check if at least one search field is provided
    if not any([
        criteria.npi,
        criteria.hic,
        criteria.mbi,
        criteria.hcpcs
    ]):
        raise ValueError("At least one search criterion must be provided")

    # Validate NPI format if provided
    if criteria.npi and not _is_valid_npi(criteria.npi):
        raise ValueError("Invalid NPI format")

    # Validate MBI format if provided
    if criteria.mbi and not _is_valid_mbi(criteria.mbi):
        raise ValueError("Invalid MBI format")

    # Validate HCPCS format if provided
    if criteria.hcpcs and not _is_valid_hcpcs(criteria.hcpcs):
        raise ValueError("Invalid HCPCS format")

    # Validate max results
    if criteria.max_results and (
        criteria.max_results < 1 or
        criteria.max_results > 1000
    ):
        raise ValueError("Max results must be between 1 and 1000")

def _is_valid_npi(npi: str) -> bool:
    """
    Validate NPI format.
    
    Args:
        npi: NPI to validate
    
    Returns:
        bool indicating if NPI is valid
    """
    if not npi or len(npi) != 10:
        return False
    
    try:
        int(npi)  # Must be numeric
        return True
    except ValueError:
        return False

def _is_valid_mbi(mbi: str) -> bool:
    """
    Validate MBI format.
    
    Args:
        mbi: MBI to validate
    
    Returns:
        bool indicating if MBI is valid
    """
    if not mbi or len(mbi) != 11:
        return False
    
    # MBI format: C A AN N A AN N A A N
    # C: Numeric 1-9
    # A: Alpha A-Z (excluding S, L, O, I, B, Z)
    # N: Numeric 0-9
    # AN: Alpha A-Z (excluding S, L, O, I, B, Z) or numeric 0-9
    
    # TODO: Implement detailed MBI format validation
    return True

def _is_valid_hcpcs(hcpcs: str) -> bool:
    """
    Validate HCPCS format.
    
    Args:
        hcpcs: HCPCS code to validate
    
    Returns:
        bool indicating if HCPCS is valid
    """
    if not hcpcs:
        return False
    
    # Level I (CPT) codes: 5 numeric digits
    # Level II codes: 1 alpha character + 4 numeric digits
    return (
        (len(hcpcs) == 5 and hcpcs.isdigit()) or
        (len(hcpcs) == 5 and hcpcs[0].isalpha() and hcpcs[1:].isdigit())
    )
