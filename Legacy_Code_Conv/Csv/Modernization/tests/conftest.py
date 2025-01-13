"""
AriesOne CSV Module Test Configuration
"""
import pytest
from pathlib import Path
import pandas as pd
import tempfile
import shutil
import os

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_csv(test_data_dir):
    """Create sample CSV file for testing."""
    file_path = Path(test_data_dir) / "sample.csv"
    data = pd.DataFrame({
        'id': range(1, 101),
        'name': [f'Item {i}' for i in range(1, 101)],
        'price': [i * 1.5 for i in range(1, 101)],
        'quantity': [i % 10 for i in range(1, 101)]
    })
    data.to_csv(file_path, index=False)
    return file_path

@pytest.fixture
def malformed_csv(test_data_dir):
    """Create malformed CSV file for testing."""
    file_path = Path(test_data_dir) / "malformed.csv"
    content = """id,name,price,quantity
1,Item 1,1.5,1
2,Item 2,3.0,invalid
3,Item 3,4.5,3
4,Item 4,missing,4"""
    file_path.write_text(content)
    return file_path

@pytest.fixture
def large_csv(test_data_dir):
    """Create large CSV file for performance testing."""
    file_path = Path(test_data_dir) / "large.csv"
    rows = []
    for i in range(100000):
        rows.append({
            'id': i,
            'name': f'Item {i}',
            'price': i * 1.5,
            'quantity': i % 100
        })
    pd.DataFrame(rows).to_csv(file_path, index=False)
    return file_path

@pytest.fixture
def empty_csv(test_data_dir):
    """Create empty CSV file for testing."""
    file_path = Path(test_data_dir) / "empty.csv"
    pd.DataFrame(columns=['id', 'name', 'price', 'quantity']).to_csv(file_path, index=False)
    return file_path
