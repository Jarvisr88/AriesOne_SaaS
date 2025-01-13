"""
Unit tests for CachedCSVReader class
"""
import pytest
import pandas as pd
from datetime import timedelta
import time
import asyncio

from cached_csv_reader import CachedCSVReader
from csv_reader import ParseErrorAction

def test_cache_hit(sample_csv):
    """Test cache hit functionality."""
    reader = CachedCSVReader(cache_duration=timedelta(minutes=5))
    
    # First read - cache miss
    df1 = reader.read_file(sample_csv)
    assert len(df1) == 100
    
    # Second read - should hit cache
    df2 = reader.read_file(sample_csv)
    assert len(df2) == 100
    assert df1.equals(df2)
    
def test_cache_expiration(sample_csv):
    """Test cache expiration."""
    reader = CachedCSVReader(cache_duration=timedelta(seconds=1))
    
    # First read
    df1 = reader.read_file(sample_csv)
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Second read - should miss cache
    df2 = reader.read_file(sample_csv)
    
    assert len(df1) == len(df2)
    assert df1.equals(df2)
    
def test_cache_size_limit(test_data_dir):
    """Test cache size limiting."""
    reader = CachedCSVReader(max_cache_size=2)
    
    # Create multiple test files
    files = []
    for i in range(3):
        file_path = test_data_dir / f"test{i}.csv"
        pd.DataFrame({'data': range(10)}).to_csv(file_path)
        files.append(file_path)
    
    # Read all files
    for file in files:
        reader.read_file(file)
    
    # Verify cache size
    assert len(reader._cache) <= 2
    
def test_stream_caching(large_csv):
    """Test caching with streaming."""
    reader = CachedCSVReader(chunk_size=1000)
    
    # First read - cache miss
    chunks1 = list(reader.read_stream(large_csv))
    total_rows1 = sum(len(chunk) for chunk in chunks1)
    
    # Second read - cache hit
    chunks2 = list(reader.read_stream(large_csv))
    total_rows2 = sum(len(chunk) for chunk in chunks2)
    
    assert total_rows1 == total_rows2 == 100000
    
@pytest.mark.asyncio
async def test_async_cache(sample_csv):
    """Test asynchronous caching."""
    reader = CachedCSVReader()
    
    # First read
    df1 = await reader.read_file_async(sample_csv)
    
    # Second read - should hit cache
    df2 = await reader.read_file_async(sample_csv)
    
    assert df1.equals(df2)
    
def test_cache_with_error_handling(malformed_csv):
    """Test caching with error handling."""
    reader = CachedCSVReader(
        parse_error_action=ParseErrorAction.SKIP_ROW,
        cache_duration=timedelta(minutes=5)
    )
    
    # First read
    df1 = reader.read_file(malformed_csv)
    
    # Second read - should hit cache
    df2 = reader.read_file(malformed_csv)
    
    assert df1.equals(df2)
    assert len(df1) < 4  # Some rows should be skipped
    
def test_cache_cleanup(test_data_dir):
    """Test cache cleanup on expiration."""
    reader = CachedCSVReader(cache_duration=timedelta(seconds=1))
    
    # Create and read multiple files
    files = []
    for i in range(3):
        file_path = test_data_dir / f"cleanup{i}.csv"
        pd.DataFrame({'data': range(10)}).to_csv(file_path)
        files.append(file_path)
        reader.read_file(file_path)
    
    assert len(reader._cache) == 3
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Trigger cleanup by reading new file
    new_file = test_data_dir / "new.csv"
    pd.DataFrame({'data': range(10)}).to_csv(new_file)
    reader.read_file(new_file)
    
    # Verify old cache entries are removed
    assert len(reader._cache) == 1
    
def test_concurrent_cache_access(sample_csv):
    """Test concurrent cache access."""
    reader = CachedCSVReader()
    
    async def read_concurrent():
        tasks = [reader.read_file_async(sample_csv) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        return results
    
    results = asyncio.run(read_concurrent())
    
    # All results should be identical
    first_df = results[0]
    assert all(df.equals(first_df) for df in results[1:])
    
def test_memory_usage_with_cache(large_csv):
    """Test memory usage with caching enabled."""
    import psutil
    process = psutil.Process()
    
    reader = CachedCSVReader(chunk_size=1000)
    
    # First read
    initial_memory = process.memory_info().rss
    for chunk in reader.read_stream(large_csv):
        current_memory = process.memory_info().rss
        # Memory should stay within reasonable limits
        assert current_memory - initial_memory < 100 * 1024 * 1024  # 100MB limit
    
    # Second read (cached)
    cached_memory = process.memory_info().rss
    for chunk in reader.read_stream(large_csv):
        current_memory = process.memory_info().rss
        # Memory shouldn't grow significantly when reading from cache
        assert current_memory - cached_memory < 10 * 1024 * 1024  # 10MB limit
