# Controls Component Transformation Rules

## 1. ChangesTracker Transformation

### Source to Target Mapping
```
Legacy (C#)                          Modern (Python)
-----------------------------------------------
ChangesTracker                    -> EventTracker (Service)
- m_handler: EventHandler         -> handler: Callable
- m_provider: ErrorProvider       -> error_provider: Optional[ErrorProvider]
- Subscribe(Control)              -> subscribe(component: Component)
- HandleControlChanged           -> handle_control_changed
```

### Transformation Rules
1. Event Handler System
   - Convert C# event handler pattern to Python callback functions
   - Replace ErrorProvider with custom validation feedback system
   - Implement async event handling

2. Control Subscription
   - Map Windows Forms controls to FastAPI/Pydantic models
   - Convert synchronous event handling to async/await
   - Implement type-safe event propagation

3. Error Handling
   - Replace Windows Forms error provider with validation system
   - Implement structured error responses
   - Add comprehensive error tracking

## 2. ControlAddress Transformation

### Source to Target Mapping
```
Legacy (C#)                          Modern (Python)
-----------------------------------------------
ControlAddress                    -> AddressComponent
- txtAddress1: TextBox           -> address_line1: str
- txtAddress2: TextBox           -> address_line2: Optional[str]
- txtCity: TextBox               -> city: str
- txtState: TextBox              -> state: str
- txtZip: TextBox                -> zip_code: str
- btnMaps: Button                -> MapService integration
- btnFind: Button                -> AddressService search
```

### Transformation Rules
1. Data Model
   - Convert Windows Forms controls to Pydantic model
   - Add field validation and type checking
   - Implement data standardization

2. Map Integration
   - Replace button click events with async service calls
   - Support multiple map providers
   - Add geocoding capabilities

3. Address Validation
   - Implement comprehensive address validation
   - Add format standardization
   - Support international addresses

## 3. ControlName Transformation

### Source to Target Mapping
```
Legacy (C#)                          Modern (Python)
-----------------------------------------------
ControlName                      -> NameComponent
- txtFirstName: TextBox          -> first_name: str
- txtMiddleName: TextBox         -> middle_initial: Optional[str]
- txtLastName: TextBox           -> last_name: str
- txtSuffix: TextBox             -> suffix: Optional[str]
- cmbCourtesy: ComboBox         -> courtesy_title: Optional[CourtesyTitle]
```

### Transformation Rules
1. Data Model
   - Convert Windows Forms controls to Pydantic model
   - Add enumerated courtesy titles
   - Implement name parsing and formatting

2. Validation Rules
   - Add comprehensive name validation
   - Implement format standardization
   - Support international name formats

3. Name Operations
   - Add name parsing capabilities
   - Implement multiple format options
   - Support name matching algorithms

## 4. MapProviderEventArgs Transformation

### Source to Target Mapping
```
Legacy (C#)                          Modern (Python)
-----------------------------------------------
MapProviderEventArgs             -> MapProviderEvent
- Provider: MapProvider          -> provider: MapProvider
                                -> coordinates: Optional[MapCoordinates]
                                -> search_result: Optional[MapSearchResult]
```

### Transformation Rules
1. Event Model
   - Convert event args to Pydantic model
   - Add additional map provider metadata
   - Implement async event handling

2. Provider Integration
   - Support multiple map providers
   - Add provider configuration
   - Implement provider-specific parsing

3. Error Handling
   - Add structured error responses
   - Implement provider fallback
   - Add retry mechanisms

## 5. Database Schema Transformations

### Address Schema
```sql
-- Legacy Table
CREATE TABLE Addresses (
    ID INT PRIMARY KEY,
    Address1 VARCHAR(100),
    Address2 VARCHAR(100),
    City VARCHAR(50),
    State CHAR(2),
    ZipCode VARCHAR(10)
);

-- Modern Schema
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    address_line1 VARCHAR(100) NOT NULL,
    address_line2 VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    state CHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_state CHECK (state ~ '^[A-Z]{2}$'),
    CONSTRAINT valid_zip CHECK (zip_code ~ '^\d{5}(-\d{4})?$')
);
```

### Name Schema
```sql
-- Legacy Table
CREATE TABLE Names (
    ID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    MiddleName VARCHAR(50),
    LastName VARCHAR(50),
    Suffix VARCHAR(10),
    CourtesyTitle VARCHAR(10)
);

-- Modern Schema
CREATE TABLE names (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    middle_initial CHAR(1),
    last_name VARCHAR(50) NOT NULL,
    suffix VARCHAR(4),
    courtesy_title VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_suffix CHECK (suffix IN ('Jr.', 'Sr.', 'II', 'III', 'IV')),
    CONSTRAINT valid_courtesy CHECK (courtesy_title IN ('Mr.', 'Mrs.', 'Miss', 'Dr.', 'Rev.'))
);
```

## 6. API Transformation Rules

### RESTful Endpoints
1. Address Operations
   ```
   Legacy: ControlAddress methods
   Modern: /api/v1/address/* endpoints
   ```
   - POST /validate: Validate address
   - POST /search: Search addresses
   - POST /geocode: Geocode address
   - GET /by-zip/{zip_code}: Get by ZIP
   - GET /by-state/{state}: Get by state

2. Name Operations
   ```
   Legacy: ControlName methods
   Modern: /api/v1/name/* endpoints
   ```
   - POST /validate: Validate name
   - POST /format: Format name
   - POST /parse: Parse name string
   - GET /courtesy-titles: List titles

3. Map Operations
   ```
   Legacy: MapProvider events
   Modern: /api/v1/map/* endpoints
   ```
   - POST /search: Search locations
   - POST /geocode: Geocode address
   - POST /reverse: Reverse geocode

## 7. Error Handling Transformation

### Error Response Format
```json
{
    "status_code": 400,
    "error": "ValidationError",
    "message": "Detailed error message",
    "details": {
        "field": ["error_details"]
    },
    "timestamp": "2025-01-07T12:23:54-06:00"
}
```

### Error Mapping
```
Legacy                             Modern
-----------------------------------------------
ArgumentNullException           -> ValidationError
InvalidOperationException       -> OperationError
Exception                       -> SystemError
```

## 8. Validation Rules Transformation

### Address Validation
```python
# Legacy
if (string.IsNullOrEmpty(txtState.Text))
    throw new ArgumentException("State is required");

# Modern
@validator('state')
def validate_state(cls, v):
    if not v:
        raise ValueError('State is required')
    if not re.match(r'^[A-Z]{2}$', v):
        raise ValueError('State must be 2 uppercase letters')
    return v
```

### Name Validation
```python
# Legacy
if (string.IsNullOrEmpty(txtFirstName.Text))
    throw new ArgumentException("First name is required");

# Modern
@validator('first_name')
def validate_first_name(cls, v):
    if not v:
        raise ValueError('First name is required')
    return v.strip().title()
```

## 9. Migration Steps

1. Data Migration
   - Export legacy data to JSON format
   - Transform using provided mappings
   - Import to new schema
   - Validate data integrity

2. Code Migration
   - Convert C# classes to Python
   - Implement new validation rules
   - Add API endpoints
   - Set up async services

3. Testing
   - Unit tests for models
   - Integration tests for services
   - API endpoint tests
   - Data migration tests
