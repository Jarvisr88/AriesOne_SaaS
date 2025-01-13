# Company Domain API Documentation
Version: 1.0.0
Last Updated: 2025-01-12

## Overview
The Company domain API provides endpoints for managing organizational structures, including companies, locations, departments, employees, and roles. It supports multi-tenant operations and hierarchical organizational structures.

## Authentication
All endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

## Base URL
```
/api/v1/company
```

## Common Parameters
- `skip`: Number of items to skip (pagination)
- `limit`: Maximum number of items to return (pagination)
- All timestamps are in ISO 8601 format
- All IDs are integers

## Error Responses
All endpoints may return these errors:
```json
{
    "401": {
        "description": "Unauthorized - Invalid or missing authentication token"
    },
    "403": {
        "description": "Forbidden - Insufficient permissions"
    },
    "404": {
        "description": "Not Found - Requested resource does not exist"
    },
    "422": {
        "description": "Validation Error - Invalid request data"
    },
    "500": {
        "description": "Internal Server Error"
    }
}
```

## Company Management

### Create Company
```http
POST /companies/
```

**Request Body:**
```json
{
    "name": "string (required)",
    "code": "string (required)",
    "status": "string (enum: Active, Inactive, Suspended, Pending)",
    "phone": "string",
    "email": "string (email)",
    "website": "string (url)",
    "address_line1": "string (required)",
    "address_line2": "string",
    "city": "string (required)",
    "state": "string (required, 2 chars)",
    "zip_code": "string (required)",
    "country": "string (default: US)",
    "fiscal_year_start": "integer (1-12)",
    "time_zone": "string",
    "currency": "string (default: USD)"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "created_by_id": "integer",
    "created_datetime": "string (datetime)",
    "last_update_user_id": "integer",
    "last_update_datetime": "string (datetime)",
    ...request fields
}
```

### Get Company
```http
GET /companies/{company_id}
```

**Response (200):** Same as Create Company response

### Update Company
```http
PUT /companies/{company_id}
```

**Request Body:** Same as Create Company, all fields optional

**Response (200):** Same as Create Company response

### List Companies
```http
GET /companies/
```

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100, max: 100)
- `status`: string (enum: Active, Inactive, Suspended, Pending)

**Response (200):**
```json
[
    {
        ...company object
    }
]
```

## Location Management

### Create Location
```http
POST /companies/{company_id}/locations/
```

**Request Body:**
```json
{
    "name": "string (required)",
    "code": "string (required)",
    "status": "string (enum: Active, Inactive, Suspended, Pending)",
    "phone": "string",
    "email": "string (email)",
    "address_line1": "string (required)",
    "address_line2": "string",
    "city": "string (required)",
    "state": "string (required, 2 chars)",
    "zip_code": "string (required)",
    "country": "string (default: US)",
    "is_warehouse": "boolean",
    "is_service_center": "boolean",
    "service_radius": "integer",
    "operating_hours": "string (JSON)",
    "local_license_number": "string",
    "license_expiry_date": "string (date)"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "company_id": "integer",
    "created_by_id": "integer",
    "created_datetime": "string (datetime)",
    "last_update_user_id": "integer",
    "last_update_datetime": "string (datetime)",
    ...request fields
}
```

### Get Location
```http
GET /locations/{location_id}
```

**Response (200):** Same as Create Location response

### Update Location
```http
PUT /locations/{location_id}
```

**Request Body:** Same as Create Location, all fields optional

**Response (200):** Same as Create Location response

### List Locations
```http
GET /companies/{company_id}/locations/
```

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100, max: 100)
- `status`: string (enum: Active, Inactive, Suspended, Pending)

**Response (200):**
```json
[
    {
        ...location object
    }
]
```

## Department Management

### Create Department
```http
POST /companies/{company_id}/departments/
```

**Request Body:**
```json
{
    "name": "string (required)",
    "code": "string (required)",
    "status": "string (enum: Active, Inactive, Suspended, Pending)",
    "location_id": "integer",
    "parent_department_id": "integer",
    "department_type": "string",
    "cost_center": "string",
    "budget_code": "string"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "company_id": "integer",
    "created_by_id": "integer",
    "created_datetime": "string (datetime)",
    "last_update_user_id": "integer",
    "last_update_datetime": "string (datetime)",
    "child_departments": [],
    ...request fields
}
```

### Get Department
```http
GET /departments/{department_id}
```

**Response (200):** Same as Create Department response

### Update Department
```http
PUT /departments/{department_id}
```

**Request Body:** Same as Create Department, all fields optional

**Response (200):** Same as Create Department response

### List Departments
```http
GET /companies/{company_id}/departments/
```

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100, max: 100)
- `status`: string (enum: Active, Inactive, Suspended, Pending)
- `location_id`: integer

**Response (200):**
```json
[
    {
        ...department object
    }
]
```

## Employee Management

### Create Employee
```http
POST /companies/{company_id}/employees/
```

**Request Body:**
```json
{
    "employee_number": "string (required)",
    "location_id": "integer",
    "department_id": "integer",
    "user_id": "integer",
    "first_name": "string (required)",
    "middle_name": "string",
    "last_name": "string (required)",
    "email": "string (email, required)",
    "phone": "string",
    "hire_date": "string (date, required)",
    "termination_date": "string (date)",
    "status": "string (enum: Active, Inactive, OnLeave, Terminated)",
    "is_full_time": "boolean",
    "title": "string",
    "license_number": "string",
    "license_expiry_date": "string (date)",
    "certifications": "string (JSON)",
    "role_ids": ["integer"]
}
```

**Response (200):**
```json
{
    "id": "integer",
    "company_id": "integer",
    "created_by_id": "integer",
    "created_datetime": "string (datetime)",
    "last_update_user_id": "integer",
    "last_update_datetime": "string (datetime)",
    "roles": [],
    ...request fields
}
```

### Get Employee
```http
GET /employees/{employee_id}
```

**Response (200):** Same as Create Employee response

### Update Employee
```http
PUT /employees/{employee_id}
```

**Request Body:** Same as Create Employee, all fields optional

**Response (200):** Same as Create Employee response

### List Employees
```http
GET /companies/{company_id}/employees/
```

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100, max: 100)
- `status`: string (enum: Active, Inactive, OnLeave, Terminated)
- `location_id`: integer
- `department_id`: integer

**Response (200):**
```json
[
    {
        ...employee object
    }
]
```

## Role Management

### Create Role
```http
POST /roles/
```

**Request Body:**
```json
{
    "name": "string (required)",
    "code": "string (required)",
    "description": "string",
    "is_system_role": "boolean",
    "permissions": "string (JSON)"
}
```

**Response (200):**
```json
{
    "id": "integer",
    "created_by_id": "integer",
    "created_datetime": "string (datetime)",
    "last_update_user_id": "integer",
    "last_update_datetime": "string (datetime)",
    ...request fields
}
```

### Get Role
```http
GET /roles/{role_id}
```

**Response (200):** Same as Create Role response

### Update Role
```http
PUT /roles/{role_id}
```

**Request Body:** Same as Create Role, all fields optional

**Response (200):** Same as Create Role response

### List Roles
```http
GET /roles/
```

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100, max: 100)
- `include_system_roles`: boolean (default: false)

**Response (200):**
```json
[
    {
        ...role object
    }
]
```

## Data Models

### Organization Status
```python
OrganizationStatus = Enum(
    'Active',     # Unit is operational
    'Inactive',   # Unit is temporarily not operational
    'Suspended',  # Unit is suspended due to compliance issues
    'Pending'     # Unit is pending activation
)
```

### Employee Status
```python
EmployeeStatus = Enum(
    'Active',     # Employee is currently working
    'Inactive',   # Employee is temporarily inactive
    'OnLeave',    # Employee is on approved leave
    'Terminated'  # Employee has been terminated
)
```

## Best Practices

1. **Pagination**
   - Always use pagination for list endpoints
   - Default limit is 100 items
   - Use skip/limit for consistent pagination

2. **Error Handling**
   - Always check for resource existence
   - Validate relationships before creation/updates
   - Return appropriate HTTP status codes

3. **Data Validation**
   - Validate email formats
   - Validate phone number formats
   - Ensure date ranges are valid
   - Verify relationship integrity

4. **Security**
   - Always authenticate requests
   - Verify company access permissions
   - Protect system roles from modification

5. **Performance**
   - Use appropriate indexes
   - Implement efficient queries
   - Cache frequently accessed data

## Rate Limiting
- 1000 requests per minute per API key
- 429 Too Many Requests response when exceeded

## Versioning
Current version: v1
Version format: /api/v{version_number}/company/

## Support
For API support, contact:
- Email: api.support@ariesone.com
- Documentation: https://docs.ariesone.com/api/company
- Status: https://status.ariesone.com
