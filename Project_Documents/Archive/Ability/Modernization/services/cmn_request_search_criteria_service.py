from repositories.cmn_request_search_criteria_repository import save_cmn_request_search_criteria
from utilities.cmn_request_search_criteria_utils import validate_cmn_request_search_criteria


def process_cmn_request_search_criteria(criteria):
    # Validate the criteria
    if not validate_cmn_request_search_criteria(criteria):
        raise ValueError("Invalid CmnRequestSearchCriteria data")
    
    # Process the criteria (business logic)
    # Example: Log the criteria processing
    print("Processing CmnRequestSearchCriteria:", criteria)
    
    # Convert criteria to dictionary and add processing details
    processed_criteria = criteria.dict()
    processed_criteria['processed'] = True
    processed_criteria['timestamp'] = "2025-01-07T02:39:11-06:00"  # Add a timestamp
    
    # Save the processed criteria
    saved_criteria = save_cmn_request_search_criteria(processed_criteria)
    
    return saved_criteria
