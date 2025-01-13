# SODA Module API Design

## Overview
The SODA module provides both REST and GraphQL APIs for interacting with Socrata Open Data resources. This document outlines the API design, including endpoints, schemas, and authentication.

## REST API

### Base URL
```
https://api.ariesone.com/v1/soda
```

### Authentication
All endpoints require JWT authentication:
```http
Authorization: Bearer <jwt_token>
```

### Endpoints

#### Resources

##### Get Resource
```http
GET /resources/{id}
```

Response:
```typescript
interface ResourceResponse {
  id: string;
  name: string;
  description?: string;
  columns: Column[];
  metadata: ResourceMetadata;
  _links: {
    self: string;
    query: string;
    metadata: string;
  };
}
```

##### Query Resource
```http
POST /resources/{id}/query
```

Request:
```typescript
interface QueryRequest {
  select?: string[];
  where?: WhereClause[];
  orderBy?: {
    column: string;
    direction: 'ASC' | 'DESC';
  };
  limit?: number;
  offset?: number;
}
```

Response:
```typescript
interface QueryResponse<T> {
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
}
```

##### Update Resource
```http
PUT /resources/{id}
```

Request:
```typescript
interface UpdateRequest {
  name?: string;
  description?: string;
  columns?: Partial<Column>[];
  metadata?: Partial<ResourceMetadata>;
}
```

Response:
```typescript
interface UpdateResponse {
  id: string;
  version: string;
  updatedAt: string;
  _links: {
    self: string;
    query: string;
  };
}
```

#### Metadata

##### Get Metadata
```http
GET /resources/{id}/metadata
```

Response:
```typescript
interface MetadataResponse {
  id: string;
  name: string;
  description?: string;
  owner: string;
  createdAt: string;
  updatedAt: string;
  license?: string;
  tags: string[];
  columns: ColumnMetadata[];
  _links: {
    self: string;
    resource: string;
  };
}
```

## GraphQL API

### Schema

#### Types
```graphql
type Resource {
  id: ID!
  name: String!
  description: String
  columns: [Column!]!
  metadata: ResourceMetadata!
  data(
    where: WhereInput
    orderBy: OrderByInput
    limit: Int
    offset: Int
  ): [JSON!]!
}

type Column {
  name: String!
  dataType: DataType!
  description: String
  isRequired: Boolean!
}

type ResourceMetadata {
  createdAt: DateTime!
  updatedAt: DateTime!
  owner: String!
  license: String
  tags: [String!]!
}

input WhereInput {
  field: String!
  operator: String!
  value: JSON
}

input OrderByInput {
  field: String!
  direction: OrderDirection!
}

enum OrderDirection {
  ASC
  DESC
}

enum DataType {
  TEXT
  NUMBER
  BOOLEAN
  DATE
  LOCATION
  PHONE
  URL
  JSON
}
```

### Queries

#### Get Resource
```graphql
query GetResource($id: ID!) {
  resource(id: $id) {
    id
    name
    description
    columns {
      name
      dataType
      description
      isRequired
    }
    metadata {
      createdAt
      updatedAt
      owner
      license
      tags
    }
  }
}
```

#### Query Resource Data
```graphql
query QueryResource(
  $id: ID!
  $where: WhereInput
  $orderBy: OrderByInput
  $limit: Int
  $offset: Int
) {
  resource(id: $id) {
    data(
      where: $where
      orderBy: $orderBy
      limit: $limit
      offset: $offset
    )
  }
}
```

### Mutations

#### Update Resource
```graphql
mutation UpdateResource($id: ID!, $input: UpdateResourceInput!) {
  updateResource(id: $id, input: $input) {
    id
    version
    updatedAt
  }
}

input UpdateResourceInput {
  name: String
  description: String
  columns: [UpdateColumnInput!]
  metadata: UpdateMetadataInput
}
```

## Error Handling

### Error Types
```typescript
interface ApiError {
  statusCode: number;
  message: string;
  code: string;
  details?: Record<string, any>;
}
```

### Common Error Codes
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Invalid input
- `RATE_LIMITED`: Too many requests

### Error Response Format
```json
{
  "error": {
    "statusCode": 400,
    "message": "Invalid query parameters",
    "code": "VALIDATION_ERROR",
    "details": {
      "field": "where",
      "message": "Invalid operator"
    }
  }
}
```

## Rate Limiting

### Limits
- Authentication: 5 requests/minute
- Query operations: 100 requests/minute
- Update operations: 50 requests/minute

### Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1609459200
```

## Pagination

### Request Parameters
- `offset`: Starting position (default: 0)
- `limit`: Items per page (default: 10, max: 100)

### Response Format
```typescript
interface PaginatedResponse<T> {
  data: T[];
  metadata: {
    total: number;
    offset: number;
    limit: number;
  };
  links: {
    self: string;
    next?: string;
    prev?: string;
  };
}
```

## Caching

### Cache Headers
```http
Cache-Control: private, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

### Conditional Requests
```http
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
If-Modified-Since: Wed, 21 Oct 2015 07:28:00 GMT
```

## Best Practices

### 1. Query Optimization
- Use selective fields
- Implement pagination
- Cache frequent queries
- Monitor query complexity

### 2. Error Handling
- Validate input data
- Return descriptive errors
- Include error codes
- Log error details

### 3. Security
- Validate authentication
- Check permissions
- Sanitize input
- Rate limit requests

### 4. Performance
- Use compression
- Implement caching
- Monitor response times
- Optimize queries
