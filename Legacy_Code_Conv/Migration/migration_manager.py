"""
Database migration manager module.
"""
from typing import Optional, List, Dict, Any
import pyodbc
import psycopg2
from psycopg2.extras import DictCursor
import logging
from datetime import datetime
from pathlib import Path
import json
import hashlib
from ..Config.config_manager import ConfigManager
from ..core.database import Database

logger = logging.getLogger(__name__)

class MigrationManager:
    """Handle database migration from ODBC to PostgreSQL."""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        migration_dir: str,
        batch_size: int = 1000
    ):
        self.config_manager = config_manager
        self.migration_dir = Path(migration_dir)
        self.batch_size = batch_size
        self.archive_dir = self.migration_dir / 'archive'
        self.checksum_file = self.migration_dir / 'checksums.json'
        
        # Create directories
        self.migration_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def _get_odbc_connection(self, odbc_string: str) -> pyodbc.Connection:
        """Create ODBC connection."""
        try:
            return pyodbc.connect(odbc_string)
        except Exception as e:
            logger.error(f'Failed to connect to ODBC source: {str(e)}')
            raise

    def _get_postgres_connection(self, env_name: str = "development"):
        """Create PostgreSQL connection."""
        try:
            config = self.config_manager.load_config(env_name)
            return Database(config)
        except Exception as e:
            logger.error(f'Failed to connect to PostgreSQL: {str(e)}')
            raise

    async def _get_table_schema(
        self,
        odbc_conn: pyodbc.Connection,
        table_name: str
    ) -> List[Dict[str, Any]]:
        """Get table schema from ODBC source."""
        cursor = odbc_conn.cursor()
        columns = []
        
        try:
            cursor.columns(table=table_name)
            for row in cursor.fetchall():
                columns.append({
                    'name': row.COLUMN_NAME,
                    'type': row.TYPE_NAME,
                    'nullable': row.NULLABLE == 1,
                    'length': row.COLUMN_SIZE,
                    'precision': row.DECIMAL_DIGITS
                })
            return columns
        finally:
            cursor.close()

    def _map_data_type(self, odbc_type: str, length: int, precision: int) -> str:
        """Map ODBC data type to PostgreSQL."""
        type_map = {
            'VARCHAR': lambda l, p: f'VARCHAR({l})',
            'NVARCHAR': lambda l, p: f'VARCHAR({l})',
            'CHAR': lambda l, p: f'CHAR({l})',
            'TEXT': lambda l, p: 'TEXT',
            'INT': lambda l, p: 'INTEGER',
            'SMALLINT': lambda l, p: 'SMALLINT',
            'BIGINT': lambda l, p: 'BIGINT',
            'DECIMAL': lambda l, p: f'DECIMAL({l},{p})',
            'NUMERIC': lambda l, p: f'NUMERIC({l},{p})',
            'FLOAT': lambda l, p: 'DOUBLE PRECISION',
            'DATETIME': lambda l, p: 'TIMESTAMP',
            'DATE': lambda l, p: 'DATE',
            'TIME': lambda l, p: 'TIME',
            'BIT': lambda l, p: 'BOOLEAN',
            'BINARY': lambda l, p: 'BYTEA',
            'VARBINARY': lambda l, p: 'BYTEA'
        }
        
        type_func = type_map.get(odbc_type.upper())
        if type_func:
            return type_func(length, precision)
        else:
            logger.warning(f'Unknown data type: {odbc_type}, defaulting to TEXT')
            return 'TEXT'

    def _generate_create_table_sql(
        self,
        table_name: str,
        columns: List[Dict[str, Any]]
    ) -> str:
        """Generate CREATE TABLE SQL for PostgreSQL."""
        column_defs = []
        for col in columns:
            nullable = 'NULL' if col['nullable'] else 'NOT NULL'
            pg_type = self._map_data_type(
                col['type'],
                col['length'],
                col['precision']
            )
            column_defs.append(
                f'"{col["name"]}" {pg_type} {nullable}'
            )
        
        return f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            {','.join(column_defs)}
        );
        '''

    async def _calculate_checksum(self, data: List[Dict[str, Any]]) -> str:
        """Calculate checksum for data verification."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    async def _save_checksum(
        self,
        table_name: str,
        checksum: str
    ):
        """Save data checksum."""
        checksums = {}
        if self.checksum_file.exists():
            with open(self.checksum_file, 'r') as f:
                checksums = json.load(f)
        
        checksums[table_name] = {
            'checksum': checksum,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.checksum_file, 'w') as f:
            json.dump(checksums, f, indent=2)

    async def _verify_data(
        self,
        table_name: str,
        source_data: List[Dict[str, Any]],
        target_db: Database
    ) -> bool:
        """Verify migrated data integrity."""
        source_checksum = await self._calculate_checksum(source_data)
        
        # Get migrated data
        query = f'SELECT * FROM "{table_name}" ORDER BY 1'
        target_data = await target_db.fetch_all(query)
        target_checksum = await self._calculate_checksum(target_data)
        
        return source_checksum == target_checksum

    async def migrate_table(
        self,
        odbc_string: str,
        table_name: str,
        env_name: str = "development"
    ):
        """Migrate single table from ODBC to PostgreSQL."""
        logger.info(f'Starting migration for table: {table_name}')
        
        # Connect to source and target
        odbc_conn = self._get_odbc_connection(odbc_string)
        target_db = self._get_postgres_connection(env_name)
        
        try:
            # Get table schema
            schema = await self._get_table_schema(odbc_conn, table_name)
            
            # Create table in PostgreSQL
            create_sql = self._generate_create_table_sql(table_name, schema)
            await target_db.execute(create_sql)
            
            # Prepare column list
            columns = [col['name'] for col in schema]
            placeholders = ','.join(['%s'] * len(columns))
            
            # Migrate data in batches
            offset = 0
            while True:
                # Get batch from source
                cursor = odbc_conn.cursor()
                cursor.execute(
                    f'SELECT {",".join(columns)} FROM {table_name} '
                    f'ORDER BY 1 OFFSET {offset} ROWS '
                    f'FETCH NEXT {self.batch_size} ROWS ONLY'
                )
                batch = cursor.fetchall()
                cursor.close()
                
                if not batch:
                    break
                
                # Insert batch into target
                insert_sql = f'''
                INSERT INTO "{table_name}" ({','.join(f'"{c}"' for c in columns)})
                VALUES ({placeholders})
                '''
                await target_db.execute_many(insert_sql, batch)
                
                offset += len(batch)
                logger.info(f'Migrated {offset} rows from {table_name}')
            
            # Verify data
            source_data = []
            cursor = odbc_conn.cursor()
            cursor.execute(f'SELECT * FROM {table_name} ORDER BY 1')
            for row in cursor.fetchall():
                source_data.append(dict(zip(columns, row)))
            cursor.close()
            
            if await self._verify_data(table_name, source_data, target_db):
                logger.info(f'Data verification successful for {table_name}')
                
                # Save checksum
                checksum = await self._calculate_checksum(source_data)
                await self._save_checksum(table_name, checksum)
                
                # Archive source data
                archive_file = self.archive_dir / f'{table_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                with open(archive_file, 'w') as f:
                    json.dump(source_data, f, indent=2)
                
                logger.info(f'Source data archived: {archive_file}')
            else:
                raise Exception(f'Data verification failed for {table_name}')
            
        finally:
            odbc_conn.close()
            await target_db.close()

    async def migrate_database(
        self,
        odbc_string: str,
        tables: List[str],
        env_name: str = "development"
    ):
        """Migrate multiple tables from ODBC to PostgreSQL."""
        for table in tables:
            await self.migrate_table(odbc_string, table, env_name)
            
        logger.info('Database migration completed successfully')
