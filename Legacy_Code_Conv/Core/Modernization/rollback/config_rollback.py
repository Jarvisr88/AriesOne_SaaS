"""
Configuration Rollback Procedures
Version: 1.0.0
Last Updated: 2025-01-10
"""
import os
import sys
import json
import yaml
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigRollback:
    def __init__(
        self,
        config_dir: str,
        backup_dir: str,
        env_file: str = '.env'
    ):
        self.config_dir = Path(config_dir)
        self.backup_dir = Path(backup_dir)
        self.env_file = Path(env_file)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, tag: str = None) -> Path:
        """Create a backup of current configuration."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tag = tag or 'pre_change'
        backup_path = self.backup_dir / f"config_backup_{tag}_{timestamp}"
        
        try:
            logger.info(f"Creating config backup: {backup_path}")
            backup_path.mkdir(parents=True)
            
            # Backup configuration files
            if self.config_dir.exists():
                shutil.copytree(
                    self.config_dir,
                    backup_path / 'config',
                    dirs_exist_ok=True
                )
            
            # Backup environment file
            if self.env_file.exists():
                shutil.copy2(self.env_file, backup_path)
            
            # Save current environment variables
            env_vars = {
                key: value for key, value in os.environ.items()
                if not key.startswith('_')
            }
            
            with open(backup_path / 'environment.json', 'w') as f:
                json.dump(env_vars, f, indent=2)
            
            logger.info(f"Backup created successfully: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Restore configuration from backup."""
        try:
            logger.info(f"Restoring config from backup: {backup_path}")
            
            # Create backup of current state before restore
            self.create_backup(tag='pre_restore')
            
            # Restore configuration files
            config_backup = backup_path / 'config'
            if config_backup.exists():
                if self.config_dir.exists():
                    shutil.rmtree(self.config_dir)
                shutil.copytree(config_backup, self.config_dir)
            
            # Restore environment file
            env_backup = backup_path / '.env'
            if env_backup.exists():
                shutil.copy2(env_backup, self.env_file)
            
            logger.info("Configuration restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise
    
    def update_config(self, config_file: str, updates: Dict[str, Any]) -> bool:
        """Update specific configuration file with new values."""
        try:
            file_path = self.config_dir / config_file
            
            # Create backup before modification
            self.create_backup(tag='pre_update')
            
            # Load existing configuration
            with open(file_path) as f:
                if file_path.suffix == '.json':
                    config = json.load(f)
                elif file_path.suffix in ['.yml', '.yaml']:
                    config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Apply updates
            def deep_update(d, u):
                for k, v in u.items():
                    if isinstance(v, dict):
                        d[k] = deep_update(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d
            
            config = deep_update(config, updates)
            
            # Save updated configuration
            with open(file_path, 'w') as f:
                if file_path.suffix == '.json':
                    json.dump(config, f, indent=2)
                else:
                    yaml.safe_dump(config, f)
            
            logger.info(f"Configuration updated successfully: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Update failed: {str(e)}")
            raise
    
    def verify_config(self) -> bool:
        """Verify configuration state after changes."""
        try:
            # Check required configuration files
            required_files = [
                'config.yml',
                'logging.yml',
                'database.yml'
            ]
            
            for file in required_files:
                if not (self.config_dir / file).exists():
                    logger.error(f"Missing required config file: {file}")
                    return False
            
            # Validate configuration format
            for file in self.config_dir.glob('*.y*ml'):
                try:
                    with open(file) as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    logger.error(f"Invalid YAML in {file}: {str(e)}")
                    return False
            
            for file in self.config_dir.glob('*.json'):
                try:
                    with open(file) as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in {file}: {str(e)}")
                    return False
            
            # Check environment file
            if self.env_file.exists():
                try:
                    with open(self.env_file) as f:
                        for line in f:
                            if line.strip() and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                if not key or not value:
                                    raise ValueError(f"Invalid environment variable: {line}")
                except Exception as e:
                    logger.error(f"Invalid environment file: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
    
    def cleanup_old_backups(self, max_age_days: int = 30):
        """Clean up old configuration backups."""
        try:
            logger.info(f"Cleaning up backups older than {max_age_days} days")
            cutoff = datetime.now().timestamp() - (max_age_days * 86400)
            
            for backup_dir in self.backup_dir.glob("config_backup_*"):
                if backup_dir.stat().st_mtime < cutoff:
                    shutil.rmtree(backup_dir)
                    logger.info(f"Deleted old backup: {backup_dir}")
                    
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python config_rollback.py [backup|restore|update|verify|cleanup]")
        sys.exit(1)
    
    # Load configuration from environment
    config = {
        'config_dir': os.getenv('CONFIG_DIR', './config'),
        'backup_dir': os.getenv('CONFIG_BACKUP_DIR', './config_backups'),
        'env_file': os.getenv('ENV_FILE', '.env')
    }
    
    rollback = ConfigRollback(**config)
    command = sys.argv[1]
    
    try:
        if command == 'backup':
            rollback.create_backup()
        
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("Please specify backup directory to restore")
                sys.exit(1)
            rollback.restore_backup(Path(sys.argv[2]))
        
        elif command == 'update':
            if len(sys.argv) < 4:
                print("Please specify config file and JSON updates")
                sys.exit(1)
            updates = json.loads(sys.argv[3])
            rollback.update_config(sys.argv[2], updates)
        
        elif command == 'verify':
            success = rollback.verify_config()
            sys.exit(0 if success else 1)
        
        elif command == 'cleanup':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            rollback.cleanup_old_backups(days)
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
