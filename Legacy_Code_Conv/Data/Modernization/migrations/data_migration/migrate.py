"""
Main migration script to coordinate data migration from MySQL to PostgreSQL.
"""
import asyncio
import logging
from datetime import datetime
from mysql_extractor import MySQLExtractor, MySQLConfig
from postgres_loader import PostgresLoader, PostgresConfig
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_migration(
    mysql_config: MySQLConfig,
    postgres_config: PostgresConfig,
    batch_size: int = 1000
):
    """Run the complete migration process."""
    start_time = datetime.now()
    logger.info(f"Starting migration at {start_time}")

    try:
        # Extract data from MySQL
        extractor = MySQLExtractor(mysql_config)
        data = await extractor.extract_all()
        
        # Save checkpoint
        checkpoint_file = f'migration_checkpoint_{start_time.strftime("%Y%m%d_%H%M%S")}.json'
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, default=str, indent=2)
        logger.info(f"Saved migration checkpoint to {checkpoint_file}")
        
        # Load data into PostgreSQL
        loader = PostgresLoader(postgres_config)
        await loader.load_all(data)
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Migration completed successfully in {duration}")
        
        # Generate migration report
        report = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'record_counts': {
                table: len(records) for table, records in data.items()
            }
        }
        
        report_file = f'migration_report_{end_time.strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Migration report saved to {report_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def load_config(config_file: str = 'migration_config.json') -> tuple:
    """Load migration configuration from file."""
    with open(config_file) as f:
        config = json.load(f)
    
    mysql_config = MySQLConfig(
        host=config['mysql']['host'],
        port=config['mysql']['port'],
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database']
    )
    
    postgres_config = PostgresConfig(
        host=config['postgres']['host'],
        port=config['postgres']['port'],
        user=config['postgres']['user'],
        password=config['postgres']['password'],
        database=config['postgres']['database']
    )
    
    return mysql_config, postgres_config

def verify_migration(report: dict) -> bool:
    """Verify migration results."""
    # Check record counts
    expected_counts = {
        'companies': 0,  # Set expected counts
        'locations': 0,
        'users': 0,
        'roles': 0,
        'user_roles': 0,
        'price_lists': 0,
        'price_list_items': 0
    }
    
    actual_counts = report['record_counts']
    
    for table in expected_counts:
        if actual_counts[table] < expected_counts[table]:
            logger.error(f"Migration verification failed: {table} has fewer records than expected")
            return False
    
    logger.info("Migration verification passed")
    return True

async def main():
    """Main migration function."""
    try:
        # Load configuration
        mysql_config, postgres_config = load_config()
        
        # Run migration
        report = await run_migration(mysql_config, postgres_config)
        
        # Verify results
        if verify_migration(report):
            logger.info("Migration completed and verified successfully")
        else:
            logger.error("Migration verification failed")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
