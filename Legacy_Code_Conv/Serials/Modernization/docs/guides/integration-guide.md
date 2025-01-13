# Serials Module Integration Guide

## Overview
This guide provides step-by-step instructions for integrating the Serials Module into your application. It covers setup, configuration, and common use cases.

## Prerequisites
- Node.js 18.x or higher
- Redis 6.x or higher
- PostgreSQL 14.x or higher
- TypeScript 4.x or higher

## Installation

### 1. Install Dependencies
```bash
npm install @ariesone/serials-module
```

### 2. Environment Configuration
Create a `.env` file with the following variables:
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ariesone
DB_USER=postgres
DB_PASSWORD=your-password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password

# Security
JWT_SECRET=your-jwt-secret
ENCRYPTION_SECRET=your-encryption-secret
ENCRYPTION_PEPPER=your-pepper-value
SERIAL_PRIVATE_KEY=path/to/private.key
SERIAL_PUBLIC_KEY=path/to/public.key

# API
API_PORT=3000
API_PREFIX=/api/v1
RATE_LIMIT=1000
```

### 3. Database Setup
Run migrations:
```bash
npm run typeorm migration:run
```

### 4. Module Integration
```typescript
// app.module.ts
import { SerialsModule } from '@ariesone/serials-module';

@Module({
  imports: [
    SerialsModule.forRoot({
      // Optional configuration overrides
      rateLimit: 1000,
      cacheExpiry: 3600,
    }),
  ],
})
export class AppModule {}
```

## Basic Usage

### 1. Serial Management

#### Create a Serial
```typescript
import { SerialService } from '@ariesone/serials-module';

@Injectable()
export class YourService {
  constructor(private serialService: SerialService) {}

  async createSerial() {
    const serial = await this.serialService.create({
      clientId: 'client-uuid',
      maxUsageCount: 5,
      expirationDate: new Date('2025-12-31'),
      isDemo: false,
    });
    return serial;
  }
}
```

#### Validate a Serial
```typescript
async validateSerial(serialNumber: string, deviceId: string) {
  const result = await this.serialService.validate({
    serialNumber,
    deviceId,
    deviceInfo: {
      os: 'linux',
      version: '1.0',
    },
  });
  return result;
}
```

### 2. Client Management

#### Create a Client
```typescript
import { ClientService } from '@ariesone/serials-module';

@Injectable()
export class YourService {
  constructor(private clientService: ClientService) {}

  async createClient() {
    const client = await this.clientService.create({
      name: 'ACME Corp',
      clientNumber: 'ACM-12345',
      contactEmail: 'contact@acme.com',
    });
    return client;
  }
}
```

### 3. Usage Tracking

#### Track Usage
```typescript
import { UsageTrackerService } from '@ariesone/serials-module';

@Injectable()
export class YourService {
  constructor(private usageTracker: UsageTrackerService) {}

  async trackUsage(serialId: string, deviceId: string) {
    const result = await this.usageTracker.trackUsage(
      serialId,
      deviceId,
      { os: 'linux', version: '1.0' },
      '192.168.1.1'
    );
    return result;
  }
}
```

## Advanced Features

### 1. Bulk Operations

#### Generate Multiple Serials
```typescript
async generateBulkSerials(count: number) {
  const serials = await this.serialService.createBulk({
    clientId: 'client-uuid',
    count,
    maxUsageCount: 5,
    expirationDate: new Date('2025-12-31'),
  });
  return serials;
}
```

### 2. Real-time Updates

#### Subscribe to Serial Events
```typescript
import { EventEmitter2 } from '@nestjs/event-emitter';

@Injectable()
export class YourService {
  constructor(private eventEmitter: EventEmitter2) {
    this.eventEmitter.on('serial.validated', (data) => {
      console.log('Serial validated:', data);
    });

    this.eventEmitter.on('serial.revoked', (data) => {
      console.log('Serial revoked:', data);
    });
  }
}
```

### 3. Caching

#### Configure Cache
```typescript
import { CacheService } from '@ariesone/serials-module';

@Injectable()
export class YourService {
  constructor(private cacheService: CacheService) {}

  async getCachedSerial(id: string) {
    const cached = await this.cacheService.get(`serial:${id}`);
    if (cached) {
      return cached;
    }

    const serial = await this.serialService.findOne(id);
    await this.cacheService.set(`serial:${id}`, serial);
    return serial;
  }
}
```

## Security Considerations

### 1. Key Management
Generate secure keys:
```bash
# Generate RSA key pair
openssl genrsa -out private.key 4096
openssl rsa -in private.key -pubout -out public.key

# Generate encryption secret
openssl rand -hex 32 > encryption.secret

# Generate pepper value
openssl rand -hex 32 > pepper.secret
```

### 2. Rate Limiting
Configure rate limits in your environment:
```typescript
@Module({
  imports: [
    ThrottlerModule.forRoot({
      ttl: 60,
      limit: 1000,
    }),
  ],
})
```

### 3. Input Validation
Use provided DTOs and validators:
```typescript
import { CreateSerialDto } from '@ariesone/serials-module';

@Post()
async create(@Body() dto: CreateSerialDto) {
  return this.serialService.create(dto);
}
```

## Monitoring

### 1. Health Checks
```typescript
import { HealthCheckService } from '@ariesone/serials-module';

@Injectable()
export class YourService {
  constructor(private healthCheck: HealthCheckService) {}

  async checkHealth() {
    const status = await this.healthCheck.check();
    return status;
  }
}
```

### 2. Metrics
```typescript
import { MetricsService } from '@ariesone/serials-module';

@Injectable()
export class YourService {
  constructor(private metrics: MetricsService) {}

  async getMetrics() {
    const metrics = await this.metrics.collect();
    return metrics;
  }
}
```

## Troubleshooting

### Common Issues

1. Connection Issues
```typescript
// Check database connection
await this.serialService.checkConnection();

// Check Redis connection
await this.cacheService.ping();
```

2. Performance Issues
```typescript
// Enable query logging
TypeOrmModule.forRoot({
  logging: true,
});

// Monitor cache hits
const stats = await this.cacheService.getStats();
```

3. Error Handling
```typescript
try {
  await this.serialService.validate(serial);
} catch (error) {
  if (error instanceof SerialValidationError) {
    // Handle validation error
  } else if (error instanceof RateLimitError) {
    // Handle rate limit
  }
}
```

## Support
For additional support:
- Documentation: https://docs.ariesone.com/serials
- GitHub Issues: https://github.com/ariesone/serials-module/issues
- Email: support@ariesone.com
