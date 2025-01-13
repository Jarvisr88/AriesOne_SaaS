# Reports Module API Reference

## REST API

### Reports

#### List Reports
```http
GET /api/reports
```

Query Parameters:
- `search` (string): Search text for name/description
- `categoryId` (UUID): Filter by category
- `isSystem` (boolean): Filter system reports
- `offset` (number): Pagination offset
- `limit` (number): Page size

Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "category": {
        "id": "uuid",
        "name": "string"
      },
      "template": {
        "id": "uuid",
        "name": "string"
      },
      "parameters": {},
      "createdBy": "string",
      "createdAt": "string",
      "updatedAt": "string",
      "isSystem": false
    }
  ],
  "total": 0,
  "offset": 0,
  "limit": 20
}
```

#### Get Report
```http
GET /api/reports/:id
```

Response:
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "category": {
    "id": "uuid",
    "name": "string"
  },
  "template": {
    "id": "uuid",
    "name": "string",
    "content": "string"
  },
  "parameters": {},
  "createdBy": "string",
  "createdAt": "string",
  "updatedAt": "string",
  "isSystem": false
}
```

#### Create Report
```http
POST /api/reports
```

Request Body:
```json
{
  "name": "string",
  "description": "string",
  "categoryId": "uuid",
  "templateId": "uuid",
  "parameters": {}
}
```

#### Update Report
```http
PUT /api/reports/:id
```

Request Body:
```json
{
  "name": "string",
  "description": "string",
  "categoryId": "uuid",
  "templateId": "uuid",
  "parameters": {}
}
```

#### Delete Report
```http
DELETE /api/reports/:id
```

#### Export Report
```http
POST /api/reports/:id/export
```

Request Body:
```json
{
  "format": "pdf|excel|csv",
  "options": {
    "pageSize": "string",
    "orientation": "portrait|landscape",
    "margins": {
      "top": 0,
      "right": 0,
      "bottom": 0,
      "left": 0
    }
  }
}
```

### Templates

#### List Templates
```http
GET /api/templates
```

Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "templateType": "string",
      "version": 0,
      "createdAt": "string",
      "updatedAt": "string"
    }
  ]
}
```

#### Get Template
```http
GET /api/templates/:id
```

Response:
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "content": "string",
  "templateType": "string",
  "version": 0,
  "createdAt": "string",
  "updatedAt": "string"
}
```

#### Create Template
```http
POST /api/templates
```

Request Body:
```json
{
  "name": "string",
  "description": "string",
  "content": "string",
  "templateType": "string"
}
```

#### Update Template
```http
PUT /api/templates/:id
```

Request Body:
```json
{
  "name": "string",
  "description": "string",
  "content": "string"
}
```

#### Delete Template
```http
DELETE /api/templates/:id
```

### Categories

#### List Categories
```http
GET /api/categories
```

Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "string",
      "parentId": "uuid",
      "children": []
    }
  ]
}
```

#### Get Category
```http
GET /api/categories/:id
```

Response:
```json
{
  "id": "uuid",
  "name": "string",
  "parentId": "uuid",
  "children": []
}
```

#### Create Category
```http
POST /api/categories
```

Request Body:
```json
{
  "name": "string",
  "parentId": "uuid"
}
```

#### Update Category
```http
PUT /api/categories/:id
```

Request Body:
```json
{
  "name": "string",
  "parentId": "uuid"
}
```

#### Delete Category
```http
DELETE /api/categories/:id
```

## GraphQL API

### Queries

#### List Reports
```graphql
query Reports($filter: ReportFilter) {
  reports(filter: $filter) {
    id
    name
    description
    category {
      id
      name
    }
    template {
      id
      name
    }
    parameters
    createdBy
    createdAt
    updatedAt
    isSystem
  }
}
```

#### Get Report
```graphql
query Report($id: ID!) {
  report(id: $id) {
    id
    name
    description
    category {
      id
      name
    }
    template {
      id
      name
      content
    }
    parameters
    createdBy
    createdAt
    updatedAt
    isSystem
  }
}
```

### Mutations

#### Create Report
```graphql
mutation CreateReport($input: ReportInput!) {
  createReport(input: $input) {
    id
    name
    description
    category {
      id
      name
    }
    template {
      id
      name
    }
    parameters
    createdBy
    createdAt
    updatedAt
    isSystem
  }
}
```

#### Update Report
```graphql
mutation UpdateReport($id: ID!, $input: ReportInput!) {
  updateReport(id: $id, input: $input) {
    id
    name
    description
    category {
      id
      name
    }
    template {
      id
      name
    }
    parameters
    createdBy
    createdAt
    updatedAt
    isSystem
  }
}
```

#### Delete Report
```graphql
mutation DeleteReport($id: ID!) {
  deleteReport(id: $id)
}
```

#### Export Report
```graphql
mutation ExportReport($id: ID!, $format: String!) {
  exportReport(id: $id, format: $format)
}
```

### Subscriptions

#### Report Exported
```graphql
subscription ReportExported($id: ID!) {
  reportExported(id: $id) {
    status
    url
    error
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input data |
| `NOT_FOUND` | Resource not found |
| `PERMISSION_DENIED` | Insufficient permissions |
| `SYSTEM_REPORT` | Cannot modify system report |
| `TEMPLATE_ERROR` | Template compilation error |
| `EXPORT_ERROR` | Export generation error |
| `DATABASE_ERROR` | Database operation error |
| `CACHE_ERROR` | Cache operation error |

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per API key
- Export operations: 10 per minute

## Authentication

### JWT Authentication
```http
Authorization: Bearer <token>
```

### API Key Authentication
```http
X-API-Key: <api-key>
```

## WebSocket Events

### Export Progress
```json
{
  "type": "EXPORT_PROGRESS",
  "data": {
    "reportId": "uuid",
    "progress": 0,
    "status": "string"
  }
}
```

### Export Complete
```json
{
  "type": "EXPORT_COMPLETE",
  "data": {
    "reportId": "uuid",
    "url": "string"
  }
}
```

### Export Error
```json
{
  "type": "EXPORT_ERROR",
  "data": {
    "reportId": "uuid",
    "error": {
      "code": "string",
      "message": "string"
    }
  }
}
```
