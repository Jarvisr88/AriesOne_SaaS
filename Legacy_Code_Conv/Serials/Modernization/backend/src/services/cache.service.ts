import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Redis from 'ioredis';

@Injectable()
export class CacheService implements OnModuleInit {
  private redis: Redis;
  private readonly defaultTTL: number = 3600; // 1 hour

  constructor(private configService: ConfigService) {}

  async onModuleInit() {
    this.redis = new Redis({
      host: this.configService.get<string>('REDIS_HOST'),
      port: this.configService.get<number>('REDIS_PORT'),
      password: this.configService.get<string>('REDIS_PASSWORD'),
      keyPrefix: 'serials:',
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
    });

    this.redis.on('error', (error) => {
      console.error('Redis connection error:', error);
    });
  }

  async get<T>(key: string): Promise<T | null> {
    const data = await this.redis.get(key);
    if (!data) {
      return null;
    }

    try {
      return JSON.parse(data);
    } catch (error) {
      console.error('Cache parse error:', error);
      return null;
    }
  }

  async set(key: string, value: any, ttl: number = this.defaultTTL): Promise<void> {
    try {
      const data = JSON.stringify(value);
      await this.redis.set(key, data, 'EX', ttl);
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }

  async del(key: string): Promise<void> {
    await this.redis.del(key);
  }

  async delPattern(pattern: string): Promise<void> {
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  async exists(key: string): Promise<boolean> {
    const result = await this.redis.exists(key);
    return result === 1;
  }

  async increment(key: string, value: number = 1): Promise<number> {
    return this.redis.incrby(key, value);
  }

  async decrement(key: string, value: number = 1): Promise<number> {
    return this.redis.decrby(key, value);
  }

  async setLock(key: string, ttl: number = 30): Promise<boolean> {
    const result = await this.redis.set(
      `lock:${key}`,
      '1',
      'EX',
      ttl,
      'NX'
    );
    return result === 'OK';
  }

  async releaseLock(key: string): Promise<void> {
    await this.redis.del(`lock:${key}`);
  }

  async clearAll(): Promise<void> {
    const keys = await this.redis.keys('*');
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }
}
