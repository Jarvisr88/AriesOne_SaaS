"""
Configuration management for CSV processing.
"""
from typing import Dict, Any, Optional
import os
import json
from pathlib import Path
from pydantic import BaseSettings, Field

class CsvSettings(BaseSettings):
    """CSV processing settings."""
    
    # Database settings
    DB_HOST: str = Field("localhost", env="CSV_DB_HOST")
    DB_PORT: int = Field(5432, env="CSV_DB_PORT")
    DB_NAME: str = Field(..., env="CSV_DB_NAME")
    DB_USER: str = Field(..., env="CSV_DB_USER")
    DB_PASSWORD: str = Field(..., env="CSV_DB_PASSWORD")
    
    # File processing settings
    MAX_FILE_SIZE: int = Field(100 * 1024 * 1024, env="CSV_MAX_FILE_SIZE")  # 100MB
    CHUNK_SIZE: int = Field(8192, env="CSV_CHUNK_SIZE")
    TEMP_DIR: str = Field("/tmp/csv_imports", env="CSV_TEMP_DIR")
    
    # Processing settings
    MAX_WORKERS: int = Field(4, env="CSV_MAX_WORKERS")
    BATCH_SIZE: int = Field(1000, env="CSV_BATCH_SIZE")
    
    # Error handling
    MAX_ERRORS: int = Field(1000, env="CSV_MAX_ERRORS")
    ERROR_THRESHOLD: float = Field(0.1, env="CSV_ERROR_THRESHOLD")
    
    # Cleanup settings
    RETENTION_DAYS: int = Field(30, env="CSV_RETENTION_DAYS")
    
    # API settings
    API_TIMEOUT: int = Field(300, env="CSV_API_TIMEOUT")
    RATE_LIMIT: int = Field(100, env="CSV_RATE_LIMIT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class ConfigManager:
    """Configuration manager for CSV processing."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.json"
        self.settings = CsvSettings()
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)

    def save_config(self):
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
        self.save_config()

    def update(self, config: Dict[str, Any]):
        """Update multiple configuration values."""
        self._config.update(config)
        self.save_config()

    def get_database_url(self) -> str:
        """Get database URL from settings."""
        return (
            f"postgresql://{self.settings.DB_USER}:"
            f"{self.settings.DB_PASSWORD}@{self.settings.DB_HOST}:"
            f"{self.settings.DB_PORT}/{self.settings.DB_NAME}"
        )

    def ensure_temp_dir(self):
        """Ensure temporary directory exists."""
        Path(self.settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)

    def get_temp_path(self, filename: str) -> str:
        """Get temporary file path."""
        return os.path.join(self.settings.TEMP_DIR, filename)

    def cleanup_temp_files(self):
        """Clean up old temporary files."""
        import time
        from datetime import datetime, timedelta
        
        retention_time = time.time() - (
            self.settings.RETENTION_DAYS * 24 * 60 * 60
        )
        
        for file in os.listdir(self.settings.TEMP_DIR):
            file_path = os.path.join(self.settings.TEMP_DIR, file)
            if os.path.getctime(file_path) < retention_time:
                try:
                    os.remove(file_path)
                except OSError:
                    pass

    @property
    def default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "csv": {
                "delimiter": ",",
                "quote_char": '"',
                "escape_char": "\\",
                "has_headers": True,
                "skip_empty_lines": True,
                "trim_spaces": True,
                "max_field_size": 100000,
                "encoding": "utf-8"
            },
            "validation": {
                "strict_mode": False,
                "allow_missing_fields": True,
                "max_errors": self.settings.MAX_ERRORS,
                "error_threshold": self.settings.ERROR_THRESHOLD
            },
            "processing": {
                "chunk_size": self.settings.CHUNK_SIZE,
                "max_workers": self.settings.MAX_WORKERS,
                "batch_size": self.settings.BATCH_SIZE
            },
            "storage": {
                "temp_dir": self.settings.TEMP_DIR,
                "retention_days": self.settings.RETENTION_DAYS
            },
            "api": {
                "timeout": self.settings.API_TIMEOUT,
                "rate_limit": self.settings.RATE_LIMIT
            }
        }

    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self._config = self.default_config.copy()
        self.save_config()

    def validate_config(self) -> bool:
        """Validate current configuration."""
        try:
            # Validate database connection
            import sqlalchemy
            engine = sqlalchemy.create_engine(self.get_database_url())
            with engine.connect():
                pass

            # Validate temp directory
            self.ensure_temp_dir()
            test_file = os.path.join(self.settings.TEMP_DIR, "test")
            Path(test_file).touch()
            os.remove(test_file)

            return True
        except Exception as e:
            print(f"Configuration validation failed: {str(e)}")
            return False
