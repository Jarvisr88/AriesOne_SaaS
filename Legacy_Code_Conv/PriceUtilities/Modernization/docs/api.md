# Price Utilities API Documentation

## API Overview
Base URL: `/api/v1`

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Price Management

#### Get Price
```http
GET /prices/{item_id}
```
Returns current price information for an item.

**Parameters:**
- `item_id`: String (required) - Unique identifier for the item

**Response:**
```json
{
  "item_id": "string",
  "base_price": "decimal",
  "currency": "string",
  "quantity_breaks": {
    "integer": "decimal"
  },
  "effective_date": "datetime",
  "icd_modifiers": [
    {
      "code": "string",
      "modifier": "decimal"
    }
  ]
}
```

#### Update Price
```http
POST /prices/update
```
Updates price information for a single item.

**Request Body:**
```json
{
  "item_id": "string",
  "base_price": "decimal",
  "currency": "string",
  "quantity_breaks": {
    "integer": "decimal"
  },
  "effective_date": "datetime",
  "icd_codes": ["string"]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "string",
  "updated_price": {
    "item_id": "string",
    "base_price": "decimal",
    "currency": "string"
  }
}
```

#### Bulk Update Prices
```http
POST /prices/bulk-update
```
Updates multiple prices in a single operation.

**Request Body:**
```json
{
  "updates": [
    {
      "item_id": "string",
      "base_price": "decimal",
      "currency": "string",
      "effective_date": "datetime"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "successful": "integer",
  "failed": "integer",
  "failures": [
    {
      "item_id": "string",
      "error": "string"
    }
  ]
}
```

### ICD Code Management

#### Get ICD Codes
```http
GET /icd-codes
```
Returns list of ICD codes with their modifiers.

**Query Parameters:**
- `page`: Integer - Page number (default: 1)
- `limit`: Integer - Items per page (default: 50)
- `search`: String - Search term

**Response:**
```json
{
  "items": [
    {
      "code": "string",
      "description": "string",
      "modifier": "decimal"
    }
  ],
  "total": "integer",
  "page": "integer",
  "pages": "integer"
}
```

#### Update ICD Code
```http
PUT /icd-codes/{code}
```
Updates an ICD code modifier.

**Request Body:**
```json
{
  "modifier": "decimal",
  "description": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "code": "string",
  "modifier": "decimal"
}
```

### Parameter Management

#### Get Parameters
```http
GET /parameters
```
Returns list of pricing parameters.

**Response:**
```json
{
  "parameters": [
    {
      "name": "string",
      "value": "decimal",
      "parameter_type": "string",
      "effective_date": "datetime"
    }
  ]
}
```

#### Update Parameter
```http
PUT /parameters/{name}
```
Updates a pricing parameter.

**Request Body:**
```json
{
  "value": "decimal",
  "parameter_type": "string",
  "effective_date": "datetime"
}
```

**Response:**
```json
{
  "status": "success",
  "name": "string",
  "value": "decimal"
}
```

### Audit Log

#### Get Audit Log
```http
GET /audit
```
Returns audit log entries.

**Query Parameters:**
- `start_date`: DateTime
- `end_date`: DateTime
- `item_id`: String
- `action_type`: String
- `page`: Integer
- `limit`: Integer

**Response:**
```json
{
  "entries": [
    {
      "timestamp": "datetime",
      "user_id": "string",
      "action": "string",
      "item_id": "string",
      "changes": {
        "field": ["old_value", "new_value"]
      }
    }
  ],
  "total": "integer",
  "page": "integer"
}
```

## Error Responses

All endpoints may return the following errors:

### 400 Bad Request
```json
{
  "status": "error",
  "message": "string",
  "details": {}
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "status": "error",
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error",
  "reference": "string"
}
```
