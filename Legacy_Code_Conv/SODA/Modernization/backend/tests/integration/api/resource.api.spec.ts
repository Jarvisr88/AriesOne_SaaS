import { Container } from 'inversify';
import { Express } from 'express';
import request from 'supertest';
import { createTestApp } from '../../utils/test-app';
import { ResourceService } from '../../../src/core/services/resource.service';
import { AuthService } from '../../../src/core/auth/auth.service';
import { Resource } from '../../../src/domain/entities/resource.entity';
import { DataType } from '../../../src/domain/enums/data-type.enum';

describe('Resource API Integration Tests', () => {
  let app: Express;
  let container: Container;
  let resourceService: ResourceService;
  let authService: AuthService;
  let authToken: string;

  beforeAll(async () => {
    ({ app, container } = await createTestApp());
    resourceService = container.get(ResourceService);
    authService = container.get(AuthService);

    // Generate test auth token
    authToken = await authService.generateToken({
      userId: 'test-user',
      roles: ['admin']
    });
  });

  describe('POST /api/resources', () => {
    const createResourceDto = {
      name: 'Test Resource',
      description: 'Test Description',
      columns: [
        {
          name: 'id',
          dataType: DataType.TEXT,
          required: true
        },
        {
          name: 'name',
          dataType: DataType.TEXT,
          required: true
        }
      ],
      metadata: {
        tags: ['test'],
        customFields: {}
      }
    };

    it('should create resource successfully', async () => {
      const response = await request(app)
        .post('/api/resources')
        .set('Authorization', `Bearer ${authToken}`)
        .send(createResourceDto)
        .expect(201);

      expect(response.body).toMatchObject({
        name: createResourceDto.name,
        description: createResourceDto.description
      });
      expect(response.body.id).toBeDefined();
    });

    it('should return 400 for invalid resource', async () => {
      const invalidDto = {
        ...createResourceDto,
        name: ''
      };

      const response = await request(app)
        .post('/api/resources')
        .set('Authorization', `Bearer ${authToken}`)
        .send(invalidDto)
        .expect(400);

      expect(response.body.errors).toBeDefined();
    });

    it('should return 401 without auth token', async () => {
      await request(app)
        .post('/api/resources')
        .send(createResourceDto)
        .expect(401);
    });
  });

  describe('GET /api/resources/:id', () => {
    let testResource: Resource;

    beforeEach(async () => {
      testResource = await resourceService.createResource({
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
      });
    });

    it('should return resource by id', async () => {
      const response = await request(app)
        .get(`/api/resources/${testResource.id}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.id).toBe(testResource.id);
      expect(response.body.name).toBe(testResource.name);
    });

    it('should return 404 for non-existent resource', async () => {
      await request(app)
        .get('/api/resources/non-existent')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);
    });
  });

  describe('POST /api/resources/:id/query', () => {
    let testResource: Resource;

    beforeEach(async () => {
      testResource = await resourceService.createResource({
        name: 'Test Resource',
        description: 'Test Description',
        columns: [
          {
            name: 'id',
            dataType: DataType.TEXT,
            required: true
          },
          {
            name: 'value',
            dataType: DataType.NUMBER,
            required: false
          }
        ],
        metadata: {
          tags: ['test'],
          customFields: {}
        }
      });

      // Add test data
      await resourceService.bulkUpload(testResource.id, [
        { id: '1', value: 100 },
        { id: '2', value: 200 },
        { id: '3', value: 300 }
      ]);
    });

    it('should query resource data successfully', async () => {
      const queryDto = {
        select: ['id', 'value'],
        where: [
          {
            field: 'value',
            operator: 'GT',
            value: 150
          }
        ],
        orderBy: {
          field: 'value',
          direction: 'ASC' as const
        }
      };

      const response = await request(app)
        .post(`/api/resources/${testResource.id}/query`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(queryDto)
        .expect(200);

      expect(response.body.data).toHaveLength(2);
      expect(response.body.data[0].value).toBe(200);
      expect(response.body.data[1].value).toBe(300);
    });

    it('should handle pagination', async () => {
      const queryDto = {
        limit: 2,
        offset: 0
      };

      const response = await request(app)
        .post(`/api/resources/${testResource.id}/query`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(queryDto)
        .expect(200);

      expect(response.body.data).toHaveLength(2);
      expect(response.body.metadata.total).toBe(3);
      expect(response.body._links.next).toBeDefined();
    });

    it('should return 400 for invalid query', async () => {
      const invalidQuery = {
        where: [
          {
            field: 'non_existent',
            operator: 'EQ',
            value: 'test'
          }
        ]
      };

      await request(app)
        .post(`/api/resources/${testResource.id}/query`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(invalidQuery)
        .expect(400);
    });
  });

  describe('POST /api/resources/:id/bulk', () => {
    let testResource: Resource;

    beforeEach(async () => {
      testResource = await resourceService.createResource({
        name: 'Test Resource',
        description: 'Test Description',
        columns: [
          {
            name: 'id',
            dataType: DataType.TEXT,
            required: true
          },
          {
            name: 'value',
            dataType: DataType.NUMBER,
            required: true
          }
        ],
        metadata: {
          tags: ['test'],
          customFields: {}
        }
      });
    });

    it('should upload bulk data successfully', async () => {
      const bulkData = [
        { id: '1', value: 100 },
        { id: '2', value: 200 }
      ];

      await request(app)
        .post(`/api/resources/${testResource.id}/bulk`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(bulkData)
        .expect(200);

      const response = await request(app)
        .get(`/api/resources/${testResource.id}`)
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.body.metadata.rowCount).toBe(2);
    });

    it('should return 400 for invalid data', async () => {
      const invalidData = [
        { id: '1' }, // Missing required value
        { id: '2', value: 'not a number' }
      ];

      const response = await request(app)
        .post(`/api/resources/${testResource.id}/bulk`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(invalidData)
        .expect(400);

      expect(response.body.errors).toBeDefined();
    });

    it('should handle large datasets with rate limiting', async () => {
      const largeData = Array.from({ length: 1000 }, (_, i) => ({
        id: `id-${i}`,
        value: i
      }));

      await request(app)
        .post(`/api/resources/${testResource.id}/bulk`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(largeData)
        .expect(200);
    });
  });
});
