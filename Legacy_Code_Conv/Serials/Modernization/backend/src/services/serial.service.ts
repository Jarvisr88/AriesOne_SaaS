import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, FindOptionsWhere, In } from 'typeorm';
import { Serial } from '../entities/serial.entity';
import { SerialUsage } from '../entities/serial-usage.entity';
import { ValidationService } from './validation.service';
import { CacheService } from './cache.service';
import { CreateSerialDto, UpdateSerialDto, ValidateSerialDto } from '../dto/serial.dto';
import { PaginationDto } from '../dto/common.dto';

@Injectable()
export class SerialService {
  constructor(
    @InjectRepository(Serial)
    private serialRepository: Repository<Serial>,
    @InjectRepository(SerialUsage)
    private usageRepository: Repository<SerialUsage>,
    private validationService: ValidationService,
    private cacheService: CacheService,
  ) {}

  async create(dto: CreateSerialDto, userId: string): Promise<Serial> {
    const serial = this.serialRepository.create({
      ...dto,
      createdBy: userId,
      signature: await this.validationService.generateSignature(dto),
      encryptionVersion: 'v1',
    });

    await this.validationService.validateSerial(serial);
    return this.serialRepository.save(serial);
  }

  async createBulk(dtos: CreateSerialDto[], userId: string): Promise<Serial[]> {
    const serials = await Promise.all(
      dtos.map(async (dto) => ({
        ...dto,
        createdBy: userId,
        signature: await this.validationService.generateSignature(dto),
        encryptionVersion: 'v1',
      }))
    );

    await Promise.all(
      serials.map((serial) => this.validationService.validateSerial(serial))
    );

    return this.serialRepository.save(serials);
  }

  async findAll(pagination: PaginationDto, filters?: FindOptionsWhere<Serial>): Promise<[Serial[], number]> {
    const [serials, total] = await this.serialRepository.findAndCount({
      where: filters,
      skip: pagination.offset,
      take: pagination.limit,
      relations: ['client', 'usages'],
      order: { createdAt: 'DESC' },
    });

    return [serials, total];
  }

  async findOne(id: string): Promise<Serial> {
    const cached = await this.cacheService.get(`serial:${id}`);
    if (cached) {
      return cached;
    }

    const serial = await this.serialRepository.findOne({
      where: { id },
      relations: ['client', 'usages'],
    });

    if (!serial) {
      throw new NotFoundException(`Serial with ID ${id} not found`);
    }

    await this.cacheService.set(`serial:${id}`, serial);
    return serial;
  }

  async update(id: string, dto: UpdateSerialDto, userId: string): Promise<Serial> {
    const serial = await this.findOne(id);

    if (dto.serialNumber || dto.clientId) {
      throw new BadRequestException('Cannot update serial number or client');
    }

    Object.assign(serial, {
      ...dto,
      updatedBy: userId,
      signature: await this.validationService.generateSignature({
        ...serial,
        ...dto,
      }),
    });

    await this.validationService.validateSerial(serial);
    await this.cacheService.del(`serial:${id}`);
    
    return this.serialRepository.save(serial);
  }

  async delete(id: string, userId: string): Promise<void> {
    const serial = await this.findOne(id);
    serial.updatedBy = userId;
    await this.serialRepository.softRemove(serial);
    await this.cacheService.del(`serial:${id}`);
  }

  async validate(dto: ValidateSerialDto): Promise<boolean> {
    const serial = await this.serialRepository.findOne({
      where: { serialNumber: dto.serialNumber },
      relations: ['usages'],
    });

    if (!serial) {
      return false;
    }

    const isValid = await this.validationService.validateSerial(serial);
    if (!isValid) {
      return false;
    }

    // Create usage record
    const usage = this.usageRepository.create({
      serialId: serial.id,
      deviceId: dto.deviceId,
      ipAddress: dto.ipAddress,
      deviceInfo: dto.deviceInfo,
      status: 'active',
    });

    await this.usageRepository.save(usage);
    return true;
  }

  async revoke(id: string, userId: string): Promise<void> {
    const serial = await this.findOne(id);
    serial.isActive = false;
    serial.updatedBy = userId;
    await this.serialRepository.save(serial);
    await this.cacheService.del(`serial:${id}`);

    // Update all active usages
    await this.usageRepository.update(
      { serialId: id, status: 'active' },
      { status: 'revoked' }
    );
  }

  async renew(id: string, expirationDate: Date, userId: string): Promise<Serial> {
    const serial = await this.findOne(id);
    serial.expirationDate = expirationDate;
    serial.updatedBy = userId;
    serial.signature = await this.validationService.generateSignature(serial);

    await this.validationService.validateSerial(serial);
    await this.cacheService.del(`serial:${id}`);
    
    return this.serialRepository.save(serial);
  }

  async getUsageStats(id: string): Promise<{
    total: number;
    active: number;
    revoked: number;
    expired: number;
  }> {
    const usages = await this.usageRepository.find({
      where: { serialId: id },
    });

    return {
      total: usages.length,
      active: usages.filter((u) => u.status === 'active').length,
      revoked: usages.filter((u) => u.status === 'revoked').length,
      expired: usages.filter((u) => u.status === 'expired').length,
    };
  }

  async cleanupExpiredUsages(): Promise<void> {
    const expiredSerials = await this.serialRepository.find({
      where: {
        expirationDate: In([null, new Date()]),
        isActive: true,
      },
    });

    for (const serial of expiredSerials) {
      if (serial.expirationDate && serial.expirationDate < new Date()) {
        await this.usageRepository.update(
          { serialId: serial.id, status: 'active' },
          { status: 'expired' }
        );
      }
    }
  }
}
