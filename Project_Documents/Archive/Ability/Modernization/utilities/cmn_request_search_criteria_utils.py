def validate_cmn_request_search_criteria(criteria):
    # Check if all required fields are present and not None
    required_fields = ['npi', 'hic', 'hcpcs', 'mbi', 'max_results']
    for field in required_fields:
        if field not in criteria.dict() or criteria.dict()[field] is None:
            return False
    
    # Type validation
    if not isinstance(criteria.npi, str):
        return False
    if not isinstance(criteria.hic, str):
        return False
    if not isinstance(criteria.hcpcs, str):
        return False
    if not isinstance(criteria.mbi, str):
        return False
    if not isinstance(criteria.max_results, int):
        return False
    
    # Example of custom validation logic
    if criteria.max_results < 0:
        return False
    
    return True
