import { Injectable } from '@nestjs/common';
import { ConfigService } from '../config/config.service';
import { LoggerService } from '../logger/logger.service';
import { TypeOrmModuleOptions } from '@nestjs/typeorm';

@Injectable()
export class DatabaseConfig {
  constructor(
    private readonly config: ConfigService,
    private readonly logger: LoggerService
  ) {}

  /**
   * Gets TypeORM configuration for the main database connection
   */
  getTypeOrmConfig(): TypeOrmModuleOptions {
    const config: TypeOrmModuleOptions = {
      type: 'postgres',
      host: this.config.get('DB_HOST', 'localhost'),
      port: this.config.getNumber('DB_PORT', 5432),
      username: this.config.get('DB_USERNAME', 'postgres'),
      password: this.config.get('DB_PASSWORD', ''),
      database: this.config.get('DB_DATABASE', 'ariesone'),
      entities: ['dist/**/*.entity{.ts,.js}'],
      migrations: ['dist/migrations/*{.ts,.js}'],
      synchronize: this.config.get('NODE_ENV', 'development') === 'development',
      logging: this.config.getBoolean('DB_LOGGING', false),
      logger: 'advanced-console',
      maxQueryExecutionTime: 1000, // Log slow queries (>1s)
      cache: {
        type: 'redis',
        options: {
          host: this.config.get('REDIS_HOST', 'localhost'),
          port: this.config.getNumber('REDIS_PORT', 6379),
          password: this.config.get('REDIS_PASSWORD', ''),
          db: this.config.getNumber('REDIS_DB', 0)
        },
        duration: 60000 // 1 minute
      },
      extra: {
        max: this.config.getNumber('DB_POOL_MAX', 20), // Max connections
        connectionTimeoutMillis: 3000, // Connection timeout
        idleTimeoutMillis: 30000, // How long a connection can be idle
        ssl: this.config.getBoolean('DB_SSL', false)
          ? {
              rejectUnauthorized: false
            }
          : undefined
      }
    };

    this.logger.debug('Database configuration loaded', {
      host: config.host,
      port: config.port,
      database: config.database,
      maxConnections: config.extra?.max
    });

    return config;
  }
}
