import { Container } from 'inversify';
import { mock, instance, when, verify, anything, reset } from 'ts-mockito';
import { ResourceService } from '../../../../src/core/services/resource.service';
import { SodaClient } from '../../../../src/core/http/soda-client';
import { CacheService } from '../../../../src/core/cache/cache.service';
import { LoggerService } from '../../../../src/core/logger/logger.service';
import { ConfigService } from '../../../../src/core/config/config.service';
import { SoqlQueryBuilder } from '../../../../src/core/query/soql-query-builder';
import { Resource } from '../../../../src/domain/entities/resource.entity';
import { Column } from '../../../../src/domain/entities/column.entity';
import { ResourceMetadata } from '../../../../src/domain/entities/resource-metadata.entity';
import { DataType } from '../../../../src/domain/enums/data-type.enum';
import { ValidationError, ResourceNotFoundError } from '../../../../src/core/errors';

describe('ResourceService', () => {
  let container: Container;
  let resourceService: ResourceService;
  let mockSodaClient: SodaClient;
  let mockCacheService: CacheService;
  let mockLoggerService: LoggerService;
  let mockConfigService: ConfigService;
  let mockQueryBuilder: SoqlQueryBuilder;

  beforeEach(() => {
    container = new Container();
    mockSodaClient = mock(SodaClient);
    mockCacheService = mock(CacheService);
    mockLoggerService = mock(LoggerService);
    mockConfigService = mock(ConfigService);
    mockQueryBuilder = mock(SoqlQueryBuilder);

    container.bind(ResourceService).toSelf();
    container.bind(SodaClient).toConstantValue(instance(mockSodaClient));
    container.bind(CacheService).toConstantValue(instance(mockCacheService));
    container.bind(LoggerService).toConstantValue(instance(mockLoggerService));
    container.bind(ConfigService).toConstantValue(instance(mockConfigService));
    container.bind(SoqlQueryBuilder).toConstantValue(instance(mockQueryBuilder));

    when(mockConfigService.get('soda.cacheTTL', anything())).thenReturn(3600);
    resourceService = container.get(ResourceService);
  });

  afterEach(() => {
    reset(mockSodaClient);
    reset(mockCacheService);
    reset(mockLoggerService);
    reset(mockConfigService);
    reset(mockQueryBuilder);
  });

  describe('createResource', () => {
    const createResourceDto = {
      name: 'Test Resource',
      description: 'Test Description',
      columns: [
        {
          name: 'id',
          dataType: DataType.TEXT,
          required: true
        }
      ],
      metadata: {
        tags: ['test'],
        customFields: {}
      }
    };

    it('should create a resource successfully', async () => {
      when(mockSodaClient.execute(anything())).thenResolve({ data: {} });
      when(mockCacheService.set(anything(), anything(), anything())).thenResolve();

      const result = await resourceService.createResource(createResourceDto);

      expect(result).toBeInstanceOf(Resource);
      expect(result.name).toBe(createResourceDto.name);
      verify(mockSodaClient.execute(anything())).once();
      verify(mockCacheService.set(anything(), anything(), anything())).once();
    });

    it('should throw ValidationError for invalid resource', async () => {
      const invalidDto = {
        ...createResourceDto,
        name: ''
      };

      await expect(resourceService.createResource(invalidDto))
        .rejects
        .toThrow(ValidationError);
    });
  });

  describe('getResource', () => {
    const resourceId = 'test-id';
    const mockResource = {
      id: resourceId,
      name: 'Test Resource',
      columns: [],
      metadata: {},
      createdAt: new Date(),
      updatedAt: new Date()
    };

    it('should return cached resource if available', async () => {
      when(mockCacheService.get(`resource:${resourceId}`))
        .thenResolve(mockResource);

      const result = await resourceService.getResource(resourceId);

      expect(result).toBeInstanceOf(Resource);
      expect(result.id).toBe(resourceId);
      verify(mockSodaClient.execute(anything())).never();
    });

    it('should fetch and cache resource if not in cache', async () => {
      when(mockCacheService.get(`resource:${resourceId}`))
        .thenResolve(null);
      when(mockSodaClient.execute(anything()))
        .thenResolve({ data: mockResource });
      when(mockCacheService.set(anything(), anything(), anything()))
        .thenResolve();

      const result = await resourceService.getResource(resourceId);

      expect(result).toBeInstanceOf(Resource);
      expect(result.id).toBe(resourceId);
      verify(mockSodaClient.execute(anything())).once();
      verify(mockCacheService.set(anything(), anything(), anything())).once();
    });

    it('should throw ResourceNotFoundError for non-existent resource', async () => {
      when(mockCacheService.get(`resource:${resourceId}`))
        .thenResolve(null);
      when(mockSodaClient.execute(anything()))
        .thenReject(new ResourceNotFoundError(resourceId));

      await expect(resourceService.getResource(resourceId))
        .rejects
        .toThrow(ResourceNotFoundError);
    });
  });

  describe('queryResource', () => {
    const resourceId = 'test-id';
    const mockResource = new Resource({
      id: resourceId,
      name: 'Test Resource',
      columns: [
        new Column({
          name: 'id',
          dataType: DataType.TEXT,
          required: true
        })
      ],
      metadata: new ResourceMetadata({
        tags: ['test'],
        customFields: {}
      }),
      createdAt: new Date(),
      updatedAt: new Date()
    });

    const queryDto = {
      select: ['id'],
      where: [
        {
          field: 'id',
          operator: 'EQ',
          value: 'test'
        }
      ],
      orderBy: {
        field: 'id',
        direction: 'ASC' as const
      },
      limit: 10,
      offset: 0
    };

    it('should execute query successfully', async () => {
      when(mockCacheService.get(anything())).thenResolve(null);
      when(mockSodaClient.execute(anything())).thenResolve({ data: [] });
      when(mockQueryBuilder.validate()).thenReturn([]);
      when(mockQueryBuilder.build()).thenReturn('SELECT id WHERE id = "test"');

      const result = await resourceService.queryResource(resourceId, queryDto);

      expect(Array.isArray(result)).toBe(true);
      verify(mockQueryBuilder.setColumns(anything())).once();
      verify(mockQueryBuilder.select(queryDto.select)).once();
      verify(mockQueryBuilder.where(queryDto.where[0])).once();
      verify(mockQueryBuilder.orderBy(queryDto.orderBy.field, queryDto.orderBy.direction)).once();
      verify(mockQueryBuilder.limit(queryDto.limit)).once();
      verify(mockQueryBuilder.offset(queryDto.offset)).once();
    });

    it('should return cached query results if available', async () => {
      const cachedResults = [{ id: 'test' }];
      when(mockCacheService.get(anything())).thenResolve(cachedResults);

      const result = await resourceService.queryResource(resourceId, queryDto);

      expect(result).toEqual(cachedResults);
      verify(mockSodaClient.execute(anything())).never();
    });

    it('should throw ValidationError for invalid query', async () => {
      when(mockQueryBuilder.validate()).thenReturn(['Invalid field']);

      await expect(resourceService.queryResource(resourceId, queryDto))
        .rejects
        .toThrow(ValidationError);
    });
  });

  describe('bulkUpload', () => {
    const resourceId = 'test-id';
    const mockData = [
      { id: '1', name: 'Test 1' },
      { id: '2', name: 'Test 2' }
    ];

    it('should upload data in batches', async () => {
      when(mockSodaClient.execute(anything())).thenResolve({ data: {} });
      when(mockCacheService.deletePattern(anything())).thenResolve();

      await resourceService.bulkUpload(resourceId, mockData);

      verify(mockSodaClient.execute(anything())).once();
      verify(mockCacheService.deletePattern(`resource:${resourceId}:*`)).once();
    });

    it('should validate data before upload', async () => {
      const invalidData = [
        { id: '', name: 'Test 1' },
        { id: '2', name: '' }
      ];

      await expect(resourceService.bulkUpload(resourceId, invalidData))
        .rejects
        .toThrow(ValidationError);
    });
  });
});
