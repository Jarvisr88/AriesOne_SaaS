from repositories.cmn_request_repository import save_cmn_request
from utilities.cmn_request_utils import validate_cmn_request


def process_cmn_request(request):
    # Validate the request
    if not validate_cmn_request(request):
        raise ValueError("Invalid CmnRequest data")
    
    # Process the request (business logic)
    # Example: Log the request processing
    print("Processing CmnRequest:", request)
    
    # Convert request to dictionary and add processing details
    processed_data = request.dict()
    processed_data['processed'] = True
    processed_data['timestamp'] = "2025-01-07T02:34:01-06:00"  # Add a timestamp
    
    # Save the processed request
    saved_request = save_cmn_request(processed_data)
    
    return saved_request
