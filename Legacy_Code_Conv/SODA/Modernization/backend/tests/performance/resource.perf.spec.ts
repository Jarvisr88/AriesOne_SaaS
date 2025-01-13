import { Container } from 'inversify';
import { Express } from 'express';
import autocannon from 'autocannon';
import { createTestApp } from '../utils/test-app';
import { ResourceService } from '../../src/core/services/resource.service';
import { AuthService } from '../../src/core/auth/auth.service';
import { Resource } from '../../src/domain/entities/resource.entity';
import { DataType } from '../../src/domain/enums/data-type.enum';

describe('Resource Performance Tests', () => {
  let app: Express;
  let container: Container;
  let resourceService: ResourceService;
  let authService: AuthService;
  let authToken: string;
  let testResource: Resource;
  let server: any;

  beforeAll(async () => {
    ({ app, container } = await createTestApp());
    resourceService = container.get(ResourceService);
    authService = container.get(AuthService);

    // Generate test auth token
    authToken = await authService.generateToken({
      userId: 'test-user',
      roles: ['admin']
    });

    // Create test resource
    testResource = await resourceService.createResource({
      name: 'Performance Test Resource',
      description: 'Resource for performance testing',
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
        tags: ['performance-test'],
        customFields: {}
      }
    });

    // Upload test data
    const testData = Array.from({ length: 10000 }, (_, i) => ({
      id: `id-${i}`,
      value: i
    }));
    await resourceService.bulkUpload(testResource.id, testData);

    // Start server
    server = app.listen(0);
  });

  afterAll(async () => {
    server.close();
  });

  const runLoadTest = (
    url: string,
    method: 'GET' | 'POST',
    payload?: any
  ): Promise<autocannon.Result> => {
    return new Promise((resolve, reject) => {
      const instance = autocannon({
        url: `http://localhost:${(server.address() as any).port}${url}`,
        connections: 10,
        pipelining: 1,
        duration: 10,
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        method,
        body: payload ? JSON.stringify(payload) : undefined,
        requests: [
          {
            method,
            path: url,
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json'
            },
            body: payload ? JSON.stringify(payload) : undefined
          }
        ]
      }, (err, result) => {
        if (err) reject(err);
        else resolve(result);
      });

      autocannon.track(instance);
    });
  };

  describe('GET /api/resources/:id', () => {
    it('should handle high throughput for single resource retrieval', async () => {
      const result = await runLoadTest(
        `/api/resources/${testResource.id}`,
        'GET'
      );

      expect(result.errors).toBe(0);
      expect(result.timeouts).toBe(0);
      expect(result.non2xx).toBe(0);
      expect(result.latency.p99).toBeLessThan(100); // 100ms
    });
  });

  describe('POST /api/resources/:id/query', () => {
    it('should handle complex queries efficiently', async () => {
      const queryDto = {
        select: ['id', 'value'],
        where: [
          {
            field: 'value',
            operator: 'GT',
            value: 5000
          }
        ],
        orderBy: {
          field: 'value',
          direction: 'ASC'
        },
        limit: 100
      };

      const result = await runLoadTest(
        `/api/resources/${testResource.id}/query`,
        'POST',
        queryDto
      );

      expect(result.errors).toBe(0);
      expect(result.timeouts).toBe(0);
      expect(result.non2xx).toBe(0);
      expect(result.latency.p99).toBeLessThan(200); // 200ms
    });

    it('should handle pagination efficiently', async () => {
      const results = await Promise.all(
        Array.from({ length: 5 }, (_, i) => ({
          limit: 20,
          offset: i * 20
        })).map(queryDto =>
          runLoadTest(
            `/api/resources/${testResource.id}/query`,
            'POST',
            queryDto
          )
        )
      );

      results.forEach(result => {
        expect(result.errors).toBe(0);
        expect(result.timeouts).toBe(0);
        expect(result.non2xx).toBe(0);
        expect(result.latency.p99).toBeLessThan(150); // 150ms
      });
    });
  });

  describe('POST /api/resources/:id/bulk', () => {
    it('should handle large bulk uploads efficiently', async () => {
      const bulkData = Array.from({ length: 1000 }, (_, i) => ({
        id: `bulk-${i}`,
        value: i
      }));

      const result = await runLoadTest(
        `/api/resources/${testResource.id}/bulk`,
        'POST',
        bulkData
      );

      expect(result.errors).toBe(0);
      expect(result.timeouts).toBe(0);
      expect(result.non2xx).toBe(0);
      expect(result.latency.p99).toBeLessThan(1000); // 1s
    });
  });

  describe('Cache Performance', () => {
    it('should improve response times for cached resources', async () => {
      // First request (uncached)
      const uncachedResult = await runLoadTest(
        `/api/resources/${testResource.id}`,
        'GET'
      );

      // Second request (cached)
      const cachedResult = await runLoadTest(
        `/api/resources/${testResource.id}`,
        'GET'
      );

      expect(cachedResult.latency.p50).toBeLessThan(uncachedResult.latency.p50);
    });
  });

  describe('Query Builder Performance', () => {
    it('should handle complex filters efficiently', async () => {
      const complexQuery = {
        select: ['id', 'value'],
        where: [
          {
            field: 'value',
            operator: 'GT',
            value: 1000
          },
          {
            field: 'value',
            operator: 'LT',
            value: 5000
          }
        ],
        orderBy: {
          field: 'value',
          direction: 'DESC'
        }
      };

      const result = await runLoadTest(
        `/api/resources/${testResource.id}/query`,
        'POST',
        complexQuery
      );

      expect(result.errors).toBe(0);
      expect(result.latency.p99).toBeLessThan(300); // 300ms
    });
  });
});
