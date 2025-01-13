# Database Troubleshooting Guide

## Common Issues and Solutions

### Connection Pool Issues

#### Problem: Connection Pool Exhaustion
```
Error: Connection pool is full
```

**Solution:**
1. Check current pool settings:
```typescript
const status = await dbService.getStatus();
console.log(status.activeConnections, status.poolSize);
```

2. Adjust pool configuration:
```typescript
{
  extra: {
    max: 30, // Increase max connections
    idleTimeoutMillis: 30000
  }
}
```

3. Monitor connection usage:
```typescript
// Add to your metrics service
metrics.gauge('db.connections.active', status.activeConnections);
```

#### Problem: Connection Timeouts
```
Error: Connection terminated unexpectedly
```

**Solution:**
1. Check network connectivity
2. Verify database server status
3. Adjust timeout settings:
```typescript
{
  extra: {
    connectionTimeoutMillis: 5000,
    statement_timeout: 10000
  }
}
```

### Query Performance

#### Problem: Slow Queries
```
Warning: Query execution time exceeded 1000ms
```

**Solution:**
1. Enable query logging:
```typescript
{
  logging: true,
  maxQueryExecutionTime: 1000
}
```

2. Analyze query plan:
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = $1;
```

3. Add appropriate indexes:
```typescript
@Entity('users')
export class User {
    @Index()
    @Column()
    email: string;
}
```

#### Problem: N+1 Queries
Symptoms: Multiple sequential queries for related data

**Solution:**
1. Use proper relations:
```typescript
const users = await userRepository.find({
    relations: ['profile', 'sessions']
});
```

2. Implement data loader:
```typescript
@Injectable()
export class UserLoader {
    private loader = new DataLoader(async (ids: string[]) => {
        const users = await this.userRepository.findByIds(ids);
        return ids.map(id => users.find(user => user.id === id));
    });
}
```

### Caching Issues

#### Problem: Cache Miss Storm
```
Warning: High cache miss rate detected
```

**Solution:**
1. Implement stale-while-revalidate:
```typescript
async function getCachedData(key: string): Promise<any> {
    const cached = await cache.get(key);
    if (cached) {
        if (isStale(cached)) {
            refreshCache(key).catch(console.error);
        }
        return cached.data;
    }
    return refreshCache(key);
}
```

2. Add cache warming:
```typescript
@Injectable()
export class CacheWarmer implements OnModuleInit {
    async onModuleInit() {
        await this.warmFrequentlyAccessedData();
    }
}
```

#### Problem: Cache Invalidation
```
Error: Stale data detected
```

**Solution:**
1. Implement proper invalidation patterns:
```typescript
async function updateEntity(id: string, data: any) {
    await entityRepository.update(id, data);
    await cache.deletePattern(`entity:${id}:*`);
}
```

2. Use versioning:
```typescript
interface CacheItem<T> {
    version: number;
    data: T;
    timestamp: number;
}
```

### Transaction Issues

#### Problem: Deadlocks
```
Error: Deadlock detected
```

**Solution:**
1. Implement retry logic:
```typescript
async function executeWithRetry<T>(
    fn: () => Promise<T>,
    retries = 3
): Promise<T> {
    try {
        return await fn();
    } catch (error) {
        if (error.code === '40P01' && retries > 0) {
            await delay(1000);
            return executeWithRetry(fn, retries - 1);
        }
        throw error;
    }
}
```

2. Order operations consistently:
```typescript
await dbService.executeTransaction(async manager => {
    // Always update lower ID first
    const [id1, id2] = [userId1, userId2].sort();
    await manager.update(User, id1, data1);
    await manager.update(User, id2, data2);
});
```

### Session Management

#### Problem: Session Leaks
```
Warning: High number of active sessions
```

**Solution:**
1. Implement session cleanup:
```typescript
@Injectable()
export class SessionCleanup {
    @Cron('0 * * * *') // Every hour
    async cleanup() {
        await this.sessionService.cleanupExpiredSessions();
    }
}
```

2. Monitor session metrics:
```typescript
metrics.gauge('sessions.active', activeSessionCount);
metrics.histogram('sessions.duration', sessionDuration);
```

## Monitoring and Debugging

### Enable Detailed Logging
```typescript
@Injectable()
export class DatabaseLogger implements Logger {
    logQuery(query: string, parameters?: any[]) {
        this.logger.debug('Query executed', {
            query,
            parameters,
            timestamp: new Date()
        });
    }
}
```

### Performance Monitoring
```typescript
@Injectable()
export class DatabaseMetrics {
    recordQuery(duration: number, success: boolean) {
        this.metrics.histogram('db.query.duration', duration);
        this.metrics.increment('db.query.total');
        if (!success) {
            this.metrics.increment('db.query.errors');
        }
    }
}
```

### Health Checks
```typescript
@Injectable()
export class HealthCheck {
    @Get('/health/db')
    async checkDatabase() {
        const status = await this.dbService.getStatus();
        const isHealthy = await this.dbService.checkConnection();
        
        return {
            status: isHealthy ? 'up' : 'down',
            details: status
        };
    }
}
```

## Recovery Procedures

### Database Backup
```bash
# Automated backup script
#!/bin/bash
timestamp=$(date +%Y%m%d_%H%M%S)
pg_dump -Fc ariesone > backup_${timestamp}.dump
```

### Data Recovery
```typescript
async function recoverData(backupFile: string) {
    await dbService.executeTransaction(async manager => {
        // Restore from backup
        await manager.query(`
            DROP SCHEMA public CASCADE;
            CREATE SCHEMA public;
            \i ${backupFile}
        `);
    });
}
```

### Emergency Contacts

- **Database Administrator**
  - Name: [Name]
  - Phone: [Phone]
  - Email: [Email]

- **System Administrator**
  - Name: [Name]
  - Phone: [Phone]
  - Email: [Email]

## Performance Tuning

### Query Optimization
1. Use proper indexes
2. Implement query caching
3. Monitor execution plans
4. Use connection pooling effectively

### Cache Optimization
1. Set appropriate TTLs
2. Implement cache warming
3. Use proper invalidation strategies
4. Monitor cache hit rates

### Connection Pool Optimization
1. Monitor connection usage
2. Adjust pool size based on load
3. Implement proper timeout settings
4. Use connection lifecycle hooks
