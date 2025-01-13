# CSV Transformation Rules

This document outlines the transformation rules for converting the legacy C# CSV implementation to the modern Python implementation.

## 1. Core Transformations

### 1.1 Architecture Changes

```plaintext
Legacy (C#)                     Modern (Python)
─────────────────────          ────────────────────
│ CsvReader           │        │ FastAPI           │
│ ├─ Read            │    →   │ ├─ API Routes     │
│ └─ Parse           │        │ └─ Endpoints      │
│                    │        │                   │
│ CachedCsvReader    │        │ Services          │
│ ├─ Cache           │    →   │ ├─ CsvService     │
│ └─ Retrieve        │        │ └─ Processing     │
│                    │        │                   │
│ Event-based Error  │        │ Exception-based   │
└────────────────────┘        └───────────────────┘
```

### 1.2 Technology Stack Changes

```plaintext
Legacy                         Modern
─────────────────             ────────────────
.NET Framework       →        Python 3.9+
System.IO           →        io/aiofiles
System.Data         →        SQLAlchemy
Event Handling      →        Exception Handling
```

## 2. Code Transformation Rules

### 2.1 Class Transformations

1. CsvReader Class:
   ```plaintext
   C#: public class CsvReader : IDataReader
   ↓
   Python: class CsvReader:
   - Remove IDataReader interface
   - Convert properties to Pydantic model
   - Replace events with exceptions
   ```

2. Error Handling:
   ```plaintext
   C#: public event EventHandler<ParseErrorEventArgs>
   ↓
   Python: raise ParseError(
       line_number=line_num,
       field_index=field_idx,
       raw_data=data,
       error_message=str(e)
   )
   ```

3. Buffer Management:
   ```plaintext
   C#: private char[] _buffer
   ↓
   Python: Use Python's built-in buffering
   ```

### 2.2 Method Transformations

1. Reading Methods:
   ```plaintext
   C#: public bool Read()
   ↓
   Python: def read_file(self, file: TextIO)
   ```

2. Field Access:
   ```plaintext
   C#: public string GetString(int i)
   ↓
   Python: Direct dictionary access
   ```

3. Parsing:
   ```plaintext
   C#: private ParseState ParseField()
   ↓
   Python: Use csv.reader/DictReader
   ```

## 3. Data Structure Transformations

### 3.1 Configuration

```plaintext
C# Properties                  Python Pydantic Model
──────────────────            ───────────────────────
public char Delimiter         delimiter: str
public char Quote             quote_char: str
public bool HasHeaders        has_headers: bool
public int BufferSize         buffer_size: int
```

### 3.2 Error Handling

```plaintext
C# Event Args                 Python Exception
──────────────────           ────────────────────
Error                        error_message: str
RawData                      raw_data: str
CurrentRecordIndex           line_number: int
CurrentFieldIndex            field_index: int
```

## 4. Database Schema Transformations

### 4.1 New Tables

1. CSV Imports:
   ```sql
   CREATE TABLE csv_imports (
       id INTEGER PRIMARY KEY,
       filename VARCHAR NOT NULL,
       status VARCHAR NOT NULL,
       config JSONB NOT NULL,
       ...
   )
   ```

2. Import Errors:
   ```sql
   CREATE TABLE csv_import_errors (
       id INTEGER PRIMARY KEY,
       import_id INTEGER REFERENCES csv_imports(id),
       line_number INTEGER NOT NULL,
       ...
   )
   ```

## 5. API Transformations

### 5.1 Endpoint Mapping

```plaintext
Legacy Method                 Modern Endpoint
──────────────────           ────────────────────
Read()                       POST /api/csv/parse
MoveTo()                     GET /api/csv/{id}
GetSchemaTable()             GET /api/csv/schema
```

## 6. Validation Rules

### 6.1 Input Validation

1. File Validation:
   ```python
   - Check file extension
   - Validate encoding
   - Verify file size
   ```

2. Configuration Validation:
   ```python
   - Validate delimiter
   - Check buffer size
   - Verify header settings
   ```

### 6.2 Data Validation

1. Field Validation:
   ```python
   - Check required fields
   - Validate data types
   - Verify field lengths
   ```

2. Row Validation:
   ```python
   - Check row completeness
   - Validate row structure
   - Verify row count
   ```

## 7. Performance Considerations

### 7.1 Memory Management

1. Streaming:
   ```python
   - Use generators for large files
   - Implement chunked processing
   - Utilize async streaming
   ```

2. Caching:
   ```python
   - Implement repository pattern
   - Use database for persistence
   - Cache frequently accessed data
   ```

### 7.2 Optimization

1. Processing:
   ```python
   - Use built-in csv module
   - Implement async processing
   - Optimize buffer sizes
   ```

2. Database:
   ```python
   - Index key columns
   - Implement batch processing
   - Use efficient queries
   ```
