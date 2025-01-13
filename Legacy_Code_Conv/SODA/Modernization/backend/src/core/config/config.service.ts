import { injectable } from 'inversify';
import * as dotenv from 'dotenv';
import * as path from 'path';
import { get } from 'lodash';

@injectable()
export class ConfigService {
  private config: Record<string, any>;

  constructor() {
    this.loadConfig();
  }

  private loadConfig(): void {
    // Load .env file
    dotenv.config({
      path: path.resolve(process.cwd(), '.env')
    });

    // Base configuration
    this.config = {
      app: {
        name: process.env.APP_NAME || 'soda-service',
        environment: process.env.NODE_ENV || 'development',
        port: parseInt(process.env.PORT || '3000', 10)
      },
      soda: {
        apiEndpoint: process.env.SODA_API_ENDPOINT,
        appToken: process.env.SODA_APP_TOKEN,
        timeout: parseInt(process.env.SODA_TIMEOUT || '30000', 10),
        enableCaching: process.env.SODA_ENABLE_CACHING === 'true',
        cacheTTL: parseInt(process.env.SODA_CACHE_TTL || '3600', 10)
      },
      auth: {
        jwtSecret: process.env.JWT_SECRET,
        tokenExpiration: process.env.TOKEN_EXPIRATION || '1h',
        cacheTTL: parseInt(process.env.AUTH_CACHE_TTL || '3600', 10)
      },
      redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379', 10),
        password: process.env.REDIS_PASSWORD,
        db: parseInt(process.env.REDIS_DB || '0', 10)
      },
      logger: {
        level: process.env.LOG_LEVEL || 'info',
        file: process.env.LOG_FILE
      },
      cache: {
        defaultTTL: parseInt(process.env.CACHE_DEFAULT_TTL || '3600', 10),
        maxSize: parseInt(process.env.CACHE_MAX_SIZE || '1000', 10)
      },
      metrics: {
        enabled: process.env.METRICS_ENABLED === 'true',
        interval: parseInt(process.env.METRICS_INTERVAL || '60000', 10)
      },
      rateLimit: {
        windowMs: parseInt(process.env.RATE_LIMIT_WINDOW || '900000', 10),
        max: parseInt(process.env.RATE_LIMIT_MAX || '100', 10)
      }
    };
  }

  get<T>(key: string, defaultValue?: T): T {
    return get(this.config, key, defaultValue);
  }

  set(key: string, value: any): void {
    this.config[key] = value;
  }

  has(key: string): boolean {
    return get(this.config, key) !== undefined;
  }

  getAll(): Record<string, any> {
    return { ...this.config };
  }

  validate(): string[] {
    const requiredKeys = [
      'soda.apiEndpoint',
      'soda.appToken',
      'auth.jwtSecret'
    ];

    const missingKeys = requiredKeys.filter(key => !this.has(key));
    return missingKeys;
  }
}
