# API Transformation Rules

## REST API Design

### Endpoint Structure
1. Resource Naming:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   /GetUser                         /users/{id}
   /SaveUser                        POST /users
   /UpdateUser                      PUT /users/{id}
   /DeleteUser                      DELETE /users/{id}
   ```

2. HTTP Methods:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   POST /GetUser                    GET /users/{id}
   POST /SaveUser                   POST /users
   POST /UpdateUser                 PUT/PATCH /users/{id}
   POST /DeleteUser                 DELETE /users/{id}
   ```

### Request/Response Format
1. Request Format:
   ```json
   // Legacy
   {
     "RequestData": {
       "UserID": 123,
       "UserName": "john_doe"
     }
   }

   // Modern
   {
     "id": 123,
     "username": "john_doe"
   }
   ```

2. Response Format:
   ```json
   // Legacy
   {
     "Success": true,
     "ErrorMessage": null,
     "Data": {
       "UserDetails": {
         "UserID": 123,
         "UserName": "john_doe"
       }
     }
   }

   // Modern
   {
     "id": 123,
     "username": "john_doe",
     "email": "john@example.com"
   }
   ```

## Authentication/Authorization

### Token Management
1. Token Format:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   Session cookies                   JWT tokens
   Server-side sessions             Stateless auth
   ```

2. Authorization Header:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   Cookie: SESSION=xyz               Authorization: Bearer xyz
   ```

### Permission Rules
1. Role-Based Access:
   ```json
   {
     "roles": ["admin", "user"],
     "permissions": [
       "users:read",
       "users:write"
     ]
   }
   ```

2. Resource Access:
   ```
   GET /users - users:read
   POST /users - users:write
   PUT /users/{id} - users:write
   DELETE /users/{id} - users:delete
   ```

## Error Handling

### Error Response Format
1. Structure:
   ```json
   {
     "status": 400,
     "error": "Bad Request",
     "message": "Invalid input",
     "details": [
       {
         "field": "username",
         "error": "must be at least 3 characters"
       }
     ]
   }
   ```

2. Status Codes:
   ```
   200 - Success
   201 - Created
   400 - Bad Request
   401 - Unauthorized
   403 - Forbidden
   404 - Not Found
   422 - Validation Error
   500 - Server Error
   ```

## Performance Rules

### Caching
1. Cache Headers:
   ```
   Cache-Control: max-age=3600
   ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
   Last-Modified: Wed, 07 Jan 2025 12:45:11 GMT
   ```

2. Cache Strategies:
   ```
   1. Response caching
   2. Query caching
   3. Rate limiting
   4. Pagination
   ```

### Rate Limiting
1. Headers:
   ```
   X-RateLimit-Limit: 100
   X-RateLimit-Remaining: 99
   X-RateLimit-Reset: 1641579911
   ```

2. Limits:
   ```
   Authentication: 5 requests/minute
   API calls: 100 requests/minute
   Bulk operations: 10 requests/minute
   ```

## Documentation Rules

### OpenAPI/Swagger
1. Operation Object:
   ```yaml
   /users/{id}:
     get:
       summary: Get user by ID
       parameters:
         - name: id
           in: path
           required: true
           schema:
             type: integer
       responses:
         '200':
           description: User found
           content:
             application/json:
               schema:
                 $ref: '#/components/schemas/User'
   ```

2. Schema Object:
   ```yaml
   components:
     schemas:
       User:
         type: object
         properties:
           id:
             type: integer
           username:
             type: string
           email:
             type: string
         required:
           - username
           - email
   ```
