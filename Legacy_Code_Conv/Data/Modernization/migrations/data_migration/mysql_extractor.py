"""
MySQL data extractor for migrating data from legacy database.
Handles extraction and transformation of data from MySQL to PostgreSQL format.
"""
import asyncio
import aiomysql
from typing import List, Dict, Any
import logging
from datetime import datetime
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = 'utf8mb4'

class MySQLExtractor:
    def __init__(self, config: MySQLConfig):
        self.config = config
        self.pool = None

    async def connect(self):
        """Create connection pool."""
        try:
            self.pool = await aiomysql.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                db=self.config.database,
                charset=self.config.charset,
                cursorclass=aiomysql.DictCursor,
                autocommit=True
            )
            logger.info("MySQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create MySQL connection pool: {e}")
            raise

    async def close(self):
        """Close connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("MySQL connection pool closed")

    async def extract_companies(self) -> List[Dict[str, Any]]:
        """Extract companies data."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT 
                        id as mysql_id,
                        name,
                        code,
                        is_active,
                        created_at,
                        updated_at,
                        created_by,
                        updated_by
                    FROM companies
                    ORDER BY id
                """)
                companies = await cursor.fetchall()
                logger.info(f"Extracted {len(companies)} companies")
                return companies

    async def extract_locations(self) -> List[Dict[str, Any]]:
        """Extract locations data."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT 
                        id as mysql_id,
                        company_id,
                        name,
                        address_line1,
                        address_line2,
                        city,
                        state,
                        zip_code,
                        is_active,
                        created_at,
                        updated_at,
                        created_by,
                        updated_by
                    FROM locations
                    ORDER BY id
                """)
                locations = await cursor.fetchall()
                logger.info(f"Extracted {len(locations)} locations")
                return locations

    async def extract_users(self) -> List[Dict[str, Any]]:
        """Extract users data."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT 
                        id as mysql_id,
                        username,
                        email,
                        password_hash,
                        is_active,
                        last_login,
                        company_id,
                        created_at,
                        updated_at,
                        created_by,
                        updated_by
                    FROM users
                    ORDER BY id
                """)
                users = await cursor.fetchall()
                logger.info(f"Extracted {len(users)} users")
                return users

    async def extract_roles(self) -> List[Dict[str, Any]]:
        """Extract roles data."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT 
                        id as mysql_id,
                        name,
                        description,
                        created_at,
                        updated_at,
                        created_by,
                        updated_by
                    FROM roles
                    ORDER BY id
                """)
                roles = await cursor.fetchall()
                logger.info(f"Extracted {len(roles)} roles")
                return roles

    async def extract_user_roles(self) -> List[Dict[str, Any]]:
        """Extract user roles data."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT 
                        id as mysql_id,
                        user_id,
                        role_id,
                        created_at,
                        updated_at,
                        created_by,
                        updated_by
                    FROM user_roles
                    ORDER BY id
                """)
                user_roles = await cursor.fetchall()
                logger.info(f"Extracted {len(user_roles)} user roles")
                return user_roles

    async def extract_price_lists(self) -> List[Dict[str, Any]]:
        """Extract price lists data."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT 
                        id as mysql_id,
                        company_id,
                        name,
                        code,
                        is_active,
                        effective_date,
                        expiration_date,
                        created_at,
                        updated_at,
                        created_by,
                        updated_by
                    FROM price_lists
                    ORDER BY id
                """)
                price_lists = await cursor.fetchall()
                logger.info(f"Extracted {len(price_lists)} price lists")
                return price_lists

    async def extract_price_list_items(self) -> List[Dict[str, Any]]:
        """Extract price list items data."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT 
                        id as mysql_id,
                        price_list_id,
                        item_code,
                        description,
                        unit_price,
                        is_active,
                        created_at,
                        updated_at,
                        created_by,
                        updated_by
                    FROM price_list_items
                    ORDER BY id
                """)
                items = await cursor.fetchall()
                logger.info(f"Extracted {len(items)} price list items")
                return items

    async def extract_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract all data from MySQL database."""
        try:
            await self.connect()
            data = {
                'companies': await self.extract_companies(),
                'locations': await self.extract_locations(),
                'users': await self.extract_users(),
                'roles': await self.extract_roles(),
                'user_roles': await self.extract_user_roles(),
                'price_lists': await self.extract_price_lists(),
                'price_list_items': await self.extract_price_list_items()
            }
            
            # Save extracted data to JSON for verification
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(f'extracted_data_{timestamp}.json', 'w') as f:
                json.dump(data, f, default=str, indent=2)
            
            logger.info("Data extraction completed successfully")
            return data
        finally:
            await self.close()

async def main():
    """Main function for testing."""
    config = MySQLConfig(
        host="localhost",
        port=3306,
        user="root",
        password="your_password",
        database="legacy_db"
    )
    
    extractor = MySQLExtractor(config)
    await extractor.extract_all()

if __name__ == "__main__":
    asyncio.run(main())
