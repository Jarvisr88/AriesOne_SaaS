import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, ValidationError
import json
from datetime import datetime
import numpy as np
from pathlib import Path
import logging
from app.core.config import settings
from app.models.core import ProcessingStatus

logger = logging.getLogger(__name__)

class ColumnSchema(BaseModel):
    name: str
    data_type: str
    required: bool = True
    validation_rules: Optional[Dict[str, Any]] = None
    transformation_rules: Optional[Dict[str, Any]] = None

class CSVSchema(BaseModel):
    name: str
    columns: List[ColumnSchema]
    delimiter: str = ','
    encoding: str = 'utf-8'
    skip_rows: int = 0
    has_header: bool = True

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[Dict[str, Any]]
    row_count: int
    valid_row_count: int
    invalid_row_count: int

class ProcessingResult(BaseModel):
    file_name: str
    schema_name: str
    status: ProcessingStatus
    total_rows: int
    processed_rows: int
    failed_rows: int
    errors: List[Dict[str, Any]]
    start_time: datetime
    end_time: Optional[datetime] = None
    output_path: Optional[str] = None

class CSVProcessor:
    def __init__(self):
        self.schemas: Dict[str, CSVSchema] = {}
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load CSV schemas from configuration files."""
        schema_dir = Path(settings.CSV_SCHEMA_DIR)
        for schema_file in schema_dir.glob("*.json"):
            try:
                schema_data = json.loads(schema_file.read_text())
                schema = CSVSchema(**schema_data)
                self.schemas[schema.name] = schema
            except Exception as e:
                logger.error(f"Failed to load schema {schema_file}: {str(e)}")

    def detect_schema(self, file_path: str) -> Tuple[Optional[str], float]:
        """
        Detect the most likely schema for a CSV file.
        Returns schema name and confidence score.
        """
        try:
            # Read first few rows to analyze structure
            df = pd.read_csv(file_path, nrows=100)
            best_match = (None, 0.0)

            for schema_name, schema in self.schemas.items():
                score = self._calculate_schema_match_score(df, schema)
                if score > best_match[1]:
                    best_match = (schema_name, score)

            return best_match
        except Exception as e:
            logger.error(f"Schema detection failed: {str(e)}")
            return None, 0.0

    def _calculate_schema_match_score(self, df: pd.DataFrame, schema: CSVSchema) -> float:
        """Calculate how well a dataframe matches a schema."""
        total_checks = 0
        passed_checks = 0

        # Check column presence
        schema_cols = {col.name for col in schema.columns}
        df_cols = set(df.columns)
        common_cols = schema_cols.intersection(df_cols)
        
        col_match_score = len(common_cols) / len(schema_cols)
        passed_checks += col_match_score
        total_checks += 1

        # Check data types for common columns
        type_checks = 0
        passed_types = 0
        
        for col in schema.columns:
            if col.name in common_cols:
                type_checks += 1
                if self._check_column_type(df[col.name], col.data_type):
                    passed_types += 1

        if type_checks > 0:
            type_match_score = passed_types / type_checks
            passed_checks += type_match_score
            total_checks += 1

        return passed_checks / total_checks if total_checks > 0 else 0.0

    def _check_column_type(self, series: pd.Series, expected_type: str) -> bool:
        """Check if a column's data matches the expected type."""
        try:
            if expected_type == 'string':
                return series.dtype == 'object'
            elif expected_type == 'integer':
                return pd.to_numeric(series, errors='coerce').notna().all()
            elif expected_type == 'float':
                return pd.to_numeric(series, errors='coerce').notna().all()
            elif expected_type == 'date':
                return pd.to_datetime(series, errors='coerce').notna().all()
            elif expected_type == 'boolean':
                return series.isin([True, False, 0, 1, 'true', 'false', 'True', 'False']).all()
            return False
        except Exception:
            return False

    def validate_file(self, file_path: str, schema_name: str) -> ValidationResult:
        """Validate a CSV file against a schema."""
        schema = self.schemas.get(schema_name)
        if not schema:
            raise ValueError(f"Schema '{schema_name}' not found")

        errors = []
        try:
            df = pd.read_csv(
                file_path,
                delimiter=schema.delimiter,
                encoding=schema.encoding,
                skiprows=schema.skip_rows,
                header=0 if schema.has_header else None
            )

            # Validate column presence
            missing_cols = [
                col.name for col in schema.columns
                if col.required and col.name not in df.columns
            ]
            if missing_cols:
                errors.append({
                    "type": "missing_columns",
                    "columns": missing_cols
                })

            # Validate data types and rules
            for col in schema.columns:
                if col.name in df.columns:
                    col_errors = self._validate_column(df[col.name], col)
                    errors.extend(col_errors)

            valid_rows = df.index[~df.index.isin([e["row"] for e in errors if "row" in e])]
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                row_count=len(df),
                valid_row_count=len(valid_rows),
                invalid_row_count=len(df) - len(valid_rows)
            )

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            errors.append({
                "type": "file_error",
                "message": str(e)
            })
            return ValidationResult(
                is_valid=False,
                errors=errors,
                row_count=0,
                valid_row_count=0,
                invalid_row_count=0
            )

    def _validate_column(self, series: pd.Series, schema: ColumnSchema) -> List[Dict[str, Any]]:
        """Validate a column against its schema."""
        errors = []

        # Check data type
        type_errors = self._validate_data_type(series, schema.data_type)
        errors.extend(type_errors)

        # Check validation rules
        if schema.validation_rules:
            rule_errors = self._apply_validation_rules(series, schema.validation_rules)
            errors.extend(rule_errors)

        return errors

    def _validate_data_type(self, series: pd.Series, expected_type: str) -> List[Dict[str, Any]]:
        """Validate data type of a column."""
        errors = []
        try:
            if expected_type == 'integer':
                invalid_mask = pd.to_numeric(series, errors='coerce').isna() & series.notna()
            elif expected_type == 'float':
                invalid_mask = pd.to_numeric(series, errors='coerce').isna() & series.notna()
            elif expected_type == 'date':
                invalid_mask = pd.to_datetime(series, errors='coerce').isna() & series.notna()
            elif expected_type == 'boolean':
                invalid_mask = ~series.isin([True, False, 0, 1, 'true', 'false', 'True', 'False'])
            else:  # string
                invalid_mask = series.isna()

            invalid_rows = series.index[invalid_mask].tolist()
            if invalid_rows:
                errors.append({
                    "type": "invalid_type",
                    "column": series.name,
                    "expected_type": expected_type,
                    "rows": invalid_rows
                })
        except Exception as e:
            logger.error(f"Type validation failed for column {series.name}: {str(e)}")
            errors.append({
                "type": "validation_error",
                "column": series.name,
                "message": str(e)
            })

        return errors

    def _apply_validation_rules(
        self,
        series: pd.Series,
        rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply validation rules to a column."""
        errors = []

        for rule, value in rules.items():
            if rule == "min":
                invalid_mask = series < value
            elif rule == "max":
                invalid_mask = series > value
            elif rule == "regex":
                invalid_mask = ~series.astype(str).str.match(value)
            elif rule == "unique":
                invalid_mask = series.duplicated() if value else pd.Series(False, index=series.index)
            elif rule == "allowed_values":
                invalid_mask = ~series.isin(value)
            else:
                continue

            invalid_rows = series.index[invalid_mask].tolist()
            if invalid_rows:
                errors.append({
                    "type": "rule_violation",
                    "column": series.name,
                    "rule": rule,
                    "value": value,
                    "rows": invalid_rows
                })

        return errors

    def process_file(
        self,
        file_path: str,
        schema_name: str,
        output_path: str
    ) -> ProcessingResult:
        """Process a CSV file according to its schema."""
        schema = self.schemas.get(schema_name)
        if not schema:
            raise ValueError(f"Schema '{schema_name}' not found")

        start_time = datetime.utcnow()
        result = ProcessingResult(
            file_name=Path(file_path).name,
            schema_name=schema_name,
            status=ProcessingStatus.IN_PROGRESS,
            total_rows=0,
            processed_rows=0,
            failed_rows=0,
            errors=[],
            start_time=start_time
        )

        try:
            # Validate file first
            validation = self.validate_file(file_path, schema_name)
            if not validation.is_valid:
                result.status = ProcessingStatus.FAILED
                result.errors = validation.errors
                result.total_rows = validation.row_count
                result.failed_rows = validation.invalid_row_count
                result.end_time = datetime.utcnow()
                return result

            # Read and process the file
            df = pd.read_csv(
                file_path,
                delimiter=schema.delimiter,
                encoding=schema.encoding,
                skiprows=schema.skip_rows,
                header=0 if schema.has_header else None
            )

            result.total_rows = len(df)

            # Apply transformations
            for col in schema.columns:
                if col.name in df.columns and col.transformation_rules:
                    df[col.name] = self._apply_transformations(
                        df[col.name],
                        col.transformation_rules
                    )

            # Save processed file
            df.to_csv(output_path, index=False)

            result.status = ProcessingStatus.COMPLETED
            result.processed_rows = len(df)
            result.output_path = output_path
            result.end_time = datetime.utcnow()

        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            result.status = ProcessingStatus.FAILED
            result.errors.append({
                "type": "processing_error",
                "message": str(e)
            })
            result.end_time = datetime.utcnow()

        return result

    def _apply_transformations(
        self,
        series: pd.Series,
        rules: Dict[str, Any]
    ) -> pd.Series:
        """Apply transformation rules to a column."""
        for rule, value in rules.items():
            if rule == "uppercase":
                series = series.str.upper() if value else series
            elif rule == "lowercase":
                series = series.str.lower() if value else series
            elif rule == "trim":
                series = series.str.strip() if value else series
            elif rule == "replace":
                series = series.replace(value["from"], value["to"])
            elif rule == "format":
                if value == "date":
                    series = pd.to_datetime(series).dt.strftime("%Y-%m-%d")
                elif value == "number":
                    series = pd.to_numeric(series, errors='coerce')
            elif rule == "default":
                series = series.fillna(value)

        return series
