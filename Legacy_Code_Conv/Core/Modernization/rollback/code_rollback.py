"""
Code Rollback Procedures
Version: 1.0.0
Last Updated: 2025-01-10
"""
import os
import sys
import shutil
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeRollback:
    def __init__(
        self,
        repo_path: str,
        backup_dir: str,
        deployment_dir: str
    ):
        self.repo_path = Path(repo_path)
        self.backup_dir = Path(backup_dir)
        self.deployment_dir = Path(deployment_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, tag: str = None) -> Path:
        """Create a backup of the current code state."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tag = tag or 'pre_deployment'
        backup_path = self.backup_dir / f"code_backup_{tag}_{timestamp}"
        
        try:
            logger.info(f"Creating code backup: {backup_path}")
            
            # Copy current code to backup directory
            shutil.copytree(self.deployment_dir, backup_path)
            
            # Save git commit hash if in git repository
            if (self.repo_path / '.git').exists():
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_hash = result.stdout.strip()
                
                with open(backup_path / 'commit_hash.txt', 'w') as f:
                    f.write(commit_hash)
            
            logger.info(f"Backup created successfully: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Restore code from backup."""
        try:
            logger.info(f"Restoring code from backup: {backup_path}")
            
            # Create backup of current state before restore
            self.create_backup(tag='pre_restore')
            
            # Remove current deployment
            if self.deployment_dir.exists():
                shutil.rmtree(self.deployment_dir)
            
            # Copy backup to deployment directory
            shutil.copytree(backup_path, self.deployment_dir)
            
            # Restore git state if applicable
            commit_hash_file = backup_path / 'commit_hash.txt'
            if commit_hash_file.exists():
                with open(commit_hash_file) as f:
                    commit_hash = f.read().strip()
                
                subprocess.run(
                    ['git', 'checkout', commit_hash],
                    cwd=self.repo_path,
                    check=True
                )
            
            logger.info("Code restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            raise
    
    def git_rollback(self, commit_hash: str) -> bool:
        """Rollback to specific git commit."""
        try:
            logger.info(f"Rolling back to commit: {commit_hash}")
            
            # Create backup before rollback
            self.create_backup(tag='pre_rollback')
            
            # Check if commit exists
            result = subprocess.run(
                ['git', 'cat-file', '-t', commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise ValueError(f"Invalid commit hash: {commit_hash}")
            
            # Perform rollback
            subprocess.run(
                ['git', 'checkout', commit_hash],
                cwd=self.repo_path,
                check=True
            )
            
            # Update deployment directory
            if self.deployment_dir.exists():
                shutil.rmtree(self.deployment_dir)
            shutil.copytree(self.repo_path, self.deployment_dir)
            
            logger.info(f"Successfully rolled back to commit: {commit_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Git rollback failed: {str(e)}")
            raise
    
    def verify_code_state(self) -> bool:
        """Verify code state after rollback."""
        try:
            # Check critical files and directories
            required_paths = [
                'core',
                'migrations',
                'tests',
                'requirements.txt',
                'README.md'
            ]
            
            for path in required_paths:
                full_path = self.deployment_dir / path
                if not full_path.exists():
                    logger.error(f"Missing required path: {path}")
                    return False
            
            # Verify Python package structure
            setup_file = self.deployment_dir / 'setup.py'
            init_file = self.deployment_dir / 'core' / '__init__.py'
            
            if not all([setup_file.exists(), init_file.exists()]):
                logger.error("Invalid Python package structure")
                return False
            
            # Check git state if applicable
            if (self.repo_path / '.git').exists():
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if result.stdout.strip():
                    logger.warning("Git working directory is not clean")
            
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
    
    def cleanup_old_backups(self, max_age_days: int = 30):
        """Clean up old code backups."""
        try:
            logger.info(f"Cleaning up backups older than {max_age_days} days")
            cutoff = datetime.now().timestamp() - (max_age_days * 86400)
            
            for backup_dir in self.backup_dir.glob("code_backup_*"):
                if backup_dir.stat().st_mtime < cutoff:
                    shutil.rmtree(backup_dir)
                    logger.info(f"Deleted old backup: {backup_dir}")
                    
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python code_rollback.py [backup|restore|rollback|verify|cleanup]")
        sys.exit(1)
    
    # Load configuration from environment
    config = {
        'repo_path': os.getenv('REPO_PATH', '.'),
        'backup_dir': os.getenv('CODE_BACKUP_DIR', './code_backups'),
        'deployment_dir': os.getenv('DEPLOYMENT_DIR', './deploy')
    }
    
    rollback = CodeRollback(**config)
    command = sys.argv[1]
    
    try:
        if command == 'backup':
            rollback.create_backup()
        
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("Please specify backup directory to restore")
                sys.exit(1)
            rollback.restore_backup(Path(sys.argv[2]))
        
        elif command == 'rollback':
            if len(sys.argv) < 3:
                print("Please specify commit hash")
                sys.exit(1)
            rollback.git_rollback(sys.argv[2])
        
        elif command == 'verify':
            success = rollback.verify_code_state()
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
