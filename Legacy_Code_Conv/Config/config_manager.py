"""
Configuration management module using modern configuration patterns.
"""
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path
from pydantic import BaseModel, validator
from fastapi import HTTPException
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Database configuration model."""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: Optional[str] = "prefer"
    application_name: Optional[str] = "AriesOne_SaaS"

    @validator('port')
    def valid_port(cls, v):
        """Validate port number."""
        if v < 1 or v > 65535:
            raise ValueError('Invalid port number')
        return v

class EnvironmentConfig(BaseModel):
    """Environment configuration model."""
    env_name: str
    debug_mode: bool = False
    log_level: str = "INFO"
    max_connections: int = 20
    connection_timeout: int = 30
    database: DatabaseConfig

    @validator('log_level')
    def valid_log_level(cls, v):
        """Validate logging level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid log level. Must be one of: {", ".join(valid_levels)}')
        return v.upper()

class ConfigManager:
    """Handle configuration management and ODBC migration."""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'config.yaml'
        self.backup_dir = self.config_dir / 'backups'
        self.current_config: Optional[EnvironmentConfig] = None

        # Create directories if they don't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _create_backup(self):
        """Create backup of current configuration."""
        if self.config_file.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f'config_backup_{timestamp}.yaml'
            backup_file.write_bytes(self.config_file.read_bytes())
            logger.info(f'Created backup: {backup_file}')

    def load_config(self, env_name: str = "development") -> EnvironmentConfig:
        """Load configuration for specified environment."""
        try:
            if not self.config_file.exists():
                raise FileNotFoundError(f'Configuration file not found: {self.config_file}')

            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)

            if env_name not in config_data:
                raise KeyError(f'Environment not found: {env_name}')

            self.current_config = EnvironmentConfig(**config_data[env_name])
            logger.info(f'Loaded configuration for environment: {env_name}')
            return self.current_config

        except Exception as e:
            logger.error(f'Error loading configuration: {str(e)}')
            raise HTTPException(
                status_code=500,
                detail=f'Failed to load configuration: {str(e)}'
            )

    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            # Validate configuration
            for env_name, env_config in config.items():
                EnvironmentConfig(**env_config)

            # Create backup
            self._create_backup()

            # Save new configuration
            with open(self.config_file, 'w') as f:
                yaml.safe_dump(config, f, default_flow_style=False)

            logger.info('Configuration saved successfully')

        except Exception as e:
            logger.error(f'Error saving configuration: {str(e)}')
            raise HTTPException(
                status_code=500,
                detail=f'Failed to save configuration: {str(e)}'
            )

    def migrate_odbc_config(self, odbc_file: str):
        """Migrate ODBC configuration to new format."""
        try:
            if not os.path.exists(odbc_file):
                raise FileNotFoundError(f'ODBC configuration file not found: {odbc_file}')

            # Read ODBC configuration
            with open(odbc_file, 'r') as f:
                odbc_config = f.read()

            # Parse ODBC configuration
            config_dict = {}
            current_section = None
            
            for line in odbc_config.splitlines():
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                    
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    config_dict[current_section] = {}
                elif current_section and '=' in line:
                    key, value = line.split('=', 1)
                    config_dict[current_section][key.strip()] = value.strip()

            # Convert to new format
            new_config = {
                "development": {
                    "env_name": "development",
                    "debug_mode": True,
                    "log_level": "DEBUG",
                    "max_connections": 20,
                    "connection_timeout": 30,
                    "database": {
                        "host": config_dict.get("Database", {}).get("Server", "localhost"),
                        "port": int(config_dict.get("Database", {}).get("Port", "5432")),
                        "database": config_dict.get("Database", {}).get("Database", ""),
                        "username": config_dict.get("Database", {}).get("Username", ""),
                        "password": config_dict.get("Database", {}).get("Password", ""),
                        "ssl_mode": "prefer",
                        "application_name": "AriesOne_SaaS"
                    }
                },
                "production": {
                    "env_name": "production",
                    "debug_mode": False,
                    "log_level": "INFO",
                    "max_connections": 100,
                    "connection_timeout": 30,
                    "database": {
                        "host": config_dict.get("Database", {}).get("Server", "localhost"),
                        "port": int(config_dict.get("Database", {}).get("Port", "5432")),
                        "database": config_dict.get("Database", {}).get("Database", ""),
                        "username": config_dict.get("Database", {}).get("Username", ""),
                        "password": config_dict.get("Database", {}).get("Password", ""),
                        "ssl_mode": "verify-full",
                        "application_name": "AriesOne_SaaS"
                    }
                }
            }

            # Save new configuration
            self.save_config(new_config)
            logger.info('ODBC configuration migrated successfully')

            # Create backup of ODBC file
            odbc_backup = Path(odbc_file + '.bak')
            Path(odbc_file).rename(odbc_backup)
            logger.info(f'Created ODBC backup: {odbc_backup}')

        except Exception as e:
            logger.error(f'Error migrating ODBC configuration: {str(e)}')
            raise HTTPException(
                status_code=500,
                detail=f'Failed to migrate ODBC configuration: {str(e)}'
            )

    def get_database_url(self, env_name: str = "development") -> str:
        """Get database URL for SQLAlchemy."""
        config = self.load_config(env_name)
        db = config.database
        
        return (
            f"postgresql://{db.username}:{db.password}@{db.host}:{db.port}/{db.database}"
            f"?application_name={db.application_name}&sslmode={db.ssl_mode}"
        )

    def get_connection_pool_config(self, env_name: str = "development") -> Dict[str, Any]:
        """Get connection pool configuration."""
        config = self.load_config(env_name)
        
        return {
            "max_connections": config.max_connections,
            "connection_timeout": config.connection_timeout
        }
