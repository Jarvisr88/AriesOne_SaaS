# SODA API Reference

## Overview
The SODA (Socrata Open Data API) module provides a modern, RESTful API for managing and querying data resources. This document outlines the available endpoints, request/response formats, and authentication requirements.

## Authentication
All API requests require authentication using JWT (JSON Web Token) Bearer tokens.

```http
Authorization: Bearer <token>
```

## Resources

### Create Resource
```http
POST /api/resources
Content-Type: application/json
```

#### Request Body
```typescript
{
  name: string;              // Resource name
  description?: string;      // Optional description
  columns: {
    name: string;           // Column name
    dataType: DataType;     // Column type (TEXT, NUMBER, etc.)
    required: boolean;      // Is the field required?
  }[];
  metadata: {
    tags: string[];         // Resource tags
    customFields: Record<string, any>; // Custom metadata
  };
}
```

#### Response
```typescript
{
  id: string;               // Resource ID
  name: string;             // Resource name
  description?: string;     // Description
  columns: Column[];        // Column definitions
  metadata: ResourceMetadata; // Resource metadata
  createdAt: string;        // Creation timestamp
  updatedAt: string;        // Last update timestamp
  _links: {                 // HATEOAS links
    self: string;
    query: string;
    metadata: string;
  };
}
```

### Get Resource
```http
GET /api/resources/:id
```

#### Response
Same as Create Resource response.

### Update Resource
```http
PUT /api/resources/:id
Content-Type: application/json
```

#### Request Body
```typescript
{
  name?: string;            // Optional name update
  description?: string;     // Optional description update
  columns?: Column[];       // Optional columns update
  metadata?: {              // Optional metadata update
    tags?: string[];
    customFields?: Record<string, any>;
  };
}
```

### Delete Resource
```http
DELETE /api/resources/:id
```

### Query Resource
```http
POST /api/resources/:id/query
Content-Type: application/json
```

#### Request Body
```typescript
{
  select?: string[];        // Columns to return
  where?: {                 // Filter conditions
    field: string;
    operator: string;       // EQ, NEQ, GT, GTE, LT, LTE, etc.
    value: any;
  }[];
  orderBy?: {              // Sort specification
    field: string;
    direction: 'ASC' | 'DESC';
  };
  limit?: number;          // Max results
  offset?: number;         // Pagination offset
}
```

#### Response
```typescript
{
  data: any[];             // Query results
  metadata: {              // Pagination metadata
    total: number;
    offset: number;
    limit: number;
  };
  _links: {                // Navigation links
    self: string;
    next?: string;
    prev?: string;
  };
}
```

### Bulk Upload
```http
POST /api/resources/:id/bulk
Content-Type: application/json
```

#### Request Body
```typescript
Array<Record<string, any>>  // Array of records matching resource schema
```

## Error Handling

### Error Response Format
```typescript
{
  error: string;            // Error message
  code: string;            // Error code
  details?: any;           // Additional error details
  errors?: string[];       // Validation errors
}
```

### Common Error Codes
- `400`: Bad Request (validation error)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `409`: Conflict (resource already exists)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

## Rate Limiting
API requests are rate-limited based on the client's API key:
- Standard tier: 100 requests/minute
- Premium tier: 1000 requests/minute

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704235200
```

## Data Types
Supported data types for resource columns:
- `TEXT`: String values
- `NUMBER`: Numeric values
- `BOOLEAN`: Boolean values
- `DATE`: ISO 8601 date strings
- `LOCATION`: Geographic coordinates
- `PHONE`: Phone numbers
- `URL`: URLs
- `JSON`: JSON objects/arrays

## Query Operators
Available operators for query filters:
- `EQ`: Equals
- `NEQ`: Not equals
- `GT`: Greater than
- `GTE`: Greater than or equal
- `LT`: Less than
- `LTE`: Less than or equal
- `IN`: In array
- `BETWEEN`: Between range
- `LIKE`: Pattern match
- `ILIKE`: Case-insensitive pattern match
