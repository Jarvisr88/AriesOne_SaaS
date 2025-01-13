from typing import List, Dict, Any, Optional, Generator, TextIO
import csv
import io
from contextlib import contextmanager
from .models import (
    CsvConfig,
    ParseError,
    CsvParseResult,
    ParseErrorAction,
    MissingFieldAction,
)


class CsvReader:
    """Modern CSV reader implementation."""

    def __init__(self, config: CsvConfig):
        """Initialize CSV reader with configuration."""
        self.config = config
        self._dialect = type(
            "CustomDialect",
            (csv.Dialect,),
            {
                "delimiter": config.delimiter,
                "quotechar": config.quote_char,
                "escapechar": config.escape_char,
                "doublequote": config.escape_char == config.quote_char,
                "skipinitialspace": config.trim_spaces,
                "lineterminator": "\r\n",
                "quoting": csv.QUOTE_MINIMAL,
            },
        )

    @contextmanager
    def _get_reader(self, file: TextIO) -> Generator[csv.DictReader, None, None]:
        """Create a CSV reader context."""
        reader = csv.DictReader(
            file,
            dialect=self._dialect,
            restkey="_extra_fields",
            restval=None,
        ) if self.config.has_headers else csv.reader(file, dialect=self._dialect)
        try:
            yield reader
        finally:
            pass

    def read_file(self, file: TextIO) -> CsvParseResult:
        """Read and parse a CSV file."""
        records: List[Dict[str, Any]] = []
        errors: List[ParseError] = []
        total_records = 0
        skipped_records = 0
        headers = None

        with self._get_reader(file) as reader:
            if self.config.has_headers and isinstance(reader, csv.DictReader):
                headers = reader.fieldnames

            for line_num, row in enumerate(reader, start=1):
                try:
                    if isinstance(row, dict):
                        record = self._process_dict_row(row, line_num)
                    else:
                        record = self._process_list_row(row, headers, line_num)

                    if record is not None:
                        records.append(record)
                        total_records += 1
                    else:
                        skipped_records += 1

                except Exception as e:
                    error = ParseError(
                        line_number=line_num,
                        field_index=-1,
                        raw_data=str(row),
                        error_message=str(e),
                    )
                    errors.append(error)

                    if self.config.parse_error_action == ParseErrorAction.RAISE_EXCEPTION:
                        raise
                    elif self.config.parse_error_action == ParseErrorAction.SKIP_ROW:
                        skipped_records += 1
                        continue

        return CsvParseResult(
            headers=headers,
            records=records,
            errors=errors,
            total_records=total_records,
            skipped_records=skipped_records,
        )

    def _process_dict_row(
        self, row: Dict[str, Any], line_num: int
    ) -> Optional[Dict[str, Any]]:
        """Process a dictionary row."""
        processed_row = {}

        for field, value in row.items():
            if field == "_extra_fields":
                continue

            if value is None:
                if self.config.missing_field_action == MissingFieldAction.PARSE_ERROR:
                    raise ValueError(f"Missing value for field {field}")
                elif self.config.missing_field_action == MissingFieldAction.REPLACE_BY_NULL:
                    processed_row[field] = None
                else:  # REPLACE_BY_EMPTY
                    processed_row[field] = ""
            else:
                processed_row[field] = value.strip() if self.config.trim_spaces else value

        return processed_row

    def _process_list_row(
        self, row: List[str], headers: Optional[List[str]], line_num: int
    ) -> Optional[Dict[str, Any]]:
        """Process a list row."""
        if not headers:
            headers = [f"field_{i}" for i in range(len(row))]

        processed_row = {}
        for i, value in enumerate(row):
            if i >= len(headers):
                break

            field = headers[i]
            if not value and value is not "":
                if self.config.missing_field_action == MissingFieldAction.PARSE_ERROR:
                    raise ValueError(f"Missing value for field {field}")
                elif self.config.missing_field_action == MissingFieldAction.REPLACE_BY_NULL:
                    processed_row[field] = None
                else:  # REPLACE_BY_EMPTY
                    processed_row[field] = ""
            else:
                processed_row[field] = value.strip() if self.config.trim_spaces else value

        return processed_row
