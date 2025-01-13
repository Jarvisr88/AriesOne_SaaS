import { injectable, inject } from 'inversify';
import Redis from 'ioredis';
import { ConfigService } from '../config/config.service';
import { LoggerService } from '../logger/logger.service';

@injectable()
export class CacheService {
  private readonly client: Redis;
  private readonly defaultTTL: number;

  constructor(
    @inject(ConfigService) private readonly config: ConfigService,
    @inject(LoggerService) private readonly logger: LoggerService
  ) {
    this.defaultTTL = this.config.get('cache.defaultTTL', 3600);
    this.client = this.createRedisClient();
  }

  private createRedisClient(): Redis {
    const options = {
      host: this.config.get('redis.host', 'localhost'),
      port: this.config.get('redis.port', 6379),
      password: this.config.get('redis.password'),
      db: this.config.get('redis.db', 0),
      retryStrategy: (times: number) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      maxRetriesPerRequest: 3
    };

    const client = new Redis(options);

    client.on('error', (error) => {
      this.logger.error('Redis client error', { error });
    });

    client.on('connect', () => {
      this.logger.info('Redis client connected');
    });

    return client;
  }

  async get<T>(key: string): Promise<T | null> {
    try {
      const value = await this.client.get(key);
      if (!value) return null;

      return JSON.parse(value) as T;
    } catch (error) {
      this.logger.error('Cache get error', { error, key });
      return null;
    }
  }

  async set<T>(
    key: string, 
    value: T, 
    ttl: number = this.defaultTTL
  ): Promise<void> {
    try {
      const serialized = JSON.stringify(value);
      await this.client.setex(key, ttl, serialized);
    } catch (error) {
      this.logger.error('Cache set error', { error, key });
    }
  }

  async delete(key: string): Promise<void> {
    try {
      await this.client.del(key);
    } catch (error) {
      this.logger.error('Cache delete error', { error, key });
    }
  }

  async has(key: string): Promise<boolean> {
    try {
      return await this.client.exists(key) === 1;
    } catch (error) {
      this.logger.error('Cache exists error', { error, key });
      return false;
    }
  }

  async clear(): Promise<void> {
    try {
      await this.client.flushdb();
    } catch (error) {
      this.logger.error('Cache clear error', { error });
    }
  }

  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    ttl: number = this.defaultTTL
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached) return cached;

    const value = await factory();
    await this.set(key, value, ttl);
    return value;
  }

  async deletePattern(pattern: string): Promise<void> {
    try {
      const keys = await this.client.keys(pattern);
      if (keys.length > 0) {
        await this.client.del(...keys);
      }
    } catch (error) {
      this.logger.error('Cache delete pattern error', { error, pattern });
    }
  }

  async increment(key: string): Promise<number> {
    try {
      return await this.client.incr(key);
    } catch (error) {
      this.logger.error('Cache increment error', { error, key });
      return 0;
    }
  }

  async decrement(key: string): Promise<number> {
    try {
      return await this.client.decr(key);
    } catch (error) {
      this.logger.error('Cache decrement error', { error, key });
      return 0;
    }
  }

  async setHash(
    key: string,
    field: string,
    value: string,
    ttl: number = this.defaultTTL
  ): Promise<void> {
    try {
      await this.client.hset(key, field, value);
      await this.client.expire(key, ttl);
    } catch (error) {
      this.logger.error('Cache setHash error', { error, key, field });
    }
  }

  async getHash(key: string, field: string): Promise<string | null> {
    try {
      return await this.client.hget(key, field);
    } catch (error) {
      this.logger.error('Cache getHash error', { error, key, field });
      return null;
    }
  }

  async getAllHash(key: string): Promise<Record<string, string>> {
    try {
      return await this.client.hgetall(key);
    } catch (error) {
      this.logger.error('Cache getAllHash error', { error, key });
      return {};
    }
  }

  async deleteHashField(key: string, field: string): Promise<void> {
    try {
      await this.client.hdel(key, field);
    } catch (error) {
      this.logger.error('Cache deleteHashField error', { error, key, field });
    }
  }
}
