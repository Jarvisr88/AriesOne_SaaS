"""
AriesOne CSV Reader Module

A high-performance CSV reader with caching capabilities and robust error handling.
"""
from typing import Optional, List, Dict, Any, Generator, Union
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import asyncio
import logging
from enum import Enum
from datetime import datetime

from csv_validator import CSVValidator, ValidationError
from csv_profiler import CSVProfiler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParseErrorAction(Enum):
    """Defines actions to take when a parse error occurs."""
    RAISE_EXCEPTION = "raise_exception"
    SKIP_ROW = "skip_row"
    REPLACE_WITH_NULL = "replace_with_null"

class MissingFieldAction(Enum):
    """Defines actions to take when a field is missing."""
    RAISE_EXCEPTION = "raise_exception"
    PARSE_AS_NULL = "parse_as_null"
    SKIP_ROW = "skip_row"

@dataclass
class ParseErrorEventArgs:
    """Event arguments for parse errors."""
    row_number: int
    field_index: int
    raw_data: str
    error_message: str
    timestamp: datetime = datetime.now()

class CSVException(Exception):
    """Base exception for CSV operations."""
    pass

class MalformedCSVException(CSVException):
    """Exception raised when CSV data is malformed."""
    def __init__(self, message: str, row_number: int, raw_data: str):
        self.row_number = row_number
        self.raw_data = raw_data
        super().__init__(f"Row {row_number}: {message}")

class MissingFieldCSVException(CSVException):
    """Exception raised when required fields are missing."""
    def __init__(self, field_name: str, row_number: int):
        self.field_name = field_name
        self.row_number = row_number
        super().__init__(f"Missing field '{field_name}' at row {row_number}")

class CSVReader:
    """Base CSV reader implementation with streaming support."""
    
    def __init__(
        self,
        parse_error_action: ParseErrorAction = ParseErrorAction.RAISE_EXCEPTION,
        missing_field_action: MissingFieldAction = MissingFieldAction.RAISE_EXCEPTION,
        chunk_size: int = 10000,
        encoding: str = 'utf-8',
        validator: Optional[CSVValidator] = None,
        profiler: Optional[CSVProfiler] = None
    ):
        """Initialize CSV reader with configuration options.
        
        Args:
            parse_error_action: Action to take on parse errors
            missing_field_action: Action to take on missing fields
            chunk_size: Number of rows to process at once
            encoding: File encoding to use
            validator: Optional CSV validator
            profiler: Optional performance profiler
        """
        self.parse_error_action = parse_error_action
        self.missing_field_action = missing_field_action
        self.chunk_size = chunk_size
        self.encoding = encoding
        self.validator = validator
        self.profiler = profiler
        self._error_handlers = []
        
    def add_error_handler(self, handler: callable):
        """Add an error event handler.
        
        Args:
            handler: Callback function for error events
        """
        self._error_handlers.append(handler)
        
    def _handle_error(self, args: ParseErrorEventArgs):
        """Process error through registered handlers.
        
        Args:
            args: Error event arguments
        """
        for handler in self._error_handlers:
            handler(args)
            
    def read_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """Read entire CSV file into DataFrame.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame containing CSV data
            
        Raises:
            MalformedCSVException: If CSV is malformed
            MissingFieldCSVException: If required fields are missing
        """
        if self.profiler:
            self.profiler.start_operation('read_file')
            
        try:
            df = pd.read_csv(
                file_path,
                encoding=self.encoding,
                on_bad_lines=self._handle_bad_line
            )
            
            if self.validator:
                errors = []
                for index, row in df.iterrows():
                    row_errors = self.validator.validate_row(row.to_dict(), index)
                    errors.extend(row_errors)
                    
                if errors:
                    for error in errors:
                        logger.error(f"Validation error: {error}")
                        if self.profiler:
                            self.profiler.record_error()
                            
            if self.profiler:
                self.profiler.record_rows(len(df))
                
            return df
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            if self.profiler:
                self.profiler.record_error()
            raise MalformedCSVException(str(e), 0, "")
            
        finally:
            if self.profiler:
                self.profiler.end_operation()
            
    def read_stream(
        self,
        file_path: Union[str, Path]
    ) -> Generator[pd.DataFrame, None, None]:
        """Stream CSV file in chunks.
        
        Args:
            file_path: Path to CSV file
            
        Yields:
            DataFrame chunks of CSV data
        """
        if self.profiler:
            self.profiler.start_operation('read_stream')
            
        try:
            for chunk in pd.read_csv(
                file_path,
                encoding=self.encoding,
                chunksize=self.chunk_size,
                on_bad_lines=self._handle_bad_line
            ):
                if self.validator:
                    errors = []
                    for index, row in chunk.iterrows():
                        row_errors = self.validator.validate_row(row.to_dict(), index)
                        errors.extend(row_errors)
                        
                    if errors:
                        for error in errors:
                            logger.error(f"Validation error: {error}")
                            if self.profiler:
                                self.profiler.record_error()
                                
                if self.profiler:
                    self.profiler.record_rows(len(chunk))
                    
                yield chunk
                
        except Exception as e:
            logger.error(f"Error streaming CSV file: {e}")
            if self.profiler:
                self.profiler.record_error()
            raise MalformedCSVException(str(e), 0, "")
            
        finally:
            if self.profiler:
                self.profiler.end_operation()
                
    async def read_file_async(
        self,
        file_path: Union[str, Path]
    ) -> pd.DataFrame:
        """Asynchronously read CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame containing CSV data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.read_file, file_path)
        
    def _handle_bad_line(
        self,
        bad_line: List[str],
        line_num: int
    ) -> Optional[List[str]]:
        """Handle malformed CSV lines based on configuration.
        
        Args:
            bad_line: The problematic line
            line_num: Line number in file
            
        Returns:
            Processed line or None to skip
        """
        error_args = ParseErrorEventArgs(
            row_number=line_num,
            field_index=-1,
            raw_data=str(bad_line),
            error_message="Malformed CSV line"
        )
        self._handle_error(error_args)
        
        if self.parse_error_action == ParseErrorAction.RAISE_EXCEPTION:
            raise MalformedCSVException(
                "Malformed CSV line",
                line_num,
                str(bad_line)
            )
        elif self.parse_error_action == ParseErrorAction.SKIP_ROW:
            return None
        else:  # REPLACE_WITH_NULL
            return [None] * len(bad_line)
