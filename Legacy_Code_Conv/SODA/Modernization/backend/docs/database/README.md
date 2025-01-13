# Database Infrastructure Documentation

## Overview
This document describes the modernized database infrastructure for the AriesOne SaaS platform. The system replaces the legacy global state management with a robust, type-safe, and scalable solution using TypeORM and PostgreSQL.

## Architecture

### Core Components
1. **Database Configuration** (`database.config.ts`)
   - Environment-based configuration
   - Connection pool management
   - SSL support
   - Redis caching integration

2. **Database Service** (`database.service.ts`)
   - Query execution with automatic retries
   - Transaction management
   - Real-time change notifications
   - Connection health monitoring

3. **Base Repository** (`base.repository.ts`)
   - Generic CRUD operations
   - Integrated caching
   - Type-safe queries
   - Validation layer

4. **Session Service** (`session.service.ts`)
   - Session lifecycle management
   - Activity tracking
   - Automatic cleanup
   - Event-driven architecture

## Setup and Configuration

### Environment Variables
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=
DB_DATABASE=ariesone
DB_SSL=false
DB_LOGGING=false
DB_POOL_MAX=20

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

### Connection Pool Settings
- Max Connections: 20 (configurable)
- Connection Timeout: 3000ms
- Idle Timeout: 30000ms
- Query Timeout: 1000ms (for slow query logging)

## Usage Examples

### Basic Database Operations
```typescript
// Inject the database service
constructor(private readonly dbService: DatabaseService) {}

// Execute a query with retries
const users = await this.dbService.executeQuery(
  'SELECT * FROM users WHERE active = $1',
  [true]
);

// Execute in transaction
await this.dbService.executeTransaction(async (manager) => {
  await manager.save(user);
  await manager.save(profile);
});
```

### Using Base Repository
```typescript
// Create a repository
@EntityRepository(User)
export class UserRepository extends BaseRepository<User> {
  // Inherit all base functionality
  // Add custom methods as needed
}

// Use in service
const user = await this.userRepository.findByIdCached(userId);
await this.userRepository.createEntity(userData);
```

### Session Management
```typescript
// Create session
const session = await this.sessionService.createSession({
  userId,
  ip: request.ip,
  userAgent: request.headers['user-agent']
});

// Validate session
const activeSession = await this.sessionService.getSession(sessionId);

// Update activity
await this.sessionService.updateSession(sessionId);

// Destroy session
await this.sessionService.destroySession(sessionId);
```

## Error Handling

### Database Errors
- `DatabaseError`: Base error for database operations
- `ValidationError`: Data validation failures
- `NotFoundError`: Entity not found
- `UnauthorizedError`: Permission denied
- `SessionExpiredError`: Invalid or expired session

### Retry Strategy
1. Automatic retry for transient failures
2. Configurable retry attempts (default: 3)
3. Exponential backoff between retries
4. Detailed error logging

## Performance Optimization

### Caching Strategy
1. **Entity Caching**
   - Individual entities cached by ID
   - Configurable TTL (default: 5 minutes)
   - Automatic cache invalidation on updates

2. **Query Results Caching**
   - List queries cached with composite keys
   - Pattern-based cache invalidation
   - Redis backend for scalability

### Connection Pooling
- Dynamic pool sizing based on load
- Connection health monitoring
- Automatic connection recovery
- Idle connection management

## Security

### Data Protection
1. **Input Validation**
   - Type checking
   - Data sanitization
   - Schema validation

2. **Access Control**
   - Role-based permissions
   - Session validation
   - IP tracking

3. **Audit Logging**
   - Query logging
   - Session activity
   - Error tracking

### SSL Configuration
```typescript
ssl: {
  rejectUnauthorized: false, // For self-signed certificates
  ca: fs.readFileSync('ca.crt'), // Custom CA
  key: fs.readFileSync('client-key.pem'), // Client key
  cert: fs.readFileSync('client-cert.pem') // Client certificate
}
```

## Monitoring and Metrics

### Available Metrics
1. **Query Performance**
   - Execution time
   - Success rate
   - Retry count

2. **Connection Pool**
   - Active connections
   - Idle connections
   - Wait time

3. **Cache Performance**
   - Hit rate
   - Miss rate
   - Invalidation rate

### Health Checks
```typescript
// Database health check
const status = await dbService.getStatus();
const isHealthy = await dbService.checkConnection();
```

## Migration from Legacy System

### Key Differences from `Globals.cs`
1. Dependency Injection vs Static Methods
2. Type Safety
3. Connection Pooling
4. Proper Error Handling
5. Caching Layer
6. Event System
7. Session Management

### Migration Steps
1. Replace static database calls with repository methods
2. Update session handling to use SessionService
3. Implement proper error handling
4. Add caching where needed
5. Update configuration management

## Best Practices

### Query Optimization
1. Use prepared statements
2. Implement proper indexing
3. Optimize JOIN operations
4. Use pagination for large results

### Transaction Management
1. Keep transactions short
2. Handle rollbacks properly
3. Use proper isolation levels
4. Implement retry logic

### Caching Guidelines
1. Cache frequently accessed data
2. Implement proper invalidation
3. Use appropriate TTLs
4. Monitor cache performance

## Troubleshooting

### Common Issues
1. **Connection Timeouts**
   - Check pool configuration
   - Verify network connectivity
   - Monitor connection count

2. **Slow Queries**
   - Review query plans
   - Check indexes
   - Optimize JOIN operations

3. **Cache Issues**
   - Verify Redis connection
   - Check cache keys
   - Monitor memory usage

### Debugging Tools
1. Query logging
2. Performance metrics
3. Connection pool monitoring
4. Cache statistics

## Support and Maintenance

### Regular Maintenance Tasks
1. Monitor connection pool health
2. Review slow queries
3. Analyze cache performance
4. Clean up expired sessions

### Scaling Considerations
1. Connection pool sizing
2. Cache distribution
3. Read/write splitting
4. Sharding strategy
