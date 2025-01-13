import { Resource } from '../entities/resource.entity';
import { Column } from '../entities/column.entity';
import { ResourceMetadata } from '../entities/resource-metadata.entity';

export class CreateResourceDto {
  name: string;
  description?: string;
  columns: Partial<Column>[];
  metadata: Partial<ResourceMetadata>;
}

export class UpdateResourceDto {
  name?: string;
  description?: string;
  columns?: Partial<Column>[];
  metadata?: Partial<ResourceMetadata>;
}

export class ResourceResponseDto {
  id: string;
  name: string;
  description?: string;
  columns: Column[];
  metadata: ResourceMetadata;
  createdAt: string;
  updatedAt: string;
  version: number;
  _links: {
    self: string;
    query: string;
    metadata: string;
  };

  static fromEntity(resource: Resource, baseUrl: string): ResourceResponseDto {
    return {
      id: resource.id,
      name: resource.name,
      description: resource.description,
      columns: resource.columns,
      metadata: resource.metadata,
      createdAt: resource.createdAt.toISOString(),
      updatedAt: resource.updatedAt.toISOString(),
      version: resource.version,
      _links: {
        self: `${baseUrl}/resources/${resource.id}`,
        query: `${baseUrl}/resources/${resource.id}/query`,
        metadata: `${baseUrl}/resources/${resource.id}/metadata`
      }
    };
  }
}

export class ResourceQueryDto {
  select?: string[];
  where?: WhereClause[];
  orderBy?: OrderByClause;
  limit?: number;
  offset?: number;
}

export interface WhereClause {
  field: string;
  operator: string;
  value: any;
}

export interface OrderByClause {
  field: string;
  direction: 'ASC' | 'DESC';
}

export class ResourceQueryResponseDto<T> {
  data: T[];
  metadata: {
    total: number;
    offset: number;
    limit: number;
  };
  _links: {
    self: string;
    next?: string;
    prev?: string;
  };

  static create<T>(
    data: T[],
    total: number,
    offset: number,
    limit: number,
    baseUrl: string
  ): ResourceQueryResponseDto<T> {
    const response = new ResourceQueryResponseDto<T>();
    response.data = data;
    response.metadata = { total, offset, limit };
    response._links = {
      self: `${baseUrl}?offset=${offset}&limit=${limit}`
    };

    if (offset + limit < total) {
      response._links.next = `${baseUrl}?offset=${offset + limit}&limit=${limit}`;
    }

    if (offset > 0) {
      response._links.prev = `${baseUrl}?offset=${Math.max(0, offset - limit)}&limit=${limit}`;
    }

    return response;
  }
}
