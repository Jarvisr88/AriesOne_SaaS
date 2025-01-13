# Forms API Documentation

## Overview

The Forms API provides endpoints for managing forms, submissions, and company-specific form configurations.

## Base URL

```
/api/v1
```

## Authentication

All endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Forms

#### List Forms

```http
GET /forms
```

Query Parameters:
- `active_only` (boolean): Filter active forms only
- `company_id` (number): Filter by company
- `page` (number): Page number for pagination
- `limit` (number): Items per page

Response:
```json
{
  "items": [
    {
      "id": 1,
      "name": "Patient Intake",
      "description": "Initial patient information form",
      "schema": {
        "fields": [...]
      },
      "created_by": "user@example.com",
      "created_at": "2025-01-11T17:55:12-06:00",
      "updated_at": "2025-01-11T17:55:12-06:00",
      "is_active": true
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20
}
```

#### Get Form

```http
GET /forms/{id}
```

Response:
```json
{
  "id": 1,
  "name": "Patient Intake",
  "description": "Initial patient information form",
  "schema": {
    "fields": [...]
  },
  "created_by": "user@example.com",
  "created_at": "2025-01-11T17:55:12-06:00",
  "updated_at": "2025-01-11T17:55:12-06:00",
  "is_active": true
}
```

#### Create Form

```http
POST /forms
```

Request Body:
```json
{
  "name": "Patient Intake",
  "description": "Initial patient information form",
  "schema": {
    "fields": [...]
  }
}
```

#### Update Form

```http
PUT /forms/{id}
```

Request Body:
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "schema": {
    "fields": [...]
  }
}
```

### Submissions

#### List Submissions

```http
GET /submissions
```

Query Parameters:
- `form_id` (number): Filter by form
- `company_id` (number): Filter by company
- `status` (string): Filter by status
- `search` (string): Search text
- `page` (number): Page number
- `limit` (number): Items per page

Response:
```json
{
  "items": [
    {
      "id": 1,
      "form_id": 1,
      "form_name": "Patient Intake",
      "company_id": 2,
      "company_name": "Medical Corp",
      "status": "pending",
      "data": {...},
      "submitted_by": "user@example.com",
      "submitted_at": "2025-01-11T17:55:12-06:00"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

#### Get Submission

```http
GET /submissions/{id}
```

Response:
```json
{
  "id": 1,
  "form_id": 1,
  "form_name": "Patient Intake",
  "company_id": 2,
  "company_name": "Medical Corp",
  "status": "pending",
  "data": {...},
  "submitted_by": "user@example.com",
  "submitted_at": "2025-01-11T17:55:12-06:00"
}
```

#### Create Submission

```http
POST /submissions
```

Request Body:
```json
{
  "form_id": 1,
  "company_id": 2,
  "data": {...}
}
```

#### Update Submission

```http
PUT /submissions/{id}
```

Request Body:
```json
{
  "status": "approved"
}
```

### Company Forms

#### List Company Forms

```http
GET /companies/{company_id}/forms
```

Response:
```json
{
  "items": [
    {
      "form_id": 1,
      "form_name": "Patient Intake",
      "settings": {...},
      "is_active": true,
      "submission_count": 25,
      "updated_at": "2025-01-11T17:55:12-06:00"
    }
  ]
}
```

#### Assign Form

```http
POST /companies/{company_id}/forms
```

Request Body:
```json
{
  "form_id": 1,
  "settings": {...}
}
```

#### Update Form Settings

```http
PUT /companies/{company_id}/forms/{form_id}
```

Request Body:
```json
{
  "settings": {...},
  "is_active": true
}
```

## Error Responses

All endpoints may return the following errors:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {
      "field": ["error message"]
    }
  }
}
```

Error Codes:
- `VALIDATION_ERROR`: Invalid input data
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Missing or invalid token
- `FORBIDDEN`: Insufficient permissions
- `INTERNAL_ERROR`: Server error
