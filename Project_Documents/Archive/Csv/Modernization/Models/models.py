from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ParseErrorAction(str, Enum):
    """Action to take when a parsing error occurs."""
    RAISE_EXCEPTION = "raise_exception"
    CONTINUE = "continue"
    SKIP_ROW = "skip_row"


class MissingFieldAction(str, Enum):
    """Action to take when a field is missing."""
    PARSE_ERROR = "parse_error"
    REPLACE_BY_NULL = "replace_by_null"
    REPLACE_BY_EMPTY = "replace_by_empty"


class CsvConfig(BaseModel):
    """Configuration for CSV parsing."""
    delimiter: str = Field(default=",", description="CSV delimiter character")
    quote_char: str = Field(default='"', description="Quote character")
    escape_char: str = Field(default='"', description="Escape character")
    comment_char: str = Field(default="#", description="Comment character")
    has_headers: bool = Field(default=True, description="Whether CSV has headers")
    trim_spaces: bool = Field(default=True, description="Whether to trim spaces")
    buffer_size: int = Field(default=4096, description="Read buffer size")
    parse_error_action: ParseErrorAction = Field(
        default=ParseErrorAction.RAISE_EXCEPTION,
        description="Action on parse errors"
    )
    missing_field_action: MissingFieldAction = Field(
        default=MissingFieldAction.PARSE_ERROR,
        description="Action on missing fields"
    )
    supports_multiline: bool = Field(
        default=True,
        description="Whether to support multiline fields"
    )


class ParseError(BaseModel):
    """Information about a parsing error."""
    line_number: int = Field(..., description="Line number where error occurred")
    field_index: int = Field(..., description="Index of problematic field")
    raw_data: str = Field(..., description="Raw data that caused the error")
    error_message: str = Field(..., description="Error description")


class CsvParseResult(BaseModel):
    """Result of CSV parsing operation."""
    headers: Optional[List[str]] = Field(None, description="CSV headers if present")
    records: List[Dict[str, Any]] = Field(..., description="Parsed records")
    errors: List[ParseError] = Field(default_factory=list, description="Parse errors")
    total_records: int = Field(..., description="Total number of records processed")
    skipped_records: int = Field(default=0, description="Number of skipped records")
