from prometheus_client import Counter, Gauge, Histogram, Info
import time

class Metrics:
    def __init__(self):
        # Database connection metrics
        self.db_pool_created = Counter(
            'db_pool_created_total',
            'Number of connection pools created'
        )
        self.db_pool_errors = Counter(
            'db_pool_errors_total',
            'Number of connection pool errors'
        )
        self.db_connections_active = Gauge(
            'db_connections_active',
            'Number of active database connections'
        )
        self.db_connection_errors = Counter(
            'db_connection_errors_total',
            'Number of connection errors'
        )
        
        # Query metrics
        self.db_queries_total = Counter(
            'db_queries_total',
            'Total number of database queries'
        )
        self.db_query_errors = Counter(
            'db_query_errors_total',
            'Number of query errors'
        )
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
        )
        
        # Health check metrics
        self.db_health_check_errors = Counter(
            'db_health_check_errors_total',
            'Number of health check errors'
        )
        
        # Connection pool stats
        self.db_pool_size = Gauge(
            'db_pool_size',
            'Current size of the connection pool'
        )
        self.db_pool_available = Gauge(
            'db_pool_available',
            'Number of available connections in the pool'
        )
        
        # Transaction metrics
        self.db_transactions_total = Counter(
            'db_transactions_total',
            'Total number of database transactions'
        )
        self.db_transaction_errors = Counter(
            'db_transaction_errors_total',
            'Number of transaction errors'
        )
        self.db_transaction_duration = Histogram(
            'db_transaction_duration_seconds',
            'Database transaction duration in seconds',
            buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 30.0)
        )
        
        # Database info
        self.db_info = Info('db_info', 'Database information')
        
        # Query types
        self.db_query_types = Counter(
            'db_query_types_total',
            'Number of queries by type',
            ['type']  # SELECT, INSERT, UPDATE, DELETE
        )
        
        # Row counts
        self.db_rows_affected = Counter(
            'db_rows_affected_total',
            'Number of rows affected by queries',
            ['operation']  # INSERT, UPDATE, DELETE
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Number of cache hits'
        )
        self.cache_misses = Counter(
            'cache_misses_total',
            'Number of cache misses'
        )
        
        # Statement metrics
        self.db_prepared_statements = Gauge(
            'db_prepared_statements',
            'Number of prepared statements'
        )
        
        # Slow query tracking
        self.db_slow_queries = Counter(
            'db_slow_queries_total',
            'Number of slow queries',
            ['query_type']
        )

    def time(self) -> float:
        """Get current time in seconds"""
        return time.monotonic()

    def update_pool_stats(self, size: int, available: int) -> None:
        """Update pool statistics"""
        self.db_pool_size.set(size)
        self.db_pool_available.set(available)

    def record_query(self, query_type: str) -> None:
        """Record query type"""
        self.db_query_types.labels(type=query_type).inc()

    def record_rows_affected(self, operation: str, count: int) -> None:
        """Record number of rows affected"""
        self.db_rows_affected.labels(operation=operation).inc(count)

    def record_slow_query(self, query_type: str) -> None:
        """Record slow query"""
        self.db_slow_queries.labels(query_type=query_type).inc()

# Create global metrics instance
metrics = Metrics()
