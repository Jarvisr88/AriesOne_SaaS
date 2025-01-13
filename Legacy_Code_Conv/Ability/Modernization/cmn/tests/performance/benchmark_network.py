"""
Performance benchmarks for network operations.
"""
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import statistics
from typing import List, Dict
import aiohttp
import pytest
from locust import HttpUser, task, between
from prometheus_client import CollectorRegistry, Counter, Histogram

from ...network.connection_manager import ConnectionPool
from ...monitoring.telemetry_service import TelemetryService
from ...config import get_settings

settings = get_settings()

class NetworkLoadTest(HttpUser):
    """Load test for network operations."""
    
    wait_time = between(0.1, 1.0)
    
    def on_start(self):
        """Setup before tests."""
        self.pool = ConnectionPool(
            pool_size=settings.POOL_SIZE,
            timeout=settings.CONNECTION_TIMEOUT,
            retry_attempts=settings.RETRY_ATTEMPTS
        )
        self.telemetry = TelemetryService()

    @task
    def test_api_endpoint(self):
        """Test API endpoint performance."""
        with self.client.get(
            "/api/test",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

class BenchmarkResults:
    """Container for benchmark results."""
    
    def __init__(self):
        """Initialize results container."""
        self.latencies: List[float] = []
        self.error_counts: Dict[str, int] = {}
        self.throughput: float = 0.0
        self.concurrent_connections: List[int] = []
        self.cpu_usage: List[float] = []
        self.memory_usage: List[float] = []

async def run_concurrent_requests(
    pool: ConnectionPool,
    num_requests: int,
    endpoint: str
) -> BenchmarkResults:
    """Run concurrent requests and measure performance."""
    results = BenchmarkResults()
    registry = CollectorRegistry()
    
    # Setup metrics
    request_latency = Histogram(
        "request_latency_seconds",
        "Request latency",
        registry=registry
    )
    error_counter = Counter(
        "request_errors_total",
        "Total request errors",
        registry=registry
    )
    
    async def make_request():
        start_time = time.time()
        try:
            async with pool.get_connection(endpoint) as response:
                latency = time.time() - start_time
                results.latencies.append(latency)
                request_latency.observe(latency)
                
                if response.status >= 400:
                    error_counter.inc()
                    error_type = f"status_{response.status}"
                    results.error_counts[error_type] = (
                        results.error_counts.get(error_type, 0) + 1
                    )
                    
        except Exception as e:
            error_counter.inc()
            error_type = type(e).__name__
            results.error_counts[error_type] = (
                results.error_counts.get(error_type, 0) + 1
            )

    # Run concurrent requests
    start_time = time.time()
    tasks = [make_request() for _ in range(num_requests)]
    await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    # Calculate metrics
    results.throughput = num_requests / total_time
    return results

@pytest.mark.benchmark
async def test_network_performance():
    """Run network performance benchmarks."""
    pool = ConnectionPool(
        pool_size=settings.POOL_SIZE,
        timeout=settings.CONNECTION_TIMEOUT,
        retry_attempts=settings.RETRY_ATTEMPTS
    )
    await pool.initialize()
    
    try:
        # Test scenarios
        scenarios = [
            ("Light Load", 100),
            ("Medium Load", 500),
            ("Heavy Load", 1000),
            ("Stress Test", 5000)
        ]
        
        for scenario_name, num_requests in scenarios:
            print(f"\nRunning {scenario_name} test...")
            
            results = await run_concurrent_requests(
                pool,
                num_requests,
                "https://api.example.com"
            )
            
            # Calculate statistics
            latency_stats = {
                "min": min(results.latencies),
                "max": max(results.latencies),
                "mean": statistics.mean(results.latencies),
                "median": statistics.median(results.latencies),
                "p95": statistics.quantiles(results.latencies, n=20)[18],
                "p99": statistics.quantiles(results.latencies, n=100)[98]
            }
            
            # Print results
            print(f"\n{scenario_name} Results:")
            print(f"Throughput: {results.throughput:.2f} requests/second")
            print("\nLatency (seconds):")
            for metric, value in latency_stats.items():
                print(f"  {metric}: {value:.3f}")
            
            print("\nErrors:")
            for error_type, count in results.error_counts.items():
                print(f"  {error_type}: {count}")
            
            # Verify performance requirements
            assert latency_stats["p95"] < 0.1, "95th percentile latency too high"
            assert latency_stats["max"] < 0.5, "Maximum latency too high"
            assert len(results.error_counts) == 0, "Unexpected errors occurred"
            
    finally:
        await pool.close()

@pytest.mark.benchmark
async def test_connection_pool_scaling():
    """Test connection pool scaling performance."""
    pool_sizes = [10, 50, 100, 500]
    request_counts = [100, 500, 1000]
    
    results = {}
    for size in pool_sizes:
        pool = ConnectionPool(
            pool_size=size,
            timeout=settings.CONNECTION_TIMEOUT,
            retry_attempts=settings.RETRY_ATTEMPTS
        )
        await pool.initialize()
        
        try:
            size_results = {}
            for count in request_counts:
                benchmark_results = await run_concurrent_requests(
                    pool,
                    count,
                    "https://api.example.com"
                )
                size_results[count] = benchmark_results
            results[size] = size_results
            
        finally:
            await pool.close()
    
    # Analyze scaling efficiency
    for size in pool_sizes:
        print(f"\nPool Size: {size}")
        for count in request_counts:
            res = results[size][count]
            print(f"  Requests: {count}")
            print(f"  Throughput: {res.throughput:.2f} req/s")
            print(f"  Avg Latency: {statistics.mean(res.latencies):.3f}s")

if __name__ == "__main__":
    asyncio.run(test_network_performance())
    asyncio.run(test_connection_pool_scaling())
