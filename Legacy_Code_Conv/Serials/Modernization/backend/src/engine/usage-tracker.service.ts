import { Injectable, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, LessThan } from 'typeorm';
import { SerialUsage } from '../entities/serial-usage.entity';
import { Serial } from '../entities/serial.entity';
import { CacheService } from '../services/cache.service';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { Cron, CronExpression } from '@nestjs/schedule';

@Injectable()
export class UsageTrackerService implements OnModuleInit {
  private readonly usageKeyPrefix = 'usage:';
  private readonly lockTimeout = 30000; // 30 seconds

  constructor(
    @InjectRepository(SerialUsage)
    private usageRepository: Repository<SerialUsage>,
    @InjectRepository(Serial)
    private serialRepository: Repository<Serial>,
    private cacheService: CacheService,
    private eventEmitter: EventEmitter2,
  ) {}

  async onModuleInit() {
    // Initialize any required cache structures
    await this.cacheService.set('usage:lastCleanup', Date.now());
  }

  async trackUsage(
    serialId: string,
    deviceId: string,
    deviceInfo: Record<string, any>,
    ipAddress: string
  ): Promise<boolean> {
    const lockKey = `${this.usageKeyPrefix}lock:${serialId}`;
    const usageKey = `${this.usageKeyPrefix}${serialId}`;

    try {
      // Acquire lock
      const locked = await this.cacheService.setLock(lockKey);
      if (!locked) {
        throw new Error('Failed to acquire lock');
      }

      // Get current usage count
      const currentCount = await this.cacheService.get<number>(usageKey) || 0;

      // Get serial details
      const serial = await this.serialRepository.findOne({
        where: { id: serialId },
      });

      if (!serial) {
        throw new Error('Serial not found');
      }

      // Check if usage is allowed
      if (currentCount >= serial.maxUsageCount) {
        return false;
      }

      // Create usage record
      const usage = this.usageRepository.create({
        serialId,
        deviceId,
        deviceInfo,
        ipAddress,
        status: 'active',
      });

      await this.usageRepository.save(usage);

      // Update cache
      await this.cacheService.set(usageKey, currentCount + 1);

      // Emit event
      this.eventEmitter.emit('serial.usage', {
        serialId,
        deviceId,
        timestamp: new Date(),
      });

      return true;
    } finally {
      // Release lock
      await this.cacheService.releaseLock(lockKey);
    }
  }

  async revokeUsage(serialId: string, deviceId: string): Promise<void> {
    await this.usageRepository.update(
      {
        serialId,
        deviceId,
        status: 'active',
      },
      {
        status: 'revoked',
      }
    );

    // Emit event
    this.eventEmitter.emit('serial.usage.revoked', {
      serialId,
      deviceId,
      timestamp: new Date(),
    });
  }

  async getActiveUsages(serialId: string): Promise<SerialUsage[]> {
    return this.usageRepository.find({
      where: {
        serialId,
        status: 'active',
      },
    });
  }

  async getUsageHistory(
    serialId: string,
    startDate?: Date,
    endDate?: Date
  ): Promise<SerialUsage[]> {
    const query = this.usageRepository
      .createQueryBuilder('usage')
      .where('usage.serialId = :serialId', { serialId });

    if (startDate) {
      query.andWhere('usage.createdAt >= :startDate', { startDate });
    }

    if (endDate) {
      query.andWhere('usage.createdAt <= :endDate', { endDate });
    }

    return query.orderBy('usage.createdAt', 'DESC').getMany();
  }

  @Cron(CronExpression.EVERY_HOUR)
  async cleanupExpiredUsages() {
    const now = new Date();
    
    // Update expired usages
    await this.usageRepository.update(
      {
        status: 'active',
        expiresAt: LessThan(now),
      },
      {
        status: 'expired',
      }
    );

    // Update cache
    await this.cacheService.set('usage:lastCleanup', Date.now());
  }

  async getUsageStats(serialId: string): Promise<{
    total: number;
    active: number;
    revoked: number;
    expired: number;
    devices: number;
  }> {
    const stats = await this.usageRepository
      .createQueryBuilder('usage')
      .select('usage.status', 'status')
      .addSelect('COUNT(*)', 'count')
      .where('usage.serialId = :serialId', { serialId })
      .groupBy('usage.status')
      .getRawMany();

    const devices = await this.usageRepository
      .createQueryBuilder('usage')
      .select('COUNT(DISTINCT usage.deviceId)', 'count')
      .where('usage.serialId = :serialId', { serialId })
      .getRawOne();

    const result = {
      total: 0,
      active: 0,
      revoked: 0,
      expired: 0,
      devices: parseInt(devices.count),
    };

    stats.forEach((stat) => {
      result[stat.status] = parseInt(stat.count);
      result.total += parseInt(stat.count);
    });

    return result;
  }
}
