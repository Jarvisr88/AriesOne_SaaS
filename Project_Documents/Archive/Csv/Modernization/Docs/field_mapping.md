# CSV Field Mapping Documentation

This document details the mapping between the legacy C# CSV implementation and the modern Python implementation.

## Class Mappings

### CsvReader (C#) → CsvReader (Python)

| Legacy Property/Method | Modern Equivalent | Notes |
|-----------------------|-------------------|-------|
| BufferSize | config.buffer_size | Configurable via CsvConfig |
| Delimiter | config.delimiter | Configurable via CsvConfig |
| Quote | config.quote_char | Configurable via CsvConfig |
| Escape | config.escape_char | Configurable via CsvConfig |
| Comment | config.comment_char | Configurable via CsvConfig |
| HasHeaders | config.has_headers | Configurable via CsvConfig |
| TrimSpaces | config.trim_spaces | Configurable via CsvConfig |
| DefaultParseErrorAction | config.parse_error_action | Uses enum ParseErrorAction |
| MissingFieldAction | config.missing_field_action | Uses enum MissingFieldAction |
| SupportsMultiline | config.supports_multiline | Configurable via CsvConfig |

### ParseErrorEventArgs (C#) → ParseError (Python)

| Legacy Property | Modern Equivalent | Notes |
|----------------|-------------------|-------|
| Error | error_message | String description of error |
| RawData | raw_data | Raw data that caused error |
| CurrentRecordIndex | line_number | 1-based line number |
| CurrentFieldIndex | field_index | 0-based field index |

### CachedCsvReader (C#) → CsvService (Python)

| Legacy Feature | Modern Equivalent | Notes |
|----------------|-------------------|-------|
| Record Caching | In-memory list | Managed by CsvService |
| MoveTo | Database pagination | Via CsvRepository |
| Binding Support | FastAPI models | Using Pydantic |

## Enum Mappings

### ParseErrorAction

| Legacy Value | Modern Value | Description |
|-------------|--------------|-------------|
| ThrowException | RAISE_EXCEPTION | Raise exception on error |
| AdvanceToNextLine | CONTINUE | Skip field and continue |
| RaiseEvent | SKIP_ROW | Skip entire row |

### MissingFieldAction

| Legacy Value | Modern Value | Description |
|-------------|--------------|-------------|
| ParseError | PARSE_ERROR | Treat as parse error |
| ReplaceByNull | REPLACE_BY_NULL | Replace with None |
| ReplaceByEmpty | REPLACE_BY_EMPTY | Replace with empty string |

## Database Schema

New tables added for tracking CSV imports:

1. csv_imports
   - Tracks import sessions
   - Stores configuration
   - Maintains status and counts

2. csv_import_errors
   - Records parsing errors
   - Links to import sessions
   - Stores error details

## API Endpoints

New REST endpoints that replace legacy functionality:

1. POST /api/csv/parse
   - Replaces direct CsvReader usage
   - Supports all configuration options
   - Returns structured response

2. POST /api/csv/validate
   - New functionality for validation
   - Header checking
   - Field validation

3. POST /api/csv/transform
   - New functionality for transformation
   - Data type conversion
   - Custom transformations

## Additional Features

New features not present in legacy implementation:

1. Async Support
   - Async file processing
   - Non-blocking operations

2. Error Tracking
   - Persistent error storage
   - Error retrieval API

3. Progress Tracking
   - Import session tracking
   - Status updates

4. Data Transformation
   - Type conversion
   - Custom transformations

5. Validation
   - Header validation
   - Data validation
