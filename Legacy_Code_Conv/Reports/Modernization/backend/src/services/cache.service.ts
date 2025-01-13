import { Injectable } from '@nestjs/common';
import { RedisService } from '@liaoliaots/nestjs-redis';
import Redis from 'ioredis';

@Injectable()
export class CacheService {
  private readonly redis: Redis;

  constructor(private redisService: RedisService) {
    this.redis = this.redisService.getClient();
  }

  async get<T>(key: string): Promise<T | null> {
    const data = await this.redis.get(key);
    if (!data) {
      return null;
    }
    return JSON.parse(data);
  }

  async set(key: string, value: any, ttlSeconds: number): Promise<void> {
    await this.redis.set(
      key,
      JSON.stringify(value),
      'EX',
      ttlSeconds,
    );
  }

  async invalidatePattern(pattern: string): Promise<void> {
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  async invalidateKey(key: string): Promise<void> {
    await this.redis.del(key);
  }

  async getOrSet<T>(
    key: string,
    ttlSeconds: number,
    factory: () => Promise<T>,
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached) {
      return cached;
    }

    const value = await factory();
    await this.set(key, value, ttlSeconds);
    return value;
  }
}
