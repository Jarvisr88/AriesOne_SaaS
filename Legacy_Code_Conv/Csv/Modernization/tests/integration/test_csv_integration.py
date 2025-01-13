"""
Integration tests for CSV module components
"""
import pytest
import pandas as pd
import asyncio
import tempfile
from pathlib import Path
import psutil
import time
import threading
from queue import Queue

from csv_reader import CSVReader, ParseErrorAction
from cached_csv_reader import CachedCSVReader
from csv_validator import CSVValidator, ValidationRule, not_empty, is_numeric
from csv_profiler import CSVProfiler

class TestCSVIntegration:
    @pytest.fixture
    def setup_components(self):
        """Set up CSV components for integration testing."""
        validator = CSVValidator()
        validator.add_rule(ValidationRule('id', is_numeric, 'ID must be numeric'))
        validator.add_rule(ValidationRule('name', not_empty, 'Name cannot be empty'))
        
        profiler = CSVProfiler()
        reader = CSVReader(validator=validator, profiler=profiler)
        cached_reader = CachedCSVReader(validator=validator, profiler=profiler)
        
        return reader, cached_reader, validator, profiler
    
    def test_end_to_end_processing(self, setup_components, sample_csv):
        """Test end-to-end CSV processing with all components."""
        reader, cached_reader, validator, profiler = setup_components
        
        # First read with validation and profiling
        profiler.start_operation('first_read')
        df1 = reader.read_file(sample_csv)
        profiler.end_operation()
        
        # Second read using cache
        profiler.start_operation('cached_read')
        df2 = cached_reader.read_file(sample_csv)
        profiler.end_operation()
        
        # Verify results
        assert df1.equals(df2)
        assert profiler.get_metrics('first_read').rows_processed == len(df1)
        assert profiler.get_metrics('cached_read').cache_hits > 0
        
    def test_concurrent_file_operations(self, setup_components, test_data_dir):
        """Test concurrent file operations with multiple components."""
        reader, cached_reader, validator, profiler = setup_components
        results_queue = Queue()
        errors_queue = Queue()
        
        def process_file(file_path, reader_instance):
            try:
                df = reader_instance.read_file(file_path)
                results_queue.put(len(df))
            except Exception as e:
                errors_queue.put(e)
        
        # Create test files
        files = []
        for i in range(5):
            file_path = Path(test_data_dir) / f"concurrent_{i}.csv"
            pd.DataFrame({
                'id': range(100),
                'name': [f'Item {j}' for j in range(100)]
            }).to_csv(file_path, index=False)
            files.append(file_path)
        
        # Start concurrent operations
        threads = []
        for file_path in files:
            thread = threading.Thread(
                target=process_file,
                args=(file_path, cached_reader)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        assert errors_queue.empty()
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        assert all(r == 100 for r in results)
        
    @pytest.mark.asyncio
    async def test_async_integration(self, setup_components, large_csv):
        """Test asynchronous operations across components."""
        reader, cached_reader, validator, profiler = setup_components
        
        async def process_chunk(chunk):
            await asyncio.sleep(0.01)  # Simulate async processing
            return len(chunk)
        
        total_rows = 0
        async for chunk in reader.read_stream_async(large_csv):
            chunk_rows = await process_chunk(chunk)
            total_rows += chunk_rows
        
        assert total_rows == 100000  # Known size of large_csv
        
    def test_error_propagation(self, setup_components, malformed_csv):
        """Test error handling and propagation between components."""
        reader, cached_reader, validator, profiler = setup_components
        errors = []
        
        def error_handler(error):
            errors.append(error)
        
        reader.add_error_handler(error_handler)
        validator.add_error_handler(error_handler)
        
        df = reader.read_file(malformed_csv)
        
        assert len(errors) > 0
        assert all(hasattr(e, 'row_number') for e in errors)
        
    def test_memory_management(self, setup_components, large_csv):
        """Test memory management across components with large files."""
        reader, cached_reader, validator, profiler = setup_components
        process = psutil.Process()
        
        def monitor_memory():
            return process.memory_info().rss
        
        initial_memory = monitor_memory()
        
        # Process large file in chunks
        chunk_sizes = []
        for chunk in reader.read_stream(large_csv):
            chunk_sizes.append(len(chunk))
            current_memory = monitor_memory()
            # Memory shouldn't grow unbounded
            assert current_memory - initial_memory < 100 * 1024 * 1024  # 100MB limit
        
        assert sum(chunk_sizes) == 100000
        
    def test_performance_metrics(self, setup_components, sample_csv):
        """Test performance metrics collection across components."""
        reader, cached_reader, validator, profiler = setup_components
        
        # First read
        profiler.start_operation('uncached')
        df1 = reader.read_file(sample_csv)
        profiler.end_operation()
        
        # Cached read
        profiler.start_operation('cached')
        df2 = cached_reader.read_file(sample_csv)
        profiler.end_operation()
        
        uncached_metrics = profiler.get_metrics('uncached')
        cached_metrics = profiler.get_metrics('cached')
        
        # Cached operation should be faster
        assert cached_metrics.duration_seconds < uncached_metrics.duration_seconds
        
    def test_data_consistency(self, setup_components, test_data_dir):
        """Test data consistency across different reading methods."""
        reader, cached_reader, validator, profiler = setup_components
        
        # Create test file with known content
        file_path = Path(test_data_dir) / "consistency.csv"
        test_data = pd.DataFrame({
            'id': range(1000),
            'name': [f'Item {i}' for i in range(1000)]
        })
        test_data.to_csv(file_path, index=False)
        
        # Read data in different ways
        df_full = reader.read_file(file_path)
        df_chunks = pd.concat(list(reader.read_stream(file_path)))
        df_cached = cached_reader.read_file(file_path)
        
        # Verify consistency
        assert df_full.equals(test_data)
        assert df_chunks.equals(test_data)
        assert df_cached.equals(test_data)
