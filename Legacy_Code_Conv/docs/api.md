# AriesOne SaaS API Reference

## API Overview

### Base URL
```
https://api.ariesone.com/v1
```

### Authentication
All API requests require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

### Response Format
All responses are in JSON format and include:
```json
{
    "status": "success|error",
    "data": {},
    "message": "Optional message",
    "errors": []
}
```

## Authentication API

### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "access_token": "eyJ0...",
        "refresh_token": "eyJ1...",
        "token_type": "bearer",
        "expires_in": 3600
    }
}
```

### Refresh Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
    "refresh_token": "eyJ1..."
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "access_token": "eyJ0...",
        "expires_in": 3600
    }
}
```

## User Management API

### List Users
```http
GET /users
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `sort`: Sort field
- `order`: Sort order (asc|desc)
- `search`: Search term

**Response:**
```json
{
    "status": "success",
    "data": {
        "items": [
            {
                "id": "user123",
                "email": "user@example.com",
                "name": "John Doe",
                "role": "admin",
                "created_at": "2025-01-08T23:05:30Z"
            }
        ],
        "total": 100,
        "page": 1,
        "limit": 10
    }
}
```

### Create User
```http
POST /users
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe",
    "role": "admin"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": "user123",
        "email": "user@example.com",
        "name": "John Doe",
        "role": "admin",
        "created_at": "2025-01-08T23:05:30Z"
    }
}
```

## Price Management API

### List Prices
```http
GET /prices
```

**Query Parameters:**
- `page`: Page number
- `limit`: Items per page
- `category`: Product category
- `status`: Price status

**Response:**
```json
{
    "status": "success",
    "data": {
        "items": [
            {
                "id": "price123",
                "product_id": "prod123",
                "amount": 99.99,
                "currency": "USD",
                "effective_date": "2025-01-08T23:05:30Z"
            }
        ],
        "total": 50,
        "page": 1,
        "limit": 10
    }
}
```

### Create Price
```http
POST /prices
```

**Request Body:**
```json
{
    "product_id": "prod123",
    "amount": 99.99,
    "currency": "USD",
    "effective_date": "2025-01-08T23:05:30Z"
}
```

## Report Generation API

### Generate Report
```http
POST /reports
```

**Request Body:**
```json
{
    "type": "sales",
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-31T23:59:59Z",
    "format": "pdf",
    "filters": {
        "category": "equipment",
        "status": "completed"
    }
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "report_id": "report123",
        "status": "processing",
        "download_url": null
    }
}
```

### Get Report Status
```http
GET /reports/{report_id}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "report_id": "report123",
        "status": "completed",
        "download_url": "https://..."
    }
}
```

## SODA Integration API

### Sync Data
```http
POST /soda/sync
```

**Request Body:**
```json
{
    "resource_type": "inventory",
    "sync_mode": "full|incremental",
    "filters": {
        "last_sync": "2025-01-08T23:05:30Z"
    }
}
```

### Get Sync Status
```http
GET /soda/sync/{sync_id}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "sync_id": "sync123",
        "resource_type": "inventory",
        "status": "completed",
        "items_processed": 1000,
        "errors": []
    }
}
```

## Error Codes

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Too Many Requests
- `500`: Internal Server Error

### Business Error Codes
- `AUTH001`: Invalid credentials
- `AUTH002`: Token expired
- `USER001`: User not found
- `USER002`: Email already exists
- `PRICE001`: Invalid amount
- `PRICE002`: Future date not allowed
- `REPORT001`: Invalid date range
- `REPORT002`: Processing failed
- `SODA001`: Sync failed
- `SODA002`: Resource not found
