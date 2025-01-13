# Performance Tests

Version: 1.0.0
Last Updated: 2025-01-10

This directory contains performance tests for the AriesOne SaaS application using multiple testing tools to ensure comprehensive coverage.

## Test Suites

### 1. Locust Tests
- Located in `locustfile.py`
- Simulates user behavior with realistic scenarios
- Provides real-time metrics and web interface
- Good for identifying bottlenecks and user experience issues

### 2. Artillery Tests
- Located in `artillery.yml` and `functions.js`
- Declarative scenario-based testing
- Excellent for API load testing
- Provides detailed reports and metrics

### 3. K6 Tests
- Located in `k6_test.js`
- Modern performance testing tool
- Supports complex scenarios and metrics
- Great for CI/CD integration

## Running the Tests

### Prerequisites
1. Install dependencies:
```bash
pip install locust
npm install -g artillery
npm install -g k6
```

2. Ensure the application is running on `http://localhost:8000`

### Running Locust Tests
```bash
locust -f locustfile.py --host=http://localhost:8000
```
Then open http://localhost:8089 in your browser

### Running Artillery Tests
```bash
artillery run artillery.yml
```

### Running K6 Tests
```bash
k6 run k6_test.js
```

## Test Scenarios

All test suites cover the following scenarios:
1. User registration and authentication
2. Tenant management
3. Inventory operations
4. Order processing
5. Token refresh

## Performance Targets

### Response Times
- 95th percentile < 500ms
- 99th percentile < 1000ms
- Average < 200ms

### Throughput
- Sustained load: 50 requests/second
- Peak load: 100 requests/second

### Error Rates
- Error rate < 1%
- No cascading failures

### Concurrent Users
- Sustained: 100 users
- Peak: 200 users

## Monitoring

During test execution, monitor:
1. API response times
2. Database performance
3. Memory usage
4. CPU utilization
5. Network I/O

## Test Data

Tests use generated data with realistic patterns:
- User information
- Tenant details
- Inventory items
- Orders

## Analyzing Results

1. Review the generated reports
2. Look for:
   - Response time patterns
   - Error rates and types
   - Resource utilization
   - Bottlenecks
   - System stability

3. Compare results against performance targets
4. Document findings and recommendations

## Troubleshooting

If tests fail:
1. Check application logs
2. Verify database connections
3. Monitor system resources
4. Review error messages
5. Validate test configuration
