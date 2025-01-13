import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { injectable, inject } from 'inversify';
import { ConfigService } from '../config/config.service';
import { LoggerService } from '../logger/logger.service';
import { CacheService } from '../cache/cache.service';
import { SodaError, ValidationError, AuthenticationError, RateLimitError } from '../errors';
import { SodaRequest, SodaResult, ResourceMetadata, RawData } from '../types';

@injectable()
export class SodaClient {
  private readonly client: AxiosInstance;
  private readonly baseUrl: string;
  private readonly appToken: string;

  constructor(
    @inject(ConfigService) private readonly config: ConfigService,
    @inject(LoggerService) private readonly logger: LoggerService,
    @inject(CacheService) private readonly cache: CacheService
  ) {
    this.baseUrl = this.config.get('soda.apiEndpoint');
    this.appToken = this.config.get('soda.appToken');

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: this.config.get('soda.timeout', 30000),
      headers: {
        'X-App-Token': this.appToken,
        'Accept': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        this.logger.debug('Outgoing request', { 
          url: config.url, 
          method: config.method 
        });
        return config;
      },
      (error) => {
        this.logger.error('Request error', { error });
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        this.logger.debug('Response received', { 
          status: response.status,
          url: response.config.url 
        });
        return response;
      },
      (error) => {
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }

  private handleError(error: any): void {
    if (!error.response) {
      throw new SodaError('Network error', 'NETWORK_ERROR');
    }

    const { status, data } = error.response;

    switch (status) {
      case 401:
        throw new AuthenticationError('Unauthorized access', data);
      case 403:
        throw new AuthenticationError('Forbidden access', data);
      case 404:
        throw new SodaError('Resource not found', 'NOT_FOUND');
      case 422:
        throw new ValidationError('Validation failed', data);
      case 429:
        throw new RateLimitError('Rate limit exceeded', data);
      default:
        throw new SodaError('Unexpected error', 'INTERNAL_ERROR');
    }
  }

  private async getCacheKey(request: SodaRequest): Promise<string> {
    const { endpoint, method, params } = request;
    return `soda:${method}:${endpoint}:${JSON.stringify(params)}`;
  }

  private shouldCache(request: SodaRequest): boolean {
    return request.method === 'GET' && this.config.get('soda.enableCaching', true);
  }

  async execute<T>(request: SodaRequest): Promise<SodaResult<T>> {
    const cacheKey = await this.getCacheKey(request);

    if (this.shouldCache(request)) {
      const cached = await this.cache.get<SodaResult<T>>(cacheKey);
      if (cached) {
        this.logger.debug('Cache hit', { cacheKey });
        return cached;
      }
    }

    try {
      const config: AxiosRequestConfig = {
        method: request.method,
        url: request.endpoint,
        params: request.params,
        data: request.data,
        headers: {
          ...request.headers,
          'X-Request-ID': request.requestId
        }
      };

      const response = await this.client.request<T>(config);
      const result: SodaResult<T> = {
        data: response.data,
        metadata: {
          requestId: request.requestId,
          timestamp: new Date().toISOString(),
          status: response.status
        }
      };

      if (this.shouldCache(request)) {
        await this.cache.set(
          cacheKey,
          result,
          this.config.get('soda.cacheTTL', 3600)
        );
      }

      return result;
    } catch (error) {
      this.logger.error('Request failed', { 
        error,
        request: {
          method: request.method,
          endpoint: request.endpoint
        }
      });
      throw error;
    }
  }

  async getMetadata(resourceId: string): Promise<ResourceMetadata> {
    const request: SodaRequest = {
      method: 'GET',
      endpoint: `/api/views/${resourceId}`,
      requestId: crypto.randomUUID()
    };

    const result = await this.execute<ResourceMetadata>(request);
    return result.data;
  }

  async getRawData(query: string): Promise<RawData> {
    const request: SodaRequest = {
      method: 'GET',
      endpoint: '/resource/data',
      params: { $query: query },
      requestId: crypto.randomUUID()
    };

    const result = await this.execute<RawData>(request);
    return result.data;
  }

  async uploadData(resourceId: string, data: any[]): Promise<void> {
    const request: SodaRequest = {
      method: 'POST',
      endpoint: `/api/views/${resourceId}/rows`,
      data,
      requestId: crypto.randomUUID()
    };

    await this.execute(request);
  }

  async deleteData(resourceId: string, rowId: string): Promise<void> {
    const request: SodaRequest = {
      method: 'DELETE',
      endpoint: `/api/views/${resourceId}/rows/${rowId}`,
      requestId: crypto.randomUUID()
    };

    await this.execute(request);
  }
}
