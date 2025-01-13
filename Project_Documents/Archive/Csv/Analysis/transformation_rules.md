# CSV Module Transformation Rules

## 1. Enums Transformation

### MissingFieldAction
Legacy:
```csharp
public enum MissingFieldAction
{
    TreatAsParseError,
    ReturnEmptyValue,
    ReturnNullValue,
    ReturnPartiallyParsedValue
}
```

Modern Python:
```python
class MissingFieldAction(str, Enum):
    TREAT_AS_ERROR = "treat_as_error"
    RETURN_EMPTY = "return_empty"
    RETURN_NULL = "return_null"
    RETURN_PARTIAL = "return_partial"
```

### ParseErrorAction
Legacy:
```csharp
public enum ParseErrorAction
{
    RaiseEvent,
    AdvanceToNextLine,
    ThrowException
}
```

Modern Python:
```python
class ParseErrorAction(str, Enum):
    RAISE_EVENT = "raise_event"
    ADVANCE_LINE = "advance_line"
    THROW_EXCEPTION = "throw_exception"
```

## 2. Exception Classes Transformation

### MalformedCsvException
Legacy:
```csharp
[Serializable]
public class MalformedCsvException : Exception
{
    private string _message;
    private string _rawData;
    private int _currentFieldIndex;
    private long _currentRecordIndex;
    private int _currentPosition;
}
```

Modern Python:
```python
class MalformedCsvException(Exception):
    def __init__(
        self,
        message: str = "",
        raw_data: str = "",
        current_position: int = -1,
        current_record_index: int = -1,
        current_field_index: int = -1,
        inner_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.raw_data = raw_data
        self.current_position = current_position
        self.current_record_index = current_record_index
        self.current_field_index = current_field_index
        self.inner_exception = inner_exception
```

### MissingFieldCsvException
Legacy:
```csharp
[Serializable]
public class MissingFieldCsvException : MalformedCsvException
{
    // Inherits all functionality from MalformedCsvException
}
```

Modern Python:
```python
class MissingFieldCsvException(MalformedCsvException):
    """Exception raised when a CSV field is missing."""
    pass
```

## 3. Event Arguments Transformation

### ParseErrorEventArgs
Legacy:
```csharp
public class ParseErrorEventArgs : EventArgs
{
    private MalformedCsvException _error;
    private ParseErrorAction _action;
}
```

Modern Python:
```python
@dataclass
class ParseErrorEvent:
    error: MalformedCsvException
    action: ParseErrorAction
    
    def __post_init__(self):
        self._original_action = self.action
```

## 4. Resource Management Transformation

### ExceptionMessage
Legacy:
```csharp
internal class ExceptionMessage
{
    private static ResourceManager resourceMan;
    private static CultureInfo resourceCulture;
    // Resource string getters
}
```

Modern Python:
```python
class ErrorMessages:
    BUFFER_SIZE_TOO_SMALL = "Buffer size is too small"
    CANNOT_MOVE_PREVIOUS = "Cannot move to previous record in forward-only mode"
    CANNOT_READ_RECORD = "Cannot read record at specified index"
    ENUMERATION_FINISHED = "Enumeration finished or not started"
    FIELD_HEADER_NOT_FOUND = "Field header not found"
    FIELD_INDEX_OUT_OF_RANGE = "Field index out of range"
    MALFORMED_CSV = "Malformed CSV data"
    MISSING_FIELD = "Missing required field"
    NO_CURRENT_RECORD = "No current record"
    NO_HEADERS = "No headers found"
    NOT_ENOUGH_SPACE = "Not enough space in array"
    PARSE_ERROR = "Parse error occurred"
    READER_CLOSED = "Reader is closed"
    RECORD_INDEX_NEGATIVE = "Record index cannot be negative"
```

## 5. Configuration Transformation

### CSV Configuration
Legacy (from CsvReader properties):
```csharp
public class CsvReader
{
    private int _bufferSize;
    private char _comment;
    private char _escape;
    private char _delimiter;
    private char _quote;
    private bool _hasHeaders;
    private bool _trimSpaces;
}
```

Modern Python:
```python
@dataclass
class CsvConfig:
    delimiter: str = ","
    quote_char: str = '"'
    escape_char: str = "\\"
    comment_char: str = "#"
    has_headers: bool = True
    trim_spaces: bool = True
    buffer_size: int = 8192
    encoding: str = "utf-8"
    missing_field_action: MissingFieldAction = MissingFieldAction.TREAT_AS_ERROR
    parse_error_action: ParseErrorAction = ParseErrorAction.RAISE_EVENT
```

## 6. Event Handling Transformation

### Legacy Event Pattern
```csharp
public event EventHandler<ParseErrorEventArgs> ParseError;
```

### Modern Python Approach
```python
from typing import Callable, List

class CsvEventHandler:
    def __init__(self):
        self._parse_error_handlers: List[Callable[[ParseErrorEvent], None]] = []

    def add_parse_error_handler(
        self,
        handler: Callable[[ParseErrorEvent], None]
    ):
        self._parse_error_handlers.append(handler)

    def remove_parse_error_handler(
        self,
        handler: Callable[[ParseErrorEvent], None]
    ):
        self._parse_error_handlers.remove(handler)

    async def handle_parse_error(self, event: ParseErrorEvent):
        for handler in self._parse_error_handlers:
            await handler(event)
```

## 7. Data Access Pattern Transformation

### Legacy Pattern
```csharp
public interface IDataReader
{
    bool Read();
    string GetString(int i);
    int GetInt32(int i);
    // Other data type getters
}
```

### Modern Python Pattern
```python
class CsvDataAccess:
    async def read_row(self) -> Optional[Dict[str, Any]]:
        """Read next row as dictionary."""
        pass

    async def read_rows(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield rows as dictionaries."""
        pass

    def get_value(
        self,
        row: Dict[str, Any],
        field: str,
        type_converter: Callable = str
    ) -> Any:
        """Get typed value from row."""
        pass
```

## 8. Error Handling Transformation

### Legacy Pattern
```csharp
try
{
    // CSV operations
}
catch (MalformedCsvException ex)
{
    // Handle malformed CSV
}
catch (MissingFieldCsvException ex)
{
    // Handle missing field
}
```

### Modern Python Pattern
```python
try:
    # CSV operations
except MalformedCsvException as e:
    logger.error(f"Malformed CSV: {e}")
    raise
except MissingFieldCsvException as e:
    logger.error(f"Missing field: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

## 9. Implementation Notes

1. **Async Support**
   - All blocking operations should be async
   - Use async file I/O with aiofiles
   - Implement async generators for streaming

2. **Type Safety**
   - Use Python type hints throughout
   - Implement Pydantic models for validation
   - Use dataclasses for data structures

3. **Error Handling**
   - Implement custom exception hierarchy
   - Use structured logging
   - Provide detailed error context

4. **Configuration**
   - Use Pydantic settings management
   - Support environment variables
   - Enable runtime configuration

5. **Testing**
   - Unit tests for each component
   - Integration tests for workflows
   - Performance benchmarks
