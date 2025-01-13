# SODA Integration Setup Guide

## Prerequisites
- Node.js v18 or higher
- Redis v6 or higher
- PostgreSQL v14 or higher
- Docker (optional)

## Installation

### Using NPM
```bash
# Install dependencies
npm install @ariesone/soda

# Install peer dependencies
npm install inversify reflect-metadata
```

### Using Docker
```bash
# Pull the Docker image
docker pull ariesone/soda:latest

# Run with Redis and PostgreSQL
docker-compose up -d
```

## Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Server Configuration
PORT=3000
NODE_ENV=production

# Authentication
JWT_SECRET=your-jwt-secret
JWT_EXPIRATION=1h

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=soda
POSTGRES_USER=soda_user
POSTGRES_PASSWORD=your-password

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Rate Limiting
RATE_LIMIT_WINDOW=60000
RATE_LIMIT_MAX=100

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
```

### TypeScript Configuration
Ensure your `tsconfig.json` includes:

```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "target": "ES2020",
    "module": "CommonJS",
    "strict": true
  }
}
```

## Basic Usage

### Initialize the Module
```typescript
import { SodaModule } from '@ariesone/soda';

const soda = new SodaModule({
  // Configuration options
  database: {
    host: process.env.POSTGRES_HOST,
    port: parseInt(process.env.POSTGRES_PORT),
    database: process.env.POSTGRES_DB,
    username: process.env.POSTGRES_USER,
    password: process.env.POSTGRES_PASSWORD
  },
  redis: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT),
    password: process.env.REDIS_PASSWORD
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRATION
  }
});

// Initialize the module
await soda.initialize();
```

### Create a Resource
```typescript
import { DataType } from '@ariesone/soda';

const resource = await soda.resources.create({
  name: 'Users',
  description: 'User records',
  columns: [
    {
      name: 'id',
      dataType: DataType.TEXT,
      required: true
    },
    {
      name: 'email',
      dataType: DataType.TEXT,
      required: true
    },
    {
      name: 'active',
      dataType: DataType.BOOLEAN,
      required: true
    }
  ],
  metadata: {
    tags: ['users', 'auth'],
    customFields: {
      department: 'IT'
    }
  }
});
```

### Query Data
```typescript
const results = await soda.resources.query(resource.id, {
  select: ['id', 'email'],
  where: [
    {
      field: 'active',
      operator: 'EQ',
      value: true
    }
  ],
  orderBy: {
    field: 'email',
    direction: 'ASC'
  },
  limit: 10,
  offset: 0
});
```

### Bulk Upload
```typescript
const data = [
  { id: '1', email: 'user1@example.com', active: true },
  { id: '2', email: 'user2@example.com', active: true }
];

await soda.resources.bulkUpload(resource.id, data);
```

## Security Best Practices

### Authentication
1. Generate strong JWT secrets:
```typescript
import { randomBytes } from 'crypto';
const secret = randomBytes(64).toString('hex');
```

2. Use short-lived tokens:
```typescript
const token = await soda.auth.generateToken({
  userId: 'user123',
  roles: ['admin'],
  expiresIn: '1h'
});
```

### Authorization
1. Implement role-based access:
```typescript
soda.use(async (ctx, next) => {
  const { roles } = await soda.auth.verifyToken(ctx.token);
  if (!roles.includes('admin')) {
    throw new Error('Insufficient permissions');
  }
  return next();
});
```

### Data Validation
1. Add custom validation rules:
```typescript
resource.addValidation('email', (value) => {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    return 'Invalid email format';
  }
  return null;
});
```

## Error Handling
```typescript
try {
  await soda.resources.create(/* ... */);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error('Validation failed:', error.errors);
  } else if (error instanceof AuthenticationError) {
    console.error('Authentication failed:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Monitoring

### Health Checks
```typescript
const health = await soda.health.check();
console.log('System health:', health);
```

### Metrics
```typescript
const metrics = await soda.metrics.get();
console.log('System metrics:', metrics);
```

## Performance Optimization

### Caching
1. Configure cache settings:
```typescript
soda.cache.configure({
  ttl: 3600,
  maxSize: 1000
});
```

2. Use query caching:
```typescript
const results = await soda.resources.query(id, query, {
  cache: true,
  ttl: 300
});
```

### Batch Operations
1. Use bulk operations for large datasets:
```typescript
await soda.resources.bulkUpload(id, data, {
  batchSize: 1000,
  parallel: 4
});
```

## Troubleshooting

### Common Issues

1. Connection Issues
```typescript
// Test database connection
await soda.database.testConnection();

// Test Redis connection
await soda.cache.testConnection();
```

2. Performance Issues
```typescript
// Enable debug logging
soda.logger.setLevel('debug');

// Monitor query performance
soda.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  console.log(`Request took ${Date.now() - start}ms`);
});
```

### Logging
```typescript
// Configure logging
soda.logger.configure({
  level: 'info',
  format: 'json',
  transports: ['console', 'file']
});
```
