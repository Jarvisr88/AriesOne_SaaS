import { Injectable, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, LessThan, Between } from 'typeorm';
import { Serial } from '../entities/serial.entity';
import { SerialUsage } from '../entities/serial-usage.entity';
import { CacheService } from '../services/cache.service';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { Cron, CronExpression } from '@nestjs/schedule';

@Injectable()
export class AutoRenewalService implements OnModuleInit {
  private readonly renewalKeyPrefix = 'renewal:';
  private readonly warningDays = 7;

  constructor(
    @InjectRepository(Serial)
    private serialRepository: Repository<Serial>,
    @InjectRepository(SerialUsage)
    private usageRepository: Repository<SerialUsage>,
    private cacheService: CacheService,
    private eventEmitter: EventEmitter2,
  ) {}

  async onModuleInit() {
    // Initialize renewal tracking
    await this.cacheService.set('renewal:lastCheck', Date.now());
  }

  @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
  async checkExpiringSerials() {
    const now = new Date();
    const warningDate = new Date(now.getTime() + this.warningDays * 24 * 60 * 60 * 1000);

    // Find serials expiring soon
    const expiringSerials = await this.serialRepository.find({
      where: {
        expirationDate: Between(now, warningDate),
        isActive: true,
        isDemo: false,
      },
      relations: ['client'],
    });

    for (const serial of expiringSerials) {
      // Check if warning already sent
      const warningSentKey = `${this.renewalKeyPrefix}warned:${serial.id}`;
      const warningSent = await this.cacheService.exists(warningSentKey);

      if (!warningSent) {
        // Emit expiration warning event
        this.eventEmitter.emit('serial.expiring', {
          serialId: serial.id,
          serialNumber: serial.serialNumber,
          clientId: serial.client.id,
          clientName: serial.client.name,
          expirationDate: serial.expirationDate,
        });

        // Mark warning as sent
        await this.cacheService.set(warningSentKey, true, 7 * 24 * 60 * 60); // 7 days TTL
      }
    }
  }

  @Cron(CronExpression.EVERY_HOUR)
  async processExpiredSerials() {
    const now = new Date();

    // Find expired serials
    const expiredSerials = await this.serialRepository.find({
      where: {
        expirationDate: LessThan(now),
        isActive: true,
      },
    });

    for (const serial of expiredSerials) {
      // Deactivate serial
      await this.serialRepository.update(serial.id, {
        isActive: false,
      });

      // Mark active usages as expired
      await this.usageRepository.update(
        {
          serialId: serial.id,
          status: 'active',
        },
        {
          status: 'expired',
        }
      );

      // Emit expiration event
      this.eventEmitter.emit('serial.expired', {
        serialId: serial.id,
        serialNumber: serial.serialNumber,
        expirationDate: serial.expirationDate,
      });
    }
  }

  async renewSerial(
    serialId: string,
    newExpirationDate: Date,
    userId: string
  ): Promise<Serial> {
    const serial = await this.serialRepository.findOne({
      where: { id: serialId },
    });

    if (!serial) {
      throw new Error('Serial not found');
    }

    // Update expiration date
    serial.expirationDate = newExpirationDate;
    serial.isActive = true;
    serial.updatedBy = userId;

    // Save changes
    const updatedSerial = await this.serialRepository.save(serial);

    // Clear warning cache if exists
    await this.cacheService.del(`${this.renewalKeyPrefix}warned:${serialId}`);

    // Emit renewal event
    this.eventEmitter.emit('serial.renewed', {
      serialId,
      serialNumber: serial.serialNumber,
      oldExpirationDate: serial.expirationDate,
      newExpirationDate,
    });

    return updatedSerial;
  }

  async bulkRenew(
    serialIds: string[],
    newExpirationDate: Date,
    userId: string
  ): Promise<Serial[]> {
    const renewedSerials = [];

    for (const serialId of serialIds) {
      try {
        const renewedSerial = await this.renewSerial(
          serialId,
          newExpirationDate,
          userId
        );
        renewedSerials.push(renewedSerial);
      } catch (error) {
        console.error(`Failed to renew serial ${serialId}:`, error);
      }
    }

    return renewedSerials;
  }

  async getExpirationStats(): Promise<{
    expiringSoon: number;
    expired: number;
    active: number;
  }> {
    const now = new Date();
    const warningDate = new Date(now.getTime() + this.warningDays * 24 * 60 * 60 * 1000);

    const [expiringSoon, expired, active] = await Promise.all([
      this.serialRepository.count({
        where: {
          expirationDate: Between(now, warningDate),
          isActive: true,
          isDemo: false,
        },
      }),
      this.serialRepository.count({
        where: {
          expirationDate: LessThan(now),
          isActive: true,
        },
      }),
      this.serialRepository.count({
        where: {
          expirationDate: LessThan(warningDate),
          isActive: true,
        },
      }),
    ]);

    return {
      expiringSoon,
      expired,
      active,
    };
  }
}
