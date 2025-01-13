"""
Helper functions for CSV processing.
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re
import hashlib
import json

class CsvHelpers:
    """Collection of helper functions for CSV operations."""

    @staticmethod
    def generate_import_id(
        filename: str,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Generate a unique import ID."""
        timestamp = timestamp or datetime.utcnow()
        data = f"{filename}_{timestamp.isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()

    @staticmethod
    def parse_date(
        value: str,
        formats: List[str] = None
    ) -> Optional[datetime]:
        """Parse date string using multiple formats."""
        formats = formats or [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M:%S'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def clean_field_name(name: str) -> str:
        """Clean and normalize field name."""
        # Remove special characters
        name = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces and - with _
        name = re.sub(r'[-\s]+', '_', name)
        # Convert to lowercase
        return name.strip().lower()

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f}TB"

    @staticmethod
    def calculate_checksum(data: Union[str, bytes]) -> str:
        """Calculate MD5 checksum of data."""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def chunk_list(items: list, chunk_size: int) -> List[list]:
        """Split list into chunks of specified size."""
        return [
            items[i:i + chunk_size]
            for i in range(0, len(items), chunk_size)
        ]

    @staticmethod
    def merge_configs(
        base: Dict[str, Any],
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if (
                key in result and
                isinstance(result[key], dict) and
                isinstance(value, dict)
            ):
                result[key] = CsvHelpers.merge_configs(
                    result[key],
                    value
                )
            else:
                result[key] = value
                
        return result

    @staticmethod
    def validate_json(data: str) -> bool:
        """Validate if string is valid JSON."""
        try:
            json.loads(data)
            return True
        except ValueError:
            return False

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.2f}s"
        minutes = seconds / 60
        if minutes < 60:
            return f"{minutes:.2f}m"
        hours = minutes / 60
        if hours < 24:
            return f"{hours:.2f}h"
        days = hours / 24
        return f"{days:.2f}d"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Limit length
        max_length = 255
        name, ext = os.path.splitext(filename)
        if len(filename) > max_length:
            return name[:max_length-len(ext)] + ext
        return filename

    @staticmethod
    def detect_encoding(
        data: bytes,
        default: str = 'utf-8'
    ) -> str:
        """Detect file encoding."""
        try:
            import chardet
            result = chardet.detect(data)
            return result['encoding'] or default
        except ImportError:
            return default

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def format_error_message(
        template: str,
        **kwargs: Any
    ) -> str:
        """Format error message with variables."""
        return template.format(**kwargs)

    @staticmethod
    def truncate_string(
        text: str,
        max_length: int,
        suffix: str = '...'
    ) -> str:
        """Truncate string to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-len(suffix)] + suffix
