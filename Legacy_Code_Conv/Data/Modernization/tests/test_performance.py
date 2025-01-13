"""
Performance tests for the database layer.
Tests connection pooling, query performance, and concurrent operations.
"""
import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import List
from ..core.database import Database, DatabaseConfig
from ..repositories.models import (
    User, Company, Location, PriceList, 
    PriceListItem, Role, UserRole
)
from ..repositories.user_repository import UserRepository
from ..repositories.company_repository import CompanyRepository
from ..repositories.price_repository import PriceRepository

async def create_test_data(company_repository: CompanyRepository) -> Company:
    """Create test data for performance testing."""
    company = await company_repository.create(
        name="Performance Test Company",
        code="PERF001",
        created_by="system",
        updated_by="system"
    )
    
    # Create locations
    tasks = []
    for i in range(100):
        tasks.append(
            company_repository.add_location(
                company_id=company.id,
                name=f"Location {i}",
                address_line1=f"{i} Test Street",
                city="Test City",
                state="TX",
                zip_code="12345",
                created_by="system"
            )
        )
    await asyncio.gather(*tasks)
    
    return company

@pytest.mark.asyncio
async def test_connection_pool_performance(database):
    """Test database connection pool performance."""
    async def execute_query():
        async with database.session() as session:
            await session.execute("SELECT 1")
    
    # Test concurrent connections
    start_time = time.time()
    tasks = [execute_query() for _ in range(50)]
    await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Should complete quickly with connection pooling
    assert end_time - start_time < 2.0

@pytest.mark.asyncio
async def test_bulk_insert_performance(database, company_repository):
    """Test bulk insert performance."""
    company = await create_test_data(company_repository)
    
    async with database.session() as session:
        # Create price list
        price_list = PriceList(
            company_id=company.id,
            name="Bulk Test Prices",
            code="BULK001",
            effective_date=datetime.utcnow(),
            created_by="system",
            updated_by="system"
        )
        session.add(price_list)
        await session.flush()
        
        # Bulk insert items
        start_time = time.time()
        items = [
            PriceListItem(
                price_list_id=price_list.id,
                item_code=f"ITEM{i}",
                description=f"Test Item {i}",
                unit_price=i * 100,
                created_by="system",
                updated_by="system"
            )
            for i in range(1000)
        ]
        session.add_all(items)
        await session.commit()
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 5.0

@pytest.mark.asyncio
async def test_query_performance(database, company_repository):
    """Test query performance with indexes."""
    company = await create_test_data(company_repository)
    
    # Test location query performance
    start_time = time.time()
    for _ in range(100):
        locations = await company_repository.get_locations(
            company_id=company.id,
            skip=0,
            limit=10
        )
        assert len(locations) == 10
    end_time = time.time()
    
    # Should be fast with proper indexing
    assert end_time - start_time < 2.0

@pytest.mark.asyncio
async def test_concurrent_updates(database, company_repository):
    """Test concurrent update performance."""
    company = await create_test_data(company_repository)
    
    async def update_location(location_id: int):
        await company_repository.update_location(
            location_id=location_id,
            updated_by="system",
            name=f"Updated Location {location_id}"
        )
    
    # Get location IDs
    locations = await company_repository.get_locations(company.id)
    location_ids = [loc.id for loc in locations[:20]]
    
    # Test concurrent updates
    start_time = time.time()
    tasks = [update_location(lid) for lid in location_ids]
    await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Should handle concurrent updates efficiently
    assert end_time - start_time < 3.0

@pytest.mark.asyncio
async def test_complex_query_performance(database):
    """Test performance of complex joins."""
    async with database.session() as session:
        # Complex query with multiple joins
        start_time = time.time()
        for _ in range(10):
            result = await session.execute("""
                SELECT 
                    u.username,
                    c.name as company_name,
                    r.name as role_name,
                    pl.name as price_list_name,
                    COUNT(pli.id) as item_count
                FROM users u
                JOIN companies c ON u.company_id = c.id
                LEFT JOIN user_roles ur ON u.id = ur.user_id
                LEFT JOIN roles r ON ur.role_id = r.id
                LEFT JOIN price_lists pl ON c.id = pl.company_id
                LEFT JOIN price_list_items pli ON pl.id = pli.price_list_id
                WHERE u.is_active = true
                GROUP BY u.username, c.name, r.name, pl.name
                LIMIT 100
            """)
            rows = result.fetchall()
        end_time = time.time()
        
        # Complex query should still be performant
        assert end_time - start_time < 2.0

@pytest.mark.asyncio
async def test_transaction_performance(database):
    """Test transaction performance under load."""
    async def run_transaction():
        async with database.session() as session:
            async with session.begin():
                # Simulate complex transaction
                company = Company(
                    name=f"Transaction Test {time.time()}",
                    code=f"TR{time.time()}",
                    created_by="system",
                    updated_by="system"
                )
                session.add(company)
                await session.flush()
                
                location = Location(
                    company_id=company.id,
                    name="Test Location",
                    address_line1="123 Test St",
                    city="Test City",
                    state="TX",
                    zip_code="12345",
                    created_by="system",
                    updated_by="system"
                )
                session.add(location)
    
    # Run multiple transactions concurrently
    start_time = time.time()
    tasks = [run_transaction() for _ in range(20)]
    await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Should handle concurrent transactions efficiently
    assert end_time - start_time < 4.0
