# Serials Module API Reference

## Overview
This document provides a comprehensive reference for the Serials Module API, including both REST and GraphQL interfaces.

## REST API

### Authentication
All endpoints require JWT authentication unless specified otherwise.

#### Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Endpoints

#### Serials

##### Create Serial
```http
POST /api/v1/serials
```

Request:
```typescript
interface CreateSerialRequest {
  clientId: string;
  maxUsageCount: number;
  expirationDate?: Date;
  isDemo?: boolean;
  metadata?: Record<string, any>;
}
```

Response:
```typescript
interface SerialResponse {
  id: string;
  serialNumber: string;
  signature: string;
  maxUsageCount: number;
  expirationDate?: Date;
  isActive: boolean;
  isDemo: boolean;
  createdAt: Date;
  createdBy: string;
}
```

##### Validate Serial
```http
POST /api/v1/serials/validate
```

Request:
```typescript
interface ValidateSerialRequest {
  serialNumber: string;
  deviceId: string;
  deviceInfo: {
    os: string;
    version: string;
    [key: string]: any;
  };
}
```

Response:
```typescript
interface ValidationResponse {
  isValid: boolean;
  message?: string;
  usage?: {
    current: number;
    max: number;
  };
}
```

##### Get Serial
```http
GET /api/v1/serials/{id}
```

Response:
```typescript
interface DetailedSerialResponse extends SerialResponse {
  client: {
    id: string;
    name: string;
  };
  usages: Array<{
    id: string;
    deviceId: string;
    status: string;
    createdAt: Date;
  }>;
}
```

#### Clients

##### Create Client
```http
POST /api/v1/clients
```

Request:
```typescript
interface CreateClientRequest {
  name: string;
  clientNumber: string;
  description?: string;
  contactEmail?: string;
  contactPhone?: string;
  metadata?: Record<string, any>;
}
```

Response:
```typescript
interface ClientResponse {
  id: string;
  name: string;
  clientNumber: string;
  isActive: boolean;
  createdAt: Date;
  createdBy: string;
}
```

## GraphQL API

### Schema Types

#### Serial Type
```graphql
type Serial {
  id: ID!
  serialNumber: String!
  maxUsageCount: Int!
  expirationDate: DateTime
  client: Client!
  metadata: JSON
  isDemo: Boolean!
  isActive: Boolean!
  usages: [SerialUsage!]!
  createdAt: DateTime!
  createdBy: String
  updatedAt: DateTime!
  updatedBy: String
}
```

#### Client Type
```graphql
type Client {
  id: ID!
  name: String!
  clientNumber: String!
  description: String
  metadata: JSON
  isActive: Boolean!
  serials: [Serial!]!
  contactEmail: String
  contactPhone: String
  notes: String
  createdAt: DateTime!
  createdBy: String
  updatedAt: DateTime!
  updatedBy: String
}
```

### Queries

#### Get Serial
```graphql
query GetSerial($id: ID!) {
  serial(id: $id) {
    id
    serialNumber
    maxUsageCount
    expirationDate
    isActive
    isDemo
    client {
      id
      name
    }
    usages {
      deviceId
      status
      createdAt
    }
  }
}
```

#### List Serials
```graphql
query ListSerials(
  $offset: Int = 0
  $limit: Int = 10
  $isActive: Boolean
  $isDemo: Boolean
  $clientId: ID
) {
  serials(
    offset: $offset
    limit: $limit
    isActive: $isActive
    isDemo: $isDemo
    clientId: $clientId
  ) {
    id
    serialNumber
    maxUsageCount
    expirationDate
    isActive
    client {
      id
      name
    }
  }
}
```

### Mutations

#### Create Serial
```graphql
mutation CreateSerial($input: CreateSerialInput!) {
  createSerial(input: $input) {
    id
    serialNumber
    maxUsageCount
    expirationDate
    isActive
  }
}

input CreateSerialInput {
  clientId: ID!
  maxUsageCount: Int!
  expirationDate: DateTime
  isDemo: Boolean
  metadata: JSON
}
```

#### Validate Serial
```graphql
mutation ValidateSerial($input: ValidateSerialInput!) {
  validateSerial(input: $input) {
    isValid
    message
    usage {
      current
      max
    }
  }
}

input ValidateSerialInput {
  serialNumber: String!
  deviceId: String!
  deviceInfo: JSON!
}
```

### Subscriptions

#### Serial Validation
```graphql
subscription OnSerialValidated($id: ID!) {
  serialValidated(id: $id) {
    deviceId
    status
    createdAt
  }
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

### Error Responses
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "field": "serialNumber",
    "message": "Invalid format"
  }
}
```

## Rate Limiting

### Limits
- Authentication: 5 requests/minute
- Serial validation: 100 requests/minute
- Other endpoints: 1000 requests/minute

### Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
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
  total: number;
  offset: number;
  limit: number;
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

### 1. Error Handling
- Always check response status codes
- Handle rate limiting gracefully
- Implement retry logic with backoff

### 2. Performance
- Use GraphQL for complex queries
- Implement client-side caching
- Monitor response times

### 3. Security
- Rotate API keys regularly
- Validate all inputs
- Use HTTPS for all requests
