import * as autocannon from 'autocannon';
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import { AppModule } from '../../app.module';

describe('Serial Performance Tests', () => {
  let app: INestApplication;
  let url: string;
  let jwtToken: string;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    // Get test JWT token
    // This should be replaced with actual token generation in your app
    jwtToken = 'test.jwt.token';

    const server = app.getHttpServer();
    const address = server.address();
    url = `http://localhost:${address.port}`;
  });

  afterAll(async () => {
    await app.close();
  });

  const runBenchmark = (
    title: string,
    path: string,
    method = 'GET',
    payload?: any
  ): Promise<autocannon.Result> => {
    const instance = autocannon({
      title,
      url: `${url}${path}`,
      connections: 10,
      pipelining: 1,
      duration: 10,
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json',
      },
      method,
      body: payload ? JSON.stringify(payload) : undefined,
    });

    autocannon.track(instance);

    return new Promise((resolve) => {
      instance.on('done', resolve);
    });
  };

  describe('Serial Validation Performance', () => {
    it('should handle high volume of validation requests', async () => {
      const result = await runBenchmark(
        'Serial Validation',
        '/serials/validate',
        'POST',
        {
          serialNumber: 'TEST123-456',
          deviceId: 'device123',
          deviceInfo: { os: 'linux', version: '1.0' },
        }
      );

      expect(result.non2xx).toBe(0);
      expect(result.errors).toBe(0);
      expect(result.timeouts).toBe(0);
      expect(result.latency.p99).toBeLessThan(100); // 100ms
    });
  });

  describe('Serial Creation Performance', () => {
    it('should handle bulk serial creation efficiently', async () => {
      const result = await runBenchmark(
        'Bulk Serial Creation',
        '/serials/bulk',
        'POST',
        {
          clientId: 'test-client',
          count: 100,
          maxUsageCount: 5,
        }
      );

      expect(result.non2xx).toBe(0);
      expect(result.errors).toBe(0);
      expect(result.timeouts).toBe(0);
      expect(result.latency.p95).toBeLessThan(500); // 500ms
    });
  });

  describe('Serial Query Performance', () => {
    it('should handle concurrent read requests efficiently', async () => {
      const result = await runBenchmark(
        'Serial Queries',
        '/serials?limit=50'
      );

      expect(result.non2xx).toBe(0);
      expect(result.errors).toBe(0);
      expect(result.timeouts).toBe(0);
      expect(result.latency.average).toBeLessThan(50); // 50ms
    });

    it('should handle filtered queries efficiently', async () => {
      const result = await runBenchmark(
        'Filtered Queries',
        '/serials?isActive=true&isDemo=false&limit=50'
      );

      expect(result.non2xx).toBe(0);
      expect(result.errors).toBe(0);
      expect(result.timeouts).toBe(0);
      expect(result.latency.p95).toBeLessThan(100); // 100ms
    });
  });

  describe('Cache Performance', () => {
    it('should serve cached responses quickly', async () => {
      // First request to populate cache
      await runBenchmark(
        'Cache Warm-up',
        '/serials/TEST123-456'
      );

      // Benchmark cached responses
      const result = await runBenchmark(
        'Cached Responses',
        '/serials/TEST123-456'
      );

      expect(result.non2xx).toBe(0);
      expect(result.errors).toBe(0);
      expect(result.timeouts).toBe(0);
      expect(result.latency.average).toBeLessThan(10); // 10ms
    });
  });

  describe('Load Testing', () => {
    it('should handle sustained load', async () => {
      const result = await runBenchmark(
        'Sustained Load',
        '/serials/validate',
        'POST',
        {
          serialNumber: 'TEST123-456',
          deviceId: 'device123',
          deviceInfo: { os: 'linux', version: '1.0' },
        }
      );

      const stats = {
        totalRequests: result.requests.total,
        throughput: result.requests.average,
        averageLatency: result.latency.average,
        errorRate: (result.non2xx / result.requests.total) * 100,
      };

      expect(stats.throughput).toBeGreaterThan(1000); // 1000 req/sec
      expect(stats.averageLatency).toBeLessThan(50); // 50ms
      expect(stats.errorRate).toBeLessThan(0.1); // 0.1% error rate
    });
  });

  describe('Stress Testing', () => {
    it('should handle spike in traffic', async () => {
      const instance = autocannon({
        title: 'Traffic Spike',
        url: `${url}/serials/validate`,
        connections: 100,
        pipelining: 10,
        duration: 5,
        headers: {
          'Authorization': `Bearer ${jwtToken}`,
          'Content-Type': 'application/json',
        },
        method: 'POST',
        body: JSON.stringify({
          serialNumber: 'TEST123-456',
          deviceId: 'device123',
          deviceInfo: { os: 'linux', version: '1.0' },
        }),
      });

      const result = await new Promise<autocannon.Result>((resolve) => {
        instance.on('done', resolve);
      });

      expect(result.non2xx).toBeLessThan(result.requests.total * 0.01); // 1% error rate
      expect(result.timeouts).toBeLessThan(result.requests.total * 0.01); // 1% timeout rate
    });
  });
});
