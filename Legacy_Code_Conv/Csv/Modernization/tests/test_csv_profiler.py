"""
Unit tests for CSVProfiler class
"""
import pytest
import time
from datetime import datetime
import pandas as pd
from pathlib import Path

from csv_profiler import CSVProfiler, ProfileMetrics

def test_basic_profiling():
    """Test basic profiling functionality."""
    profiler = CSVProfiler()
    
    # Start operation
    profiler.start_operation('test_op')
    
    # Simulate work
    time.sleep(0.1)
    profiler.record_rows(100)
    
    # End operation
    profiler.end_operation()
    
    # Check metrics
    metrics = profiler.get_metrics('test_op')
    assert isinstance(metrics, ProfileMetrics)
    assert metrics.operation == 'test_op'
    assert metrics.rows_processed == 100
    assert metrics.duration_seconds >= 0.1
    
def test_cache_metrics():
    """Test cache hit/miss tracking."""
    profiler = CSVProfiler()
    profiler.start_operation('cache_test')
    
    # Record some cache events
    profiler.record_cache_hit()
    profiler.record_cache_hit()
    profiler.record_cache_miss()
    
    profiler.end_operation()
    
    metrics = profiler.get_metrics('cache_test')
    assert metrics.cache_hits == 2
    assert metrics.cache_misses == 1
    assert metrics.cache_hit_ratio == 2/3
    
def test_error_tracking():
    """Test error tracking."""
    profiler = CSVProfiler()
    profiler.start_operation('error_test')
    
    # Record some errors
    profiler.record_error()
    profiler.record_error()
    
    profiler.end_operation()
    
    metrics = profiler.get_metrics('error_test')
    assert metrics.errors_encountered == 2
    
def test_performance_metrics():
    """Test performance metrics calculation."""
    profiler = CSVProfiler()
    profiler.start_operation('perf_test')
    
    # Simulate processing
    time.sleep(0.1)
    profiler.record_rows(1000)
    
    profiler.end_operation()
    
    metrics = profiler.get_metrics('perf_test')
    assert metrics.rows_per_second > 0
    assert metrics.memory_usage > 0
    assert metrics.cpu_percent >= 0
    
def test_multiple_operations():
    """Test tracking multiple operations."""
    profiler = CSVProfiler()
    
    # First operation
    profiler.start_operation('op1')
    profiler.record_rows(100)
    profiler.end_operation()
    
    # Second operation
    profiler.start_operation('op2')
    profiler.record_rows(200)
    profiler.end_operation()
    
    assert len(profiler.metrics) == 2
    assert profiler.get_metrics('op1').rows_processed == 100
    assert profiler.get_metrics('op2').rows_processed == 200
    
def test_report_generation(tmp_path):
    """Test performance report generation."""
    profiler = CSVProfiler()
    
    # Record some operations
    for i in range(3):
        profiler.start_operation(f'op{i}')
        profiler.record_rows(100 * (i + 1))
        profiler.end_operation()
    
    # Generate report
    report_path = tmp_path / "report.csv"
    df = profiler.generate_report(report_path)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert report_path.exists()
    
def test_concurrent_operations():
    """Test handling of concurrent operations."""
    profiler = CSVProfiler()
    
    # Start operation without ending previous
    profiler.start_operation('op1')
    profiler.start_operation('op2')  # Should handle gracefully
    
    profiler.record_rows(100)
    profiler.end_operation()
    
    assert 'op2' in profiler.metrics
    assert profiler.get_metrics('op2').rows_processed == 100
    
def test_metrics_timestamps():
    """Test operation timestamp tracking."""
    profiler = CSVProfiler()
    
    start_time = datetime.now()
    profiler.start_operation('time_test')
    time.sleep(0.1)
    profiler.end_operation()
    end_time = datetime.now()
    
    metrics = profiler.get_metrics('time_test')
    assert start_time <= metrics.start_time <= end_time
    assert start_time <= metrics.end_time <= end_time
    
def test_memory_tracking():
    """Test memory usage tracking."""
    profiler = CSVProfiler()
    profiler.start_operation('memory_test')
    
    # Allocate some memory
    large_list = [0] * 1000000
    
    profiler.end_operation()
    
    metrics = profiler.get_metrics('memory_test')
    assert metrics.memory_usage > 0
    
    # Cleanup
    del large_list
    
def test_zero_duration_operation():
    """Test handling of very quick operations."""
    profiler = CSVProfiler()
    
    profiler.start_operation('quick')
    profiler.record_rows(100)
    profiler.end_operation()
    
    metrics = profiler.get_metrics('quick')
    assert metrics.duration_seconds >= 0
    assert metrics.rows_per_second >= 0
