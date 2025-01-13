"""
PostgreSQL data loader for migrating data from MySQL.
Handles loading and validation of data into PostgreSQL.
"""
import asyncio
from typing import List, Dict, Any
import logging
from datetime import datetime
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from ..repositories.models import (
    Base, Company, Location, User, Role,
    UserRole, PriceList, PriceListItem
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PostgresConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

class PostgresLoader:
    def __init__(self, config: PostgresConfig):
        self.config = config
        self.engine = None
        self.session_factory = None
        self.id_mappings = {
            'companies': {},
            'locations': {},
            'users': {},
            'roles': {},
            'price_lists': {}
        }

    async def connect(self):
        """Create database engine and session factory."""
        try:
            url = f"postgresql+asyncpg://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
            self.engine = create_async_engine(url, echo=True)
            self.session_factory = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
            logger.info("PostgreSQL connection established")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    async def close(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            logger.info("PostgreSQL connection closed")

    async def load_companies(self, companies: List[Dict[str, Any]]):
        """Load companies data."""
        async with self.session_factory() as session:
            for company in companies:
                mysql_id = company.pop('mysql_id')
                stmt = insert(Company).values(**company)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['code']
                )
                result = await session.execute(stmt)
                if result.rowcount > 0:
                    # Get the inserted company's ID
                    result = await session.execute(
                        "SELECT id FROM companies WHERE code = :code",
                        {'code': company['code']}
                    )
                    pg_id = result.scalar()
                    self.id_mappings['companies'][mysql_id] = pg_id
            
            await session.commit()
            logger.info(f"Loaded {len(companies)} companies")

    async def load_locations(self, locations: List[Dict[str, Any]]):
        """Load locations data."""
        async with self.session_factory() as session:
            for location in locations:
                mysql_id = location.pop('mysql_id')
                # Map company ID
                location['company_id'] = self.id_mappings['companies'][location['company_id']]
                
                stmt = insert(Location).values(**location)
                result = await session.execute(stmt)
                if result.rowcount > 0:
                    # Get the inserted location's ID
                    result = await session.execute(
                        """
                        SELECT id FROM locations 
                        WHERE company_id = :company_id 
                        AND name = :name
                        """,
                        {
                            'company_id': location['company_id'],
                            'name': location['name']
                        }
                    )
                    pg_id = result.scalar()
                    self.id_mappings['locations'][mysql_id] = pg_id
            
            await session.commit()
            logger.info(f"Loaded {len(locations)} locations")

    async def load_users(self, users: List[Dict[str, Any]]):
        """Load users data."""
        async with self.session_factory() as session:
            for user in users:
                mysql_id = user.pop('mysql_id')
                # Map company ID
                user['company_id'] = self.id_mappings['companies'][user['company_id']]
                
                stmt = insert(User).values(**user)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['username']
                )
                result = await session.execute(stmt)
                if result.rowcount > 0:
                    # Get the inserted user's ID
                    result = await session.execute(
                        "SELECT id FROM users WHERE username = :username",
                        {'username': user['username']}
                    )
                    pg_id = result.scalar()
                    self.id_mappings['users'][mysql_id] = pg_id
            
            await session.commit()
            logger.info(f"Loaded {len(users)} users")

    async def load_roles(self, roles: List[Dict[str, Any]]):
        """Load roles data."""
        async with self.session_factory() as session:
            for role in roles:
                mysql_id = role.pop('mysql_id')
                stmt = insert(Role).values(**role)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['name']
                )
                result = await session.execute(stmt)
                if result.rowcount > 0:
                    # Get the inserted role's ID
                    result = await session.execute(
                        "SELECT id FROM roles WHERE name = :name",
                        {'name': role['name']}
                    )
                    pg_id = result.scalar()
                    self.id_mappings['roles'][mysql_id] = pg_id
            
            await session.commit()
            logger.info(f"Loaded {len(roles)} roles")

    async def load_user_roles(self, user_roles: List[Dict[str, Any]]):
        """Load user roles data."""
        async with self.session_factory() as session:
            for user_role in user_roles:
                # Map user and role IDs
                user_role['user_id'] = self.id_mappings['users'][user_role['user_id']]
                user_role['role_id'] = self.id_mappings['roles'][user_role['role_id']]
                
                stmt = insert(UserRole).values(**user_role)
                await session.execute(stmt)
            
            await session.commit()
            logger.info(f"Loaded {len(user_roles)} user roles")

    async def load_price_lists(self, price_lists: List[Dict[str, Any]]):
        """Load price lists data."""
        async with self.session_factory() as session:
            for price_list in price_lists:
                mysql_id = price_list.pop('mysql_id')
                # Map company ID
                price_list['company_id'] = self.id_mappings['companies'][price_list['company_id']]
                
                stmt = insert(PriceList).values(**price_list)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['code']
                )
                result = await session.execute(stmt)
                if result.rowcount > 0:
                    # Get the inserted price list's ID
                    result = await session.execute(
                        "SELECT id FROM price_lists WHERE code = :code",
                        {'code': price_list['code']}
                    )
                    pg_id = result.scalar()
                    self.id_mappings['price_lists'][mysql_id] = pg_id
            
            await session.commit()
            logger.info(f"Loaded {len(price_lists)} price lists")

    async def load_price_list_items(self, items: List[Dict[str, Any]]):
        """Load price list items data."""
        async with self.session_factory() as session:
            for item in items:
                # Map price list ID
                item['price_list_id'] = self.id_mappings['price_lists'][item['price_list_id']]
                
                stmt = insert(PriceListItem).values(**item)
                await session.execute(stmt)
            
            await session.commit()
            logger.info(f"Loaded {len(items)} price list items")

    async def load_all(self, data: Dict[str, List[Dict[str, Any]]]):
        """Load all data into PostgreSQL database."""
        try:
            await self.connect()
            
            # Load data in order of dependencies
            await self.load_companies(data['companies'])
            await self.load_locations(data['locations'])
            await self.load_users(data['users'])
            await self.load_roles(data['roles'])
            await self.load_user_roles(data['user_roles'])
            await self.load_price_lists(data['price_lists'])
            await self.load_price_list_items(data['price_list_items'])
            
            logger.info("Data loading completed successfully")
        finally:
            await self.close()

async def main():
    """Main function for testing."""
    config = PostgresConfig(
        host="localhost",
        port=5432,
        user="postgres",
        password="your_password",
        database="new_db"
    )
    
    loader = PostgresLoader(config)
    # Test with sample data
    sample_data = {
        'companies': [],
        'locations': [],
        'users': [],
        'roles': [],
        'user_roles': [],
        'price_lists': [],
        'price_list_items': []
    }
    await loader.load_all(sample_data)

if __name__ == "__main__":
    asyncio.run(main())
