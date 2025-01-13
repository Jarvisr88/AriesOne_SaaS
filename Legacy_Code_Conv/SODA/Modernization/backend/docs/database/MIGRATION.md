# Database Migration Guide

## Overview
This guide details the process of migrating from the legacy `Globals.cs` database management to the new TypeORM-based infrastructure.

## Legacy vs Modern Comparison

### Connection Management

#### Legacy (`Globals.cs`)
```csharp
public static SqlConnection GetConnection()
{
    return new SqlConnection(connectionString);
}
```

#### Modern (`DatabaseService`)
```typescript
@Injectable()
export class DatabaseService {
    constructor(
        @InjectConnection()
        private readonly connection: Connection
    ) {}

    async executeQuery<T>(query: string, parameters: any[] = []): Promise<T> {
        // Managed connection with retries and pooling
    }
}
```

### Session Handling

#### Legacy
```csharp
public static void SetSession(string key, object value)
{
    HttpContext.Current.Session[key] = value;
}
```

#### Modern
```typescript
@Injectable()
export class SessionService {
    async createSession(data: SessionData): Promise<Session> {
        // Type-safe session creation with validation
    }
}
```

## Migration Steps

### 1. Database Configuration
1. Create `.env` file with database credentials
2. Configure TypeORM connection in `database.config.ts`
3. Set up connection pooling parameters

### 2. Entity Migration
1. Convert table structures to TypeORM entities
2. Add proper relations and indices
3. Implement validation decorators

Example:
```typescript
@Entity('users')
export class User {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column({ length: 100 })
    name: string;

    @OneToMany(() => Session, session => session.user)
    sessions: Session[];
}
```

### 3. Repository Implementation
1. Create repositories extending `BaseRepository`
2. Implement custom query methods
3. Add caching where appropriate

Example:
```typescript
@EntityRepository(User)
export class UserRepository extends BaseRepository<User> {
    async findByEmail(email: string): Promise<User | undefined> {
        return this.findOne({ where: { email } });
    }
}
```

### 4. Service Layer Migration
1. Replace direct SQL queries with repository methods
2. Implement proper error handling
3. Add transaction management

Example:
```typescript
@Injectable()
export class UserService {
    constructor(
        private readonly userRepository: UserRepository,
        private readonly profileRepository: ProfileRepository
    ) {}

    async createUser(data: CreateUserDto): Promise<User> {
        return this.userRepository.executeTransaction(async manager => {
            const user = await manager.save(User, data);
            await manager.save(Profile, { userId: user.id });
            return user;
        });
    }
}
```

### 5. Session Management
1. Replace HttpContext sessions with `SessionService`
2. Implement session cleanup
3. Add activity tracking

### 6. Error Handling
1. Replace try-catch blocks with proper error classes
2. Implement retry logic for transient failures
3. Add proper logging

Example:
```typescript
try {
    await this.userRepository.createEntity(userData);
} catch (error) {
    if (error instanceof ValidationError) {
        // Handle validation error
    } else if (error instanceof DatabaseError) {
        // Handle database error
    }
    throw error;
}
```

### 7. Caching Implementation
1. Configure Redis connection
2. Implement entity caching
3. Add query result caching

Example:
```typescript
@Injectable()
export class UserService {
    private readonly CACHE_TTL = 300; // 5 minutes

    async getUserById(id: string): Promise<User> {
        const cacheKey = `user:${id}`;
        const cached = await this.cache.get<User>(cacheKey);
        
        if (cached) {
            return cached;
        }

        const user = await this.userRepository.findOne(id);
        await this.cache.set(cacheKey, user, this.CACHE_TTL);
        
        return user;
    }
}
```

### 8. Testing and Validation
1. Create integration tests
2. Validate data migration
3. Performance testing

## Testing Strategy

### Unit Tests
```typescript
describe('UserService', () => {
    it('should create user with profile', async () => {
        const user = await userService.createUser(userData);
        expect(user).toBeDefined();
        expect(user.profile).toBeDefined();
    });
});
```

### Integration Tests
```typescript
describe('Database Integration', () => {
    it('should handle transactions correctly', async () => {
        await dbService.executeTransaction(async manager => {
            // Test transaction operations
        });
    });
});
```

## Rollback Plan

### Before Migration
1. Backup all databases
2. Document current state
3. Create restoration points

### During Migration
1. Keep legacy system running
2. Implement feature flags
3. Monitor performance

### Rollback Steps
1. Disable new features
2. Restore from backup if needed
3. Switch back to legacy system

## Performance Monitoring

### Key Metrics
1. Query execution time
2. Connection pool usage
3. Cache hit rates
4. Error rates

### Monitoring Tools
1. TypeORM logging
2. Redis monitoring
3. Application metrics
4. Error tracking

## Security Considerations

### Data Protection
1. Implement proper input validation
2. Use prepared statements
3. Enable SSL/TLS

### Access Control
1. Implement role-based access
2. Validate sessions
3. Log security events

## Post-Migration Tasks

### Cleanup
1. Remove legacy code
2. Archive old data
3. Update documentation

### Optimization
1. Fine-tune connection pool
2. Optimize queries
3. Adjust cache settings

### Documentation
1. Update API documentation
2. Document new features
3. Create troubleshooting guides

## Support and Maintenance

### Regular Tasks
1. Monitor performance
2. Review error logs
3. Update dependencies

### Troubleshooting
1. Connection issues
2. Performance problems
3. Cache invalidation

## Contact

For support and questions:
- Technical Lead: [Name]
- Database Admin: [Name]
- Support Team: [Email]
