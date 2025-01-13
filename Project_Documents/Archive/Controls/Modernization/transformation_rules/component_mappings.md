# Component Transformation Mappings

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
