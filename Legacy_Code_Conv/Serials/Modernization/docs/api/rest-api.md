# Serials Module REST API Documentation

## Overview
The Serials Module provides a RESTful API for managing serial numbers, clients, and usage tracking. This document outlines all available endpoints, authentication requirements, and example usage.

## Authentication
All API endpoints require JWT authentication except for serial validation. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Base URL
```
https://api.ariesone.com/v1
```

## Endpoints

### Serials

#### Create Serial
```http
POST /serials
```
Creates a new serial number.

**Request Body:**
```json
{
  "clientId": "string (UUID)",
  "maxUsageCount": "number",
  "expirationDate": "string (ISO date)",
  "isDemo": "boolean (optional)",
  "metadata": "object (optional)"
}
```

**Response:** `201 Created`
```json
{
  "id": "string (UUID)",
  "serialNumber": "string",
  "signature": "string",
  "maxUsageCount": "number",
  "expirationDate": "string",
  "isActive": "boolean",
  "isDemo": "boolean",
  "createdAt": "string",
  "createdBy": "string"
}
```

#### Bulk Create Serials
```http
POST /serials/bulk
```
Creates multiple serial numbers.

**Request Body:**
```json
{
  "clientId": "string (UUID)",
  "count": "number",
  "maxUsageCount": "number",
  "expirationDate": "string (ISO date)",
  "isDemo": "boolean (optional)"
}
```

**Response:** `201 Created`
```json
{
  "serials": [
    {
      "id": "string (UUID)",
      "serialNumber": "string",
      "signature": "string"
    }
  ],
  "count": "number"
}
```

#### List Serials
```http
GET /serials
```
Retrieves a paginated list of serials.

**Query Parameters:**
- `offset` (number, default: 0): Pagination offset
- `limit` (number, default: 10): Items per page
- `isActive` (boolean): Filter by active status
- `isDemo` (boolean): Filter by demo status
- `clientId` (UUID): Filter by client

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "string (UUID)",
      "serialNumber": "string",
      "maxUsageCount": "number",
      "expirationDate": "string",
      "isActive": "boolean",
      "isDemo": "boolean",
      "client": {
        "id": "string (UUID)",
        "name": "string"
      }
    }
  ],
  "total": "number",
  "offset": "number",
  "limit": "number"
}
```

#### Get Serial
```http
GET /serials/{id}
```
Retrieves a specific serial by ID.

**Response:** `200 OK`
```json
{
  "id": "string (UUID)",
  "serialNumber": "string",
  "maxUsageCount": "number",
  "expirationDate": "string",
  "isActive": "boolean",
  "isDemo": "boolean",
  "client": {
    "id": "string (UUID)",
    "name": "string"
  },
  "usages": [
    {
      "id": "string (UUID)",
      "deviceId": "string",
      "status": "string",
      "createdAt": "string"
    }
  ]
}
```

#### Update Serial
```http
PUT /serials/{id}
```
Updates a serial number.

**Request Body:**
```json
{
  "maxUsageCount": "number (optional)",
  "expirationDate": "string (optional)",
  "isActive": "boolean (optional)",
  "metadata": "object (optional)"
}
```

**Response:** `200 OK`
```json
{
  "id": "string (UUID)",
  "serialNumber": "string",
  "maxUsageCount": "number",
  "expirationDate": "string",
  "isActive": "boolean",
  "updatedAt": "string",
  "updatedBy": "string"
}
```

#### Delete Serial
```http
DELETE /serials/{id}
```
Soft deletes a serial number.

**Response:** `204 No Content`

#### Validate Serial
```http
POST /serials/validate
```
Validates a serial number and records usage.

**Request Body:**
```json
{
  "serialNumber": "string",
  "deviceId": "string",
  "deviceInfo": "object"
}
```

**Response:** `200 OK`
```json
{
  "isValid": "boolean",
  "message": "string (optional)"
}
```

### Clients

#### Create Client
```http
POST /clients
```
Creates a new client.

**Request Body:**
```json
{
  "name": "string",
  "clientNumber": "string",
  "description": "string (optional)",
  "contactEmail": "string (optional)",
  "contactPhone": "string (optional)",
  "metadata": "object (optional)"
}
```

**Response:** `201 Created`
```json
{
  "id": "string (UUID)",
  "name": "string",
  "clientNumber": "string",
  "isActive": "boolean",
  "createdAt": "string",
  "createdBy": "string"
}
```

#### List Clients
```http
GET /clients
```
Retrieves a paginated list of clients.

**Query Parameters:**
- `offset` (number, default: 0): Pagination offset
- `limit` (number, default: 10): Items per page
- `isActive` (boolean): Filter by active status

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "string (UUID)",
      "name": "string",
      "clientNumber": "string",
      "isActive": "boolean",
      "serialCount": "number"
    }
  ],
  "total": "number",
  "offset": "number",
  "limit": "number"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "statusCode": 400,
  "message": "string",
  "errors": [
    {
      "field": "string",
      "message": "string"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "statusCode": 401,
  "message": "Unauthorized"
}
```

### 403 Forbidden
```json
{
  "statusCode": 403,
  "message": "Forbidden"
}
```

### 404 Not Found
```json
{
  "statusCode": 404,
  "message": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "statusCode": 429,
  "message": "Too many requests",
  "retryAfter": "number"
}
```

## Rate Limiting
API endpoints are rate-limited to protect the service. Current limits:
- Authentication endpoints: 5 requests per minute
- Serial validation: 100 requests per minute
- Other endpoints: 1000 requests per minute

## Best Practices
1. Always validate serial numbers before use
2. Implement proper error handling
3. Use bulk operations for large datasets
4. Cache frequently accessed data
5. Monitor rate limits and usage patterns
