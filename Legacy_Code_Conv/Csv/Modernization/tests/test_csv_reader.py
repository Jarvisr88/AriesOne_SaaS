"""
Unit tests for CSVReader class
"""
import pytest
import pandas as pd
from pathlib import Path
import asyncio

from csv_reader import (
    CSVReader,
    ParseErrorAction,
    MissingFieldAction,
    MalformedCSVException,
    MissingFieldCSVException
)

def test_read_file_success(sample_csv):
    """Test successful file reading."""
    reader = CSVReader()
    df = reader.read_file(sample_csv)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    assert list(df.columns) == ['id', 'name', 'price', 'quantity']
    assert df['id'].iloc[0] == 1
    assert df['name'].iloc[0] == 'Item 1'
    
def test_read_file_malformed(malformed_csv):
    """Test handling of malformed CSV."""
    reader = CSVReader(parse_error_action=ParseErrorAction.SKIP_ROW)
    df = reader.read_file(malformed_csv)
    
    assert len(df) == 3  # One row should be skipped
    assert 'missing' not in df['price'].values
    
def test_read_file_malformed_raise(malformed_csv):
    """Test exception raising for malformed CSV."""
    reader = CSVReader(parse_error_action=ParseErrorAction.RAISE_EXCEPTION)
    with pytest.raises(MalformedCSVException):
        reader.read_file(malformed_csv)
        
def test_read_stream(large_csv):
    """Test streaming functionality."""
    reader = CSVReader(chunk_size=1000)
    chunks = list(reader.read_stream(large_csv))
    
    assert len(chunks) == 100  # 100k rows / 1000 chunk_size
    assert all(isinstance(chunk, pd.DataFrame) for chunk in chunks)
    assert sum(len(chunk) for chunk in chunks) == 100000
    
def test_read_empty_file(empty_csv):
    """Test reading empty CSV file."""
    reader = CSVReader()
    df = reader.read_file(empty_csv)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert list(df.columns) == ['id', 'name', 'price', 'quantity']
    
@pytest.mark.asyncio
async def test_read_file_async(sample_csv):
    """Test asynchronous file reading."""
    reader = CSVReader()
    df = await reader.read_file_async(sample_csv)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    
def test_error_handler(malformed_csv):
    """Test error handler functionality."""
    errors = []
    
    def error_handler(args):
        errors.append(args)
    
    reader = CSVReader(parse_error_action=ParseErrorAction.SKIP_ROW)
    reader.add_error_handler(error_handler)
    reader.read_file(malformed_csv)
    
    assert len(errors) > 0
    assert all(hasattr(error, 'row_number') for error in errors)
    
def test_memory_usage(large_csv):
    """Test memory usage during large file processing."""
    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    reader = CSVReader(chunk_size=1000)
    for chunk in reader.read_stream(large_csv):
        current_memory = process.memory_info().rss
        # Memory usage shouldn't grow significantly due to streaming
        assert current_memory - initial_memory < 50 * 1024 * 1024  # 50MB limit
        
def test_file_not_found():
    """Test handling of non-existent file."""
    reader = CSVReader()
    with pytest.raises(FileNotFoundError):
        reader.read_file('nonexistent.csv')
        
def test_encoding(test_data_dir):
    """Test different file encodings."""
    file_path = Path(test_data_dir) / "encoded.csv"
    content = "id,name\n1,测试\n2,テスト"
    file_path.write_text(content, encoding='utf-8')
    
    reader = CSVReader(encoding='utf-8')
    df = reader.read_file(file_path)
    assert df['name'].iloc[0] == '测试'
    assert df['name'].iloc[1] == 'テスト'
    
def test_concurrent_reads(sample_csv):
    """Test concurrent file reading."""
    reader = CSVReader()
    
    async def read_concurrent():
        tasks = [reader.read_file_async(sample_csv) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        return results
    
    results = asyncio.run(read_concurrent())
    assert len(results) == 5
    assert all(len(df) == 100 for df in results)
