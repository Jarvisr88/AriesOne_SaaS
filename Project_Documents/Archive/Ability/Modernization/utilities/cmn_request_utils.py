def validate_cmn_request(request):
    # Check if all required fields are present and not None
    required_fields = ['medicare_mainframe', 'search_criteria', 'mock_response']
    for field in required_fields:
        if field not in request.dict() or request.dict()[field] is None:
            return False
    
    # Type validation
    if not isinstance(request.medicare_mainframe, str):
        return False
    if not isinstance(request.mock_response, bool):
        return False
    
    # Example of custom validation logic
    if request.mock_response not in [True, False]:
        return False
    
    return True
