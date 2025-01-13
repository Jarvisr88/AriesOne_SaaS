# CSV Processing System

## Overview

The CSV Processing System is a robust and flexible solution for handling CSV file imports with validation, transformation, and error handling capabilities. It supports schema-based validation, custom transformation rules, and asynchronous processing with progress tracking.

## Features

### 1. Schema Management

- **JSON-based Schema Definition**
  - Define column names, data types, and validation rules
  - Support for required/optional fields
  - Custom validation rules per column
  - Transformation rules for data cleanup

- **Supported Data Types**
  - string
  - integer
  - float
  - date
  - boolean

- **Validation Rules**
  - Regular expressions
  - Min/max values
  - Allowed values
  - Unique constraints
  - Custom validation functions

### 2. File Processing

- **Upload Handling**
  - Secure file upload
  - File size validation
  - MIME type verification
  - Temporary storage management

- **Schema Detection**
  - Automatic schema detection
  - Confidence scoring
  - Header analysis
  - Data type inference

- **Validation**
  - Column presence verification
  - Data type validation
  - Custom rule validation
  - Detailed error reporting

- **Transformation**
  - Case conversion
  - String trimming
  - Date formatting
  - Value replacement
  - Custom transformations

### 3. Error Handling

- **Validation Errors**
  - Missing required columns
  - Invalid data types
  - Rule violations
  - Row-level error tracking

- **Processing Errors**
  - File read/write errors
  - Encoding issues
  - Memory constraints
  - System errors

### 4. Performance

- **Optimization**
  - Streaming processing for large files
  - Batch processing
  - Memory efficient operations
  - Progress tracking

- **Scalability**
  - Asynchronous processing
  - Background job queuing
  - Resource management
  - Error recovery

## Usage

### 1. Schema Definition

Create a JSON schema file in the `schemas` directory:

```json
{
  "name": "patient_records",
  "columns": [
    {
      "name": "patient_id",
      "data_type": "string",
      "required": true,
      "validation_rules": {
        "regex": "^[A-Z]{2}\\d{6}$",
        "unique": true
      }
    },
    {
      "name": "first_name",
      "data_type": "string",
      "required": true,
      "transformation_rules": {
        "trim": true,
        "uppercase": true
      }
    }
  ]
}
```

### 2. API Endpoints

#### Schema Management
```http
GET /api/v1/csv/schemas
POST /api/v1/csv/detect-schema
```

#### File Processing
```http
POST /api/v1/csv/validate
POST /api/v1/csv/process
GET /api/v1/csv/jobs
GET /api/v1/csv/jobs/{job_id}
```

### 3. Frontend Integration

```typescript
import { CSVUploader } from '@/components/csv/CSVUploader'
import { CSVJobManager } from '@/components/csv/CSVJobManager'

function CSVManagement() {
  return (
    <div>
      <CSVUploader />
      <CSVJobManager />
    </div>
  )
}
```

## Performance Considerations

1. **File Size**
   - Maximum file size: 100MB
   - Recommended rows: < 100,000
   - Memory usage: ~2x file size

2. **Processing Speed**
   - Validation: ~10,000 rows/second
   - Transformation: ~5,000 rows/second
   - Total processing: ~3,000 rows/second

3. **Concurrent Processing**
   - Maximum concurrent jobs: 10
   - Queue timeout: 30 minutes
   - Memory limit per job: 1GB

## Error Handling

1. **Validation Errors**
   ```json
   {
     "type": "validation_error",
     "errors": [
       {
         "type": "missing_columns",
         "columns": ["patient_id", "first_name"]
       },
       {
         "type": "invalid_type",
         "column": "age",
         "expected_type": "integer",
         "rows": [1, 5, 10]
       }
     ]
   }
   ```

2. **Processing Errors**
   ```json
   {
     "type": "processing_error",
     "message": "Failed to process file",
     "details": {
       "error_type": "memory_exceeded",
       "limit": "1GB",
       "current_usage": "1.2GB"
     }
   }
   ```

## Security

1. **File Upload**
   - Allowed extensions: .csv
   - Maximum file size: 100MB
   - Virus scanning
   - Content type verification

2. **Data Protection**
   - Temporary file cleanup
   - Access control
   - Audit logging
   - Data encryption

## Monitoring

1. **Metrics**
   - Processing time
   - Success/failure rate
   - Queue length
   - Resource usage

2. **Alerts**
   - High failure rate
   - Long queue time
   - Resource exhaustion
   - System errors

## Best Practices

1. **File Preparation**
   - Use UTF-8 encoding
   - Include headers
   - Clean data before upload
   - Validate file size

2. **Error Handling**
   - Check validation results
   - Handle partial success
   - Implement retries
   - Log errors

3. **Performance**
   - Process files in batches
   - Monitor resource usage
   - Implement timeouts
   - Clean up temporary files

4. **Security**
   - Validate file content
   - Implement access control
   - Secure temporary storage
   - Audit processing activities
