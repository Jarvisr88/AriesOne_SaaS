import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, FindOptionsWhere } from 'typeorm';
import { Client } from '../entities/client.entity';
import { ValidationService } from './validation.service';
import { CacheService } from './cache.service';
import { CreateClientDto, UpdateClientDto } from '../dto/client.dto';
import { PaginationDto } from '../dto/common.dto';

@Injectable()
export class ClientService {
  constructor(
    @InjectRepository(Client)
    private clientRepository: Repository<Client>,
    private validationService: ValidationService,
    private cacheService: CacheService,
  ) {}

  async create(dto: CreateClientDto, userId: string): Promise<Client> {
    await this.validationService.validateClientNumber(dto.clientNumber);

    const client = this.clientRepository.create({
      ...dto,
      createdBy: userId,
    });

    return this.clientRepository.save(client);
  }

  async findAll(pagination: PaginationDto, filters?: FindOptionsWhere<Client>): Promise<[Client[], number]> {
    const [clients, total] = await this.clientRepository.findAndCount({
      where: filters,
      skip: pagination.offset,
      take: pagination.limit,
      relations: ['serials'],
      order: { createdAt: 'DESC' },
    });

    return [clients, total];
  }

  async findOne(id: string): Promise<Client> {
    const cached = await this.cacheService.get(`client:${id}`);
    if (cached) {
      return cached;
    }

    const client = await this.clientRepository.findOne({
      where: { id },
      relations: ['serials'],
    });

    if (!client) {
      throw new NotFoundException(`Client with ID ${id} not found`);
    }

    await this.cacheService.set(`client:${id}`, client);
    return client;
  }

  async update(id: string, dto: UpdateClientDto, userId: string): Promise<Client> {
    const client = await this.findOne(id);

    if (dto.clientNumber) {
      await this.validationService.validateClientNumber(dto.clientNumber);
    }

    Object.assign(client, {
      ...dto,
      updatedBy: userId,
    });

    await this.cacheService.del(`client:${id}`);
    return this.clientRepository.save(client);
  }

  async delete(id: string, userId: string): Promise<void> {
    const client = await this.findOne(id);
    client.updatedBy = userId;
    await this.clientRepository.softRemove(client);
    await this.cacheService.del(`client:${id}`);
  }

  async getSerialStats(id: string): Promise<{
    total: number;
    active: number;
    expired: number;
    demo: number;
  }> {
    const client = await this.findOne(id);
    const serials = client.serials || [];

    return {
      total: serials.length,
      active: serials.filter((s) => s.isActive && !s.isDemo).length,
      expired: serials.filter((s) => s.expirationDate && s.expirationDate < new Date()).length,
      demo: serials.filter((s) => s.isDemo).length,
    };
  }

  async search(query: string, pagination: PaginationDto): Promise<[Client[], number]> {
    const [clients, total] = await this.clientRepository
      .createQueryBuilder('client')
      .where('client.name ILIKE :query OR client.clientNumber ILIKE :query', {
        query: `%${query}%`,
      })
      .skip(pagination.offset)
      .take(pagination.limit)
      .getManyAndCount();

    return [clients, total];
  }
}
