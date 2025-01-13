# CSV Processing Module

This module provides modern CSV processing capabilities for the AriesOne SaaS platform. It is a modernized version of the legacy DMEWorks.Csv implementation, rewritten in Python using FastAPI.

## Features

- Configurable CSV parsing with support for:
  - Custom delimiters
  - Quote and escape characters
  - Comment handling
  - Header management
  - Space trimming
  - Multiline fields
- Error handling with multiple strategies:
  - Raise exceptions
  - Continue processing
  - Skip problematic rows
- Missing field handling:
  - Treat as parse error
  - Replace with null
  - Replace with empty string
- File encoding detection
- Data transformation capabilities
- Header validation
- REST API endpoints for CSV operations
- Type safety with Pydantic models
- Async/await support
- Streaming large files

## Components

1. `models.py`: Data models and configurations
2. `reader.py`: Core CSV reading implementation
3. `service.py`: Business logic and file handling
4. `api.py`: REST API endpoints

## API Endpoints

### POST /api/csv/parse
Parse a CSV file with optional configuration.

```python
response = await client.post(
    "/api/csv/parse",
    files={"file": csv_file},
    json={"config": CsvConfig(delimiter=",", has_headers=True)}
)
```

### POST /api/csv/validate
Validate CSV headers against required fields.

```python
response = await client.post(
    "/api/csv/validate",
    files={"file": csv_file},
    json={"required_fields": ["name", "email"]}
)
```

### POST /api/csv/transform
Parse and transform CSV data.

```python
response = await client.post(
    "/api/csv/transform",
    files={"file": csv_file},
    json={"transformations": {"age": "int", "active": "bool"}}
)
```

## Usage Example

```python
from csv import CsvConfig, CsvService

# Create service instance
service = CsvService()

# Configure CSV parsing
config = CsvConfig(
    delimiter=",",
    has_headers=True,
    trim_spaces=True
)

# Process file
async with aiofiles.open("data.csv", "rb") as f:
    result = await service.process_file(f, config)

# Access results
print(f"Total records: {result.total_records}")
print(f"Headers: {result.headers}")
print(f"First record: {result.records[0]}")
```

## Error Handling

The module provides detailed error information through the `ParseError` model:

```python
for error in result.errors:
    print(f"Error on line {error.line_number}: {error.error_message}")
```

## Data Transformation

Transform data during parsing:

```python
transformations = {
    "age": int,
    "salary": float,
    "active": lambda x: x.lower() == "true"
}

transformed_data = service.transform_data(result.records, transformations)
```

## Integration

To integrate this module into your FastAPI application:

```python
from fastapi import FastAPI
from csv import csv_router

app = FastAPI()
app.include_router(csv_router)
```
