# CmnRequestSearchCriteria Transformation Rules

## Transformation Logic
- Ensure all fields are correctly mapped from C# to Python.
- Validate data types and structures.
- Apply specific business rules for transformation.

## Code Example
```python
def transform_cmn_request_search_criteria(data):
    # Transform the data according to business rules
    transformed_data = data.copy()
    
    # Example transformation: convert all strings to uppercase
    for key, value in transformed_data.items():
        if isinstance(value, str):
            transformed_data[key] = value.upper()
    
    # Business-specific transformation example
    if 'max_results' in transformed_data:
        transformed_data['max_results'] = min(transformed_data['max_results'], 100)  # Limit max_results to 100
    
    return transformed_data
