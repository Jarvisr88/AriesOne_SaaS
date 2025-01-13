from typing import Dict, List, Optional, BinaryIO
from datetime import datetime
import csv
import json
import pandas as pd
import openpyxl
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.data_exchange import (
    FileImport,
    FileExport,
    FileMapping,
    ValidationRule
)

class FileService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.supported_formats = ["csv", "xlsx", "json", "xml"]
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    async def import_file(
        self,
        file: UploadFile,
        mapping_id: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """Import data from file"""
        try:
            # Validate file
            await self._validate_file(file)
            
            # Get mapping
            mapping = await self._get_mapping(mapping_id)
            
            # Create import record
            import_record = await FileImport.create(
                filename=file.filename,
                format=self._get_file_format(file.filename),
                mapping_id=mapping_id,
                status="processing",
                options=options or {},
                created_at=datetime.now()
            )
            
            # Read and parse file
            data = await self._read_file(file, mapping)
            
            # Validate data
            validation_results = await self._validate_data(
                data,
                mapping.validation_rules
            )
            
            if validation_results["errors"]:
                import_record.status = "failed"
                import_record.error_details = validation_results["errors"]
                await import_record.save()
                
                return {
                    "status": "failed",
                    "import_id": str(import_record.id),
                    "errors": validation_results["errors"]
                }
            
            # Transform data
            transformed_data = await self._transform_data(
                data,
                mapping.field_mappings,
                mapping.transformation_rules
            )
            
            # Process import
            result = await self._process_import(
                transformed_data,
                mapping,
                options
            )
            
            # Update import record
            import_record.status = "completed"
            import_record.processed_records = len(transformed_data)
            import_record.completed_at = datetime.now()
            await import_record.save()
            
            return {
                "status": "success",
                "import_id": str(import_record.id),
                "records_processed": len(transformed_data),
                "details": result
            }
        except Exception as e:
            logger.error(f"File import failed: {str(e)}")
            if import_record:
                import_record.status = "failed"
                import_record.error_details = str(e)
                await import_record.save()
            raise HTTPException(status_code=500, detail=str(e))

    async def export_data(
        self,
        format: str,
        data: List[Dict],
        mapping_id: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """Export data to file"""
        try:
            # Validate format
            if format not in self.supported_formats:
                raise ValueError(f"Unsupported format: {format}")
            
            # Get mapping
            mapping = await self._get_mapping(mapping_id)
            
            # Create export record
            export_record = await FileExport.create(
                format=format,
                mapping_id=mapping_id,
                status="processing",
                options=options or {},
                created_at=datetime.now()
            )
            
            # Transform data
            transformed_data = await self._transform_data(
                data,
                mapping.field_mappings,
                mapping.transformation_rules
            )
            
            # Generate file
            file_content = await self._generate_file(
                transformed_data,
                format,
                mapping,
                options
            )
            
            # Store file
            file_path = await self._store_file(
                file_content,
                format,
                export_record.id
            )
            
            # Update export record
            export_record.status = "completed"
            export_record.file_path = file_path
            export_record.record_count = len(transformed_data)
            export_record.completed_at = datetime.now()
            await export_record.save()
            
            return {
                "status": "success",
                "export_id": str(export_record.id),
                "file_path": file_path,
                "record_count": len(transformed_data)
            }
        except Exception as e:
            logger.error(f"Data export failed: {str(e)}")
            if export_record:
                export_record.status = "failed"
                export_record.error_details = str(e)
                await export_record.save()
            raise HTTPException(status_code=500, detail=str(e))

    async def create_mapping(
        self,
        mapping_data: Dict
    ) -> FileMapping:
        """Create file mapping"""
        try:
            # Validate mapping data
            self._validate_mapping_data(mapping_data)
            
            # Create mapping
            mapping = await FileMapping.create(
                name=mapping_data["name"],
                description=mapping_data.get("description"),
                field_mappings=mapping_data["field_mappings"],
                validation_rules=mapping_data.get("validation_rules", {}),
                transformation_rules=mapping_data.get("transformation_rules", {}),
                created_at=datetime.now()
            )
            
            return mapping
        except Exception as e:
            logger.error(f"Failed to create mapping: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check file size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > self.max_file_size:
            raise ValueError(
                f"File too large. Maximum size is {self.max_file_size} bytes"
            )
        
        # Check format
        format = self._get_file_format(file.filename)
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {format}")

    async def _get_mapping(self, mapping_id: str) -> FileMapping:
        """Get file mapping"""
        mapping = await FileMapping.get(id=mapping_id)
        if not mapping:
            raise ValueError(f"Mapping not found: {mapping_id}")
        return mapping

    async def _read_file(
        self,
        file: UploadFile,
        mapping: FileMapping
    ) -> List[Dict]:
        """Read and parse file content"""
        format = self._get_file_format(file.filename)
        content = await file.read()
        
        if format == "csv":
            return self._parse_csv(content)
        elif format == "xlsx":
            return self._parse_xlsx(content)
        elif format == "json":
            return self._parse_json(content)
        elif format == "xml":
            return self._parse_xml(content)
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def _validate_data(
        self,
        data: List[Dict],
        rules: Dict
    ) -> Dict:
        """Validate data against rules"""
        errors = []
        
        for idx, record in enumerate(data):
            record_errors = []
            
            for field, rule in rules.items():
                if field in record:
                    value = record[field]
                    
                    # Required field
                    if rule.get("required") and not value:
                        record_errors.append(
                            f"Field '{field}' is required"
                        )
                    
                    # Data type
                    if rule.get("type"):
                        if not self._validate_type(
                            value,
                            rule["type"]
                        ):
                            record_errors.append(
                                f"Field '{field}' must be of type {rule['type']}"
                            )
                    
                    # Pattern
                    if rule.get("pattern"):
                        if not self._validate_pattern(
                            value,
                            rule["pattern"]
                        ):
                            record_errors.append(
                                f"Field '{field}' does not match pattern"
                            )
                    
                    # Range
                    if rule.get("range"):
                        if not self._validate_range(
                            value,
                            rule["range"]
                        ):
                            record_errors.append(
                                f"Field '{field}' is out of range"
                            )
            
            if record_errors:
                errors.append({
                    "row": idx + 1,
                    "errors": record_errors
                })
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    async def _transform_data(
        self,
        data: List[Dict],
        mappings: Dict,
        rules: Dict
    ) -> List[Dict]:
        """Transform data using mappings and rules"""
        transformed = []
        
        for record in data:
            # Apply field mappings
            mapped_record = {}
            for target_field, source_field in mappings.items():
                if isinstance(source_field, str):
                    mapped_record[target_field] = record.get(source_field)
                elif isinstance(source_field, dict):
                    if "constant" in source_field:
                        mapped_record[target_field] = source_field["constant"]
                    elif "concatenate" in source_field:
                        values = [
                            record.get(field, "")
                            for field in source_field["concatenate"]
                        ]
                        mapped_record[target_field] = "".join(
                            str(v) for v in values
                        )
            
            # Apply transformation rules
            for field, rule in rules.items():
                if field in mapped_record:
                    if rule.get("type") == "date":
                        mapped_record[field] = self._transform_date(
                            mapped_record[field],
                            rule.get("format", "%Y-%m-%d")
                        )
                    elif rule.get("type") == "number":
                        mapped_record[field] = self._transform_number(
                            mapped_record[field],
                            rule.get("decimals", 2)
                        )
                    elif rule.get("type") == "enum":
                        mapped_record[field] = rule["values"].get(
                            mapped_record[field],
                            mapped_record[field]
                        )
            
            transformed.append(mapped_record)
        
        return transformed

    def _get_file_format(self, filename: str) -> str:
        """Get file format from filename"""
        return filename.split(".")[-1].lower()

    def _parse_csv(self, content: bytes) -> List[Dict]:
        """Parse CSV content"""
        data = []
        content_str = content.decode("utf-8")
        reader = csv.DictReader(content_str.splitlines())
        for row in reader:
            data.append(dict(row))
        return data

    def _parse_xlsx(self, content: bytes) -> List[Dict]:
        """Parse Excel content"""
        df = pd.read_excel(content)
        return df.to_dict("records")

    def _parse_json(self, content: bytes) -> List[Dict]:
        """Parse JSON content"""
        return json.loads(content)

    def _parse_xml(self, content: bytes) -> List[Dict]:
        """Parse XML content"""
        # Implement XML parsing
        pass

    def _validate_type(
        self,
        value: any,
        type_name: str
    ) -> bool:
        """Validate value type"""
        try:
            if type_name == "string":
                return isinstance(value, str)
            elif type_name == "number":
                float(value)
                return True
            elif type_name == "integer":
                int(value)
                return True
            elif type_name == "boolean":
                return isinstance(value, bool)
            elif type_name == "date":
                datetime.strptime(value, "%Y-%m-%d")
                return True
            return False
        except:
            return False

    def _validate_pattern(
        self,
        value: str,
        pattern: str
    ) -> bool:
        """Validate value against pattern"""
        import re
        return bool(re.match(pattern, str(value)))

    def _validate_range(
        self,
        value: float,
        range_rule: Dict
    ) -> bool:
        """Validate value within range"""
        try:
            num_value = float(value)
            min_val = float(range_rule.get("min", "-inf"))
            max_val = float(range_rule.get("max", "inf"))
            return min_val <= num_value <= max_val
        except:
            return False

    def _transform_date(
        self,
        value: str,
        format: str
    ) -> str:
        """Transform date value"""
        if not value:
            return ""
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            return dt.strftime(format)
        except:
            return value

    def _transform_number(
        self,
        value: float,
        decimals: int
    ) -> float:
        """Transform number value"""
        if not value:
            return 0.0
        try:
            return round(float(value), decimals)
        except:
            return 0.0

    def _validate_mapping_data(self, mapping_data: Dict) -> None:
        """Validate mapping data"""
        required_fields = ["name", "field_mappings"]
        for field in required_fields:
            if field not in mapping_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(mapping_data["field_mappings"], dict):
            raise ValueError("Field mappings must be a dictionary")
