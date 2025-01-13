import { Repository, EntityRepository, ObjectLiteral, FindOneOptions, FindManyOptions, DeepPartial } from 'typeorm';
import { NotFoundException } from '@nestjs/common';
import { LoggerService } from '../logger/logger.service';
import { CacheService } from '../cache/cache.service';
import { ConfigService } from '../config/config.service';
import { ValidationError } from '../errors';

@EntityRepository()
export class BaseRepository<T extends ObjectLiteral> extends Repository<T> {
  protected readonly CACHE_TTL = 300; // 5 minutes
  protected readonly CACHE_PREFIX: string;

  constructor(
    protected readonly logger: LoggerService,
    protected readonly cache: CacheService,
    protected readonly config: ConfigService
  ) {
    super();
    this.CACHE_PREFIX = `${this.metadata.name.toLowerCase()}:`;
  }

  /**
   * Finds an entity by ID with caching
   */
  async findByIdCached(id: string | number): Promise<T> {
    const cacheKey = `${this.CACHE_PREFIX}${id}`;
    
    // Try cache first
    const cached = await this.cache.get<T>(cacheKey);
    if (cached) {
      return cached;
    }

    // Get from database
    const entity = await this.findOne(id as any);
    if (!entity) {
      throw new NotFoundException(
        `${this.metadata.name} with id ${id} not found`
      );
    }

    // Cache for future use
    await this.cache.set(cacheKey, entity, this.CACHE_TTL);

    return entity;
  }

  /**
   * Creates a new entity with validation
   */
  async createEntity(data: DeepPartial<T>): Promise<T> {
    // Validate
    const errors = await this.validateEntity(data);
    if (errors.length > 0) {
      throw new ValidationError(
        `Invalid ${this.metadata.name} data`,
        errors
      );
    }

    // Create and save
    const entity = this.create(data);
    const saved = await this.save(entity);

    // Invalidate relevant caches
    await this.invalidateListCache();

    return saved;
  }

  /**
   * Updates an entity with validation
   */
  async updateEntity(
    id: string | number,
    data: DeepPartial<T>
  ): Promise<T> {
    const entity = await this.findOne(id as any);
    if (!entity) {
      throw new NotFoundException(
        `${this.metadata.name} with id ${id} not found`
      );
    }

    // Validate
    const errors = await this.validateEntity({ ...entity, ...data });
    if (errors.length > 0) {
      throw new ValidationError(
        `Invalid ${this.metadata.name} data`,
        errors
      );
    }

    // Update and save
    Object.assign(entity, data);
    const saved = await this.save(entity);

    // Invalidate caches
    await this.invalidateEntityCache(id);
    await this.invalidateListCache();

    return saved;
  }

  /**
   * Deletes an entity and cleans up caches
   */
  async deleteEntity(id: string | number): Promise<void> {
    const entity = await this.findOne(id as any);
    if (!entity) {
      throw new NotFoundException(
        `${this.metadata.name} with id ${id} not found`
      );
    }

    await this.remove(entity);

    // Invalidate caches
    await this.invalidateEntityCache(id);
    await this.invalidateListCache();
  }

  /**
   * Finds entities with caching
   */
  async findWithCache(
    options: FindManyOptions<T> = {},
    cacheKey?: string
  ): Promise<T[]> {
    const key = cacheKey || this.getListCacheKey(options);
    
    // Try cache first
    const cached = await this.cache.get<T[]>(key);
    if (cached) {
      return cached;
    }

    // Get from database
    const entities = await this.find(options);

    // Cache for future use
    await this.cache.set(key, entities, this.CACHE_TTL);

    return entities;
  }

  /**
   * Validates an entity
   */
  protected async validateEntity(data: DeepPartial<T>): Promise<string[]> {
    const errors: string[] = [];

    // Get validation metadata
    const validationMetadata = this.metadata.columns
      .filter(column => column.propertyName in data)
      .map(column => ({
        name: column.propertyName,
        type: column.type,
        isNullable: column.isNullable,
        length: column.length
      }));

    // Validate each field
    for (const meta of validationMetadata) {
      const value = data[meta.name];

      // Required check
      if (!meta.isNullable && (value === undefined || value === null)) {
        errors.push(`${meta.name} is required`);
        continue;
      }

      // Type check
      if (value !== undefined && value !== null) {
        switch (meta.type) {
          case String:
            if (typeof value !== 'string') {
              errors.push(`${meta.name} must be a string`);
            } else if (meta.length && value.length > meta.length) {
              errors.push(
                `${meta.name} must be at most ${meta.length} characters`
              );
            }
            break;

          case Number:
            if (typeof value !== 'number') {
              errors.push(`${meta.name} must be a number`);
            }
            break;

          case Boolean:
            if (typeof value !== 'boolean') {
              errors.push(`${meta.name} must be a boolean`);
            }
            break;

          case Date:
            if (!(value instanceof Date) && isNaN(Date.parse(value))) {
              errors.push(`${meta.name} must be a valid date`);
            }
            break;
        }
      }
    }

    return errors;
  }

  /**
   * Gets cache key for entity lists
   */
  protected getListCacheKey(options: FindManyOptions<T>): string {
    return `${this.CACHE_PREFIX}list:${JSON.stringify(options)}`;
  }

  /**
   * Invalidates entity cache
   */
  protected async invalidateEntityCache(id: string | number): Promise<void> {
    await this.cache.delete(`${this.CACHE_PREFIX}${id}`);
  }

  /**
   * Invalidates list cache
   */
  protected async invalidateListCache(): Promise<void> {
    await this.cache.deletePattern(`${this.CACHE_PREFIX}list:*`);
  }
}
