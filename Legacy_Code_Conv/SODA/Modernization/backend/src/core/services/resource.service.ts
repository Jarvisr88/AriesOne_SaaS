import { injectable, inject } from 'inversify';
import { SodaClient } from '../http/soda-client';
import { CacheService } from '../cache/cache.service';
import { LoggerService } from '../logger/logger.service';
import { ConfigService } from '../config/config.service';
import { Resource } from '../../domain/entities/resource.entity';
import { ResourceMetadata } from '../../domain/entities/resource-metadata.entity';
import { SoqlQueryBuilder } from '../query/soql-query-builder';
import { CreateResourceDto, UpdateResourceDto, ResourceQueryDto } from '../../domain/dtos/resource.dto';
import { ValidationError } from '../errors';

@injectable()
export class ResourceService {
  private readonly cachePrefix = 'resource:';
  private readonly cacheTTL: number;

  constructor(
    @inject(SodaClient) private readonly client: SodaClient,
    @inject(CacheService) private readonly cache: CacheService,
    @inject(LoggerService) private readonly logger: LoggerService,
    @inject(ConfigService) private readonly config: ConfigService,
    @inject(SoqlQueryBuilder) private readonly queryBuilder: SoqlQueryBuilder
  ) {
    this.cacheTTL = this.config.get('soda.cacheTTL', 3600);
  }

  async createResource(dto: CreateResourceDto): Promise<Resource> {
    this.logger.debug('Creating resource', { dto });

    const resource = new Resource({
      ...dto,
      id: crypto.randomUUID(),
      createdAt: new Date(),
      updatedAt: new Date()
    });

    const errors = resource.validate();
    if (errors.length > 0) {
      throw new ValidationError('Resource validation failed', errors);
    }

    try {
      await this.client.execute({
        method: 'POST',
        endpoint: '/api/resources',
        data: resource.toJSON(),
        requestId: crypto.randomUUID()
      });

      await this.cache.set(
        `${this.cachePrefix}${resource.id}`,
        resource,
        this.cacheTTL
      );

      this.logger.info('Resource created', { resourceId: resource.id });
      return resource;
    } catch (error) {
      this.logger.error('Failed to create resource', { error, dto });
      throw error;
    }
  }

  async getResource(id: string): Promise<Resource> {
    this.logger.debug('Getting resource', { id });

    const cacheKey = `${this.cachePrefix}${id}`;
    const cached = await this.cache.get<Resource>(cacheKey);
    if (cached) {
      this.logger.debug('Resource found in cache', { id });
      return new Resource(cached);
    }

    try {
      const result = await this.client.execute<Resource>({
        method: 'GET',
        endpoint: `/api/resources/${id}`,
        requestId: crypto.randomUUID()
      });

      const resource = new Resource(result.data);
      await this.cache.set(cacheKey, resource, this.cacheTTL);

      this.logger.debug('Resource fetched', { id });
      return resource;
    } catch (error) {
      this.logger.error('Failed to get resource', { error, id });
      throw error;
    }
  }

  async updateResource(id: string, dto: UpdateResourceDto): Promise<Resource> {
    this.logger.debug('Updating resource', { id, dto });

    const resource = await this.getResource(id);
    resource.update(dto);

    const errors = resource.validate();
    if (errors.length > 0) {
      throw new ValidationError('Resource validation failed', errors);
    }

    try {
      await this.client.execute({
        method: 'PUT',
        endpoint: `/api/resources/${id}`,
        data: resource.toJSON(),
        requestId: crypto.randomUUID()
      });

      await this.cache.delete(`${this.cachePrefix}${id}`);

      this.logger.info('Resource updated', { id });
      return resource;
    } catch (error) {
      this.logger.error('Failed to update resource', { error, id, dto });
      throw error;
    }
  }

  async deleteResource(id: string): Promise<void> {
    this.logger.debug('Deleting resource', { id });

    try {
      await this.client.execute({
        method: 'DELETE',
        endpoint: `/api/resources/${id}`,
        requestId: crypto.randomUUID()
      });

      await this.cache.delete(`${this.cachePrefix}${id}`);
      this.logger.info('Resource deleted', { id });
    } catch (error) {
      this.logger.error('Failed to delete resource', { error, id });
      throw error;
    }
  }

  async queryResource<T>(id: string, query: ResourceQueryDto): Promise<T[]> {
    this.logger.debug('Querying resource', { id, query });

    const resource = await this.getResource(id);
    this.queryBuilder.setColumns(resource.columns);

    if (query.select) {
      this.queryBuilder.select(query.select);
    }

    if (query.where) {
      query.where.forEach(clause => {
        this.queryBuilder.where(clause);
      });
    }

    if (query.orderBy) {
      this.queryBuilder.orderBy(
        query.orderBy.field,
        query.orderBy.direction
      );
    }

    if (query.limit) {
      this.queryBuilder.limit(query.limit);
    }

    if (query.offset) {
      this.queryBuilder.offset(query.offset);
    }

    const errors = this.queryBuilder.validate();
    if (errors.length > 0) {
      throw new ValidationError('Query validation failed', errors);
    }

    const soqlQuery = this.queryBuilder.build();
    const cacheKey = `${this.cachePrefix}${id}:query:${soqlQuery}`;

    try {
      const cached = await this.cache.get<T[]>(cacheKey);
      if (cached) {
        this.logger.debug('Query results found in cache', { id, query });
        return cached;
      }

      const result = await this.client.execute<T[]>({
        method: 'GET',
        endpoint: `/api/resources/${id}/query`,
        params: { $query: soqlQuery },
        requestId: crypto.randomUUID()
      });

      await this.cache.set(cacheKey, result.data, this.cacheTTL);
      return result.data;
    } catch (error) {
      this.logger.error('Failed to query resource', { error, id, query });
      throw error;
    }
  }

  async bulkUpload(id: string, data: any[]): Promise<void> {
    this.logger.debug('Bulk uploading data', { id, count: data.length });

    const resource = await this.getResource(id);
    const errors: string[] = [];

    // Validate each row
    data.forEach((row, index) => {
      resource.columns.forEach(column => {
        const value = row[column.name];
        const validationErrors = column.validateValue(value);
        if (validationErrors.length > 0) {
          errors.push(`Row ${index + 1}, Column ${column.name}: ${validationErrors.join(', ')}`);
        }
      });
    });

    if (errors.length > 0) {
      throw new ValidationError('Bulk upload validation failed', errors);
    }

    try {
      // Upload in batches of 1000
      const batchSize = 1000;
      for (let i = 0; i < data.length; i += batchSize) {
        const batch = data.slice(i, i + batchSize);
        await this.client.execute({
          method: 'POST',
          endpoint: `/api/resources/${id}/bulk`,
          data: batch,
          requestId: crypto.randomUUID()
        });
      }

      // Invalidate cache
      await this.cache.deletePattern(`${this.cachePrefix}${id}:*`);
      
      // Update metadata
      const metadata = resource.metadata;
      metadata.updateRowCount(metadata.rowCount + data.length);
      await this.updateResource(id, { metadata });

      this.logger.info('Bulk upload completed', { 
        id, 
        count: data.length 
      });
    } catch (error) {
      this.logger.error('Failed to bulk upload data', { 
        error, 
        id, 
        count: data.length 
      });
      throw error;
    }
  }

  async getMetadata(id: string): Promise<ResourceMetadata> {
    this.logger.debug('Getting resource metadata', { id });

    const cacheKey = `${this.cachePrefix}${id}:metadata`;
    const cached = await this.cache.get<ResourceMetadata>(cacheKey);
    if (cached) {
      return new ResourceMetadata(cached);
    }

    try {
      const result = await this.client.execute<ResourceMetadata>({
        method: 'GET',
        endpoint: `/api/resources/${id}/metadata`,
        requestId: crypto.randomUUID()
      });

      const metadata = new ResourceMetadata(result.data);
      await this.cache.set(cacheKey, metadata, this.cacheTTL);

      return metadata;
    } catch (error) {
      this.logger.error('Failed to get resource metadata', { error, id });
      throw error;
    }
  }

  async validateResource(id: string): Promise<string[]> {
    this.logger.debug('Validating resource', { id });

    try {
      const resource = await this.getResource(id);
      return resource.validate();
    } catch (error) {
      this.logger.error('Failed to validate resource', { error, id });
      throw error;
    }
  }
}
