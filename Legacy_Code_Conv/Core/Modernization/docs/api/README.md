# AriesOne SaaS API Documentation

Version: 1.0.0
Last Updated: 2025-01-10

## Overview

The AriesOne SaaS API provides a comprehensive set of endpoints for managing healthcare equipment inventory, orders, and tenant operations. This RESTful API uses JSON for request/response payloads and follows OAuth2 for authentication.

## Authentication

### OAuth2 Flow
```
POST /api/v1/auth/token
```

Request:
```json
{
  "grant_type": "password",
  "username": "user@example.com",
  "password": "secure_password",
  "client_id": "your_client_id"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### API Key Authentication
For service-to-service communication, use API key in the header:
```
X-API-Key: your_api_key
```

## Endpoints

### Tenant Management

#### Create Tenant
```
POST /api/v1/tenants
```

Request:
```json
{
  "name": "Healthcare Provider Inc",
  "domain": "provider.com",
  "plan": "enterprise",
  "admin_email": "admin@provider.com"
}
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Healthcare Provider Inc",
  "domain": "provider.com",
  "status": "active",
  "created_at": "2025-01-10T20:00:00Z"
}
```

### Inventory Management

#### List Items
```
GET /api/v1/inventory
```

Parameters:
- `page` (int): Page number
- `per_page` (int): Items per page
- `status` (string): Filter by status
- `category` (string): Filter by category

Response:
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "sku": "CPAP-001",
      "name": "CPAP Machine",
      "category": "respiratory",
      "quantity": 50,
      "status": "active"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

#### Create Item
```
POST /api/v1/inventory
```

Request:
```json
{
  "sku": "CPAP-001",
  "name": "CPAP Machine",
  "category": "respiratory",
  "description": "Continuous Positive Airway Pressure device",
  "quantity": 50,
  "minimum_quantity": 10,
  "maximum_quantity": 100,
  "location_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

### Order Management

#### Create Order
```
POST /api/v1/orders
```

Request:
```json
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440003",
  "items": [
    {
      "inventory_item_id": "550e8400-e29b-41d4-a716-446655440001",
      "quantity": 1,
      "rental_period": 30
    }
  ],
  "delivery_address": {
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip": "62701"
  }
}
```

## Webhooks

### Event Types
- `inventory.low_stock`
- `order.created`
- `order.updated`
- `order.completed`

### Payload Format
```json
{
  "event": "inventory.low_stock",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-10T20:00:00Z",
  "data": {
    "item_id": "550e8400-e29b-41d4-a716-446655440001",
    "sku": "CPAP-001",
    "current_quantity": 5,
    "minimum_quantity": 10
  }
}
```

## Rate Limiting

- Standard Plan: 100 requests/minute
- Enterprise Plan: 1000 requests/minute

Headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1673397785
```

## Error Handling

### HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Invalid input parameters",
    "details": {
      "field": "quantity",
      "reason": "must be greater than 0"
    }
  }
}
```

## Pagination

All list endpoints support pagination using:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

Response includes:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5
}
```

## SDK Support

Official SDKs available for:
- Python
- JavaScript
- Java
- C#

Example (Python):
```python
from ariesone import AriesOneClient

client = AriesOneClient(api_key="your_api_key")

# List inventory
inventory = client.inventory.list(
    category="respiratory",
    status="active"
)

# Create order
order = client.orders.create(
    customer_id="customer_id",
    items=[{
        "inventory_item_id": "item_id",
        "quantity": 1
    }]
)
```

## Best Practices

1. **Authentication**
   - Store API keys securely
   - Rotate keys regularly
   - Use environment variables

2. **Rate Limiting**
   - Implement exponential backoff
   - Cache responses when possible
   - Monitor usage patterns

3. **Error Handling**
   - Implement retry logic
   - Log all errors
   - Monitor error rates

4. **Webhooks**
   - Acknowledge quickly
   - Process asynchronously
   - Implement retry logic

## Support

- Email: api-support@ariesone.com
- Documentation: docs.ariesone.com
- Status: status.ariesone.com
