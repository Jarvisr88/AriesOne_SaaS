# API Transformation Rules

## RESTful Endpoint Mappings

### 1. Address Operations

#### Legacy to Modern Mapping
```
Legacy: ControlAddress methods
Modern: /api/v1/address/* endpoints
```

#### Endpoint Specifications
1. Validate Address
   ```
   POST /api/v1/address/validate
   
   Request:
   {
       "address_line1": "string",
       "address_line2": "string",
       "city": "string",
       "state": "string",
       "zip_code": "string"
   }
   
   Response:
   {
       "valid": boolean,
       "standardized_address": AddressModel,
       "validation_messages": string[]
   }
   ```

2. Search Addresses
   ```
   POST /api/v1/address/search
   
   Request:
   {
       "query": "string",
       "limit": integer,
       "offset": integer
   }
   
   Response:
   {
       "results": AddressModel[],
       "total": integer,
       "page": integer
   }
   ```

3. Geocode Address
   ```
   POST /api/v1/address/geocode
   
   Request:
   AddressModel
   
   Response:
   {
       "coordinates": {
           "latitude": float,
           "longitude": float
       },
       "confidence": float,
       "provider": string
   }
   ```

### 2. Name Operations

#### Legacy to Modern Mapping
```
Legacy: ControlName methods
Modern: /api/v1/name/* endpoints
```

#### Endpoint Specifications
1. Validate Name
   ```
   POST /api/v1/name/validate
   
   Request:
   {
       "first_name": "string",
       "middle_initial": "string",
       "last_name": "string",
       "suffix": "string",
       "courtesy_title": "string"
   }
   
   Response:
   {
       "valid": boolean,
       "standardized_name": NameModel,
       "validation_messages": string[]
   }
   ```

2. Format Name
   ```
   POST /api/v1/name/format
   
   Request:
   {
       "name": NameModel,
       "format_type": "full" | "formal" | "initials"
   }
   
   Response:
   {
       "formatted_name": "string"
   }
   ```

3. Parse Name
   ```
   POST /api/v1/name/parse
   
   Request:
   {
       "name_string": "string"
   }
   
   Response:
   NameModel
   ```

### 3. Map Operations

#### Legacy to Modern Mapping
```
Legacy: MapProvider events
Modern: /api/v1/map/* endpoints
```

#### Endpoint Specifications
1. Search Locations
   ```
   POST /api/v1/map/search
   
   Request:
   {
       "query": "string",
       "provider": "string",
       "limit": integer
   }
   
   Response:
   {
       "results": MapSearchResult[],
       "provider": string,
       "query_time": float
   }
   ```

2. Geocode
   ```
   POST /api/v1/map/geocode
   
   Request:
   AddressModel
   
   Response:
   {
       "location": MapLocation,
       "alternatives": MapLocation[],
       "provider": string
   }
   ```

## Error Response Format

### Standard Error Response
```json
{
    "status_code": integer,
    "error": string,
    "message": string,
    "details": {
        "field": ["error_details"]
    },
    "timestamp": string
}
```

### Error Type Mapping
```
400 Bad Request:
- ValidationError
- InvalidFormatError
- MissingFieldError

404 Not Found:
- AddressNotFoundError
- NameNotFoundError
- ResourceNotFoundError

500 Internal Server Error:
- MapProviderError
- DatabaseError
- SystemError
```

## API Versioning Rules

1. Version Format
   - Use /api/v1/* format
   - Include version in response headers
   - Support multiple versions

2. Deprecation Process
   - Add Sunset header
   - Provide migration path
   - Support grace period

3. Documentation
   - OpenAPI/Swagger specs
   - Version changelog
   - Migration guides
