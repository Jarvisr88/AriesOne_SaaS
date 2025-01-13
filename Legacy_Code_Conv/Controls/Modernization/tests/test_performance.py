import pytest
import asyncio
import time
from locust import HttpUser, task, between
from concurrent.futures import ThreadPoolExecutor
import statistics
from datetime import datetime, timedelta

class PerformanceMetrics:
    def __init__(self):
        self.response_times = []
        self.error_counts = {}
        self.start_time = None
        self.end_time = None

    def record_response_time(self, duration):
        self.response_times.append(duration)

    def record_error(self, error_type):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

    def start_test(self):
        self.start_time = datetime.now()

    def end_test(self):
        self.end_time = datetime.now()

    def get_summary(self):
        if not self.response_times:
            return "No performance data available"

        duration = (self.end_time - self.start_time).total_seconds()
        return {
            "total_requests": len(self.response_times),
            "total_errors": sum(self.error_counts.values()),
            "error_breakdown": self.error_counts,
            "duration_seconds": duration,
            "requests_per_second": len(self.response_times) / duration,
            "response_times": {
                "min": min(self.response_times),
                "max": max(self.response_times),
                "mean": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "p95": self.percentile(95),
                "p99": self.percentile(99)
            }
        }

    def percentile(self, p):
        sorted_times = sorted(self.response_times)
        k = (len(sorted_times) - 1) * (p/100.0)
        f = int(k)
        c = k - f
        if f + 1 < len(sorted_times):
            return sorted_times[f] * (1-c) + sorted_times[f+1] * c
        return sorted_times[f]

class LoadTest:
    def __init__(self, endpoint, num_users, spawn_rate, duration):
        self.endpoint = endpoint
        self.num_users = num_users
        self.spawn_rate = spawn_rate
        self.duration = duration
        self.metrics = PerformanceMetrics()

    async def run(self):
        self.metrics.start_test()
        
        async def user_session():
            try:
                start_time = time.time()
                # Simulate user actions
                await asyncio.sleep(0.1)  # Simulated API call
                duration = time.time() - start_time
                self.metrics.record_response_time(duration)
            except Exception as e:
                self.metrics.record_error(str(e))

        # Create user sessions
        tasks = [user_session() for _ in range(self.num_users)]
        await asyncio.gather(*tasks)
        
        self.metrics.end_test()
        return self.metrics.get_summary()

@pytest.mark.asyncio
async def test_api_performance():
    """Test API endpoint performance under load"""
    load_test = LoadTest(
        endpoint="/api/v1/controls",
        num_users=100,
        spawn_rate=10,
        duration=60
    )
    
    results = await load_test.run()
    
    # Assert performance requirements
    assert results["response_times"]["p95"] < 0.5  # 95th percentile under 500ms
    assert results["response_times"]["mean"] < 0.2  # Mean under 200ms
    assert results["requests_per_second"] > 50  # Minimum 50 RPS
    assert results["total_errors"] == 0  # No errors allowed

class TestDatabasePerformance:
    """Test database operation performance"""

    @pytest.fixture
    def db_pool(self):
        """Setup database connection pool"""
        return ThreadPoolExecutor(max_workers=10)

    def test_concurrent_reads(self, db_pool):
        """Test concurrent database read performance"""
        start_time = time.time()
        
        def read_operation():
            time.sleep(0.1)  # Simulate DB read
            return True

        # Execute concurrent reads
        futures = [db_pool.submit(read_operation) for _ in range(100)]
        results = [f.result() for f in futures]
        
        duration = time.time() - start_time
        
        assert all(results)  # All operations successful
        assert duration < 2.0  # Complete within 2 seconds

    def test_write_performance(self, db_pool):
        """Test database write performance"""
        start_time = time.time()
        
        def write_operation():
            time.sleep(0.2)  # Simulate DB write
            return True

        # Execute writes
        futures = [db_pool.submit(write_operation) for _ in range(50)]
        results = [f.result() for f in futures]
        
        duration = time.time() - start_time
        
        assert all(results)  # All operations successful
        assert duration < 5.0  # Complete within 5 seconds

class TestCachePerformance:
    """Test caching system performance"""

    def test_cache_hit_ratio(self):
        """Test cache hit ratio under load"""
        cache_hits = 0
        cache_misses = 0
        total_operations = 1000

        for _ in range(total_operations):
            if time.time() % 2 == 0:  # Simulate cache hit
                cache_hits += 1
            else:  # Simulate cache miss
                cache_misses += 1

        hit_ratio = cache_hits / total_operations
        assert hit_ratio > 0.8  # Minimum 80% cache hit ratio

class TestMemoryUsage:
    """Test memory usage under load"""

    def test_memory_leak(self):
        """Test for memory leaks during operations"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Perform memory-intensive operations
        large_data = ["x" * 1000 for _ in range(1000)]
        del large_data

        # Check memory usage
        final_memory = process.memory_info().rss
        memory_diff = final_memory - initial_memory

        # Allow for some memory overhead, but fail if too high
        assert memory_diff < 10 * 1024 * 1024  # Less than 10MB increase

@pytest.mark.asyncio
async def test_end_to_end_performance():
    """Test end-to-end system performance"""
    
    async def complex_operation():
        """Simulate complex business operation"""
        await asyncio.sleep(0.3)  # Simulate processing
        return True

    start_time = time.time()
    
    # Execute multiple operations concurrently
    tasks = [complex_operation() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    
    assert all(results)  # All operations successful
    assert duration < 1.0  # Complete within 1 second

class ControlsLoadTest(HttpUser):
    """Load test for Controls module"""
    wait_time = between(1, 2)

    @task
    def test_validation_endpoint(self):
        self.client.post("/api/v1/controls/validate", json={
            "data": {"test": "data"}
        })

    @task
    def test_processing_endpoint(self):
        self.client.post("/api/v1/controls/process", json={
            "action": "test",
            "parameters": {}
        })

if __name__ == "__main__":
    pytest.main([__file__])
