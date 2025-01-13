# CreateSourceEventArgs Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
CreateSourceEventArgs          CreateSourceEventArgs[T]
└── EventArgs Class           └── Generic Pydantic Model
    └── Limited Type Safety       └── Full Type Safety
    └── No Validation            └── Full Validation
    └── Windows Forms specific   └── Framework Agnostic
```

## 2. Property Transformations

### Event Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Source property               source: Optional[T]
Cancelled property           cancelled: bool
No error handling            error: Optional[str]
No metadata                  metadata: Dict[str, Any]
```

## 3. Supporting Models

### New Models
```
GridSourceType (Enum):
- TABLE
- QUERY
- CUSTOM
- VIRTUAL

GridSource (Model):
- type: GridSourceType
- name: str
- schema: Dict[str, Any]
- metadata: Dict[str, Any]

SourceCreatedEvent (Model):
- source_id: str
- source_type: GridSourceType
- timestamp: float
- metadata: Dict[str, Any]

SourceEventContext (Model):
- user_id: str
- session_id: str
- form_id: Optional[str]
- metadata: Dict[str, Any]
```

## 4. Data Type Transformations

### Type Mappings
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
object                        Generic[T]
bool                         bool
null                         Optional[Type]
no validation                Pydantic validation
no type hints                Full type hints
```

## 5. Service Layer Transformations

### Service Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No service layer             EventService[T]:
                            - create_source()
                            - get_source()
                            - get_source_event()
                            - delete_source()
```

## 6. API Transformations

### Endpoint Mappings
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No API endpoints             FastAPI Endpoints:
                            POST /sources
                            GET /sources/{source_id}
                            GET /sources/{source_id}/event
                            DELETE /sources/{source_id}
```

## 7. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create GridSourceType enum
   class GridSourceType(str, Enum):
       TABLE = "table"
       QUERY = "query"
       # ...

   # 2. Create CreateSourceEventArgs
   class CreateSourceEventArgs(GenericModel, Generic[T]):
       source: Optional[T] = None
       cancelled: bool = False
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create EventService
   class EventService(BaseService, Generic[T]):
       async def create_source(
           self,
           source_type: GridSourceType,
           schema: Dict[str, Any],
           context: SourceEventContext
       ) -> CreateSourceEventArgs[T]:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create API endpoints
   @router.post("/sources")
   async def create_source(
       source_type: GridSourceType,
       schema: Dict[str, Any],
       current_user: User = Depends(get_current_user)
   ) -> CreateSourceEventArgs[GridSource]:
       # ...
   ```

## 8. Testing Strategy

1. **Unit Tests**
   - Test CreateSourceEventArgs validation
   - Test EventService methods
   - Test type safety
   - Test error handling

2. **Integration Tests**
   - Test API endpoints
   - Test service integration
   - Test event flow
   - Test error scenarios

3. **Migration Tests**
   - Test data conversion
   - Test type compatibility
   - Test event handling
   - Test performance impact

## 9. Validation Requirements

1. **Data Validation**
   - Source type must be valid
   - Schema must be valid JSON
   - Required fields must be present
   - Types must match specifications

2. **Business Rules**
   - Source IDs must be unique
   - Events must have context
   - Timestamps must be valid
   - Metadata must be JSON

## 10. Error Handling

1. **Input Validation**
   ```python
   # Handle validation errors
   try:
       CreateSourceEventArgs(...)
   except ValidationError as e:
       handle_validation_error(e)
   ```

2. **Service Errors**
   ```python
   # Handle service errors
   try:
       await event_service.create_source(...)
   except Exception as e:
       return CreateSourceEventArgs(
           cancelled=True,
           error=str(e)
       )
   ```

## 11. Performance Considerations

1. **Event Processing**
   - Async event handling
   - Efficient source storage
   - Optimized lookups
   - Metadata indexing

2. **Memory Management**
   - Efficient generic types
   - Proper cleanup
   - Resource management
   - Cache optimization

## 12. Security Considerations

1. **Authentication**
   - User authentication
   - Session validation
   - Permission checking
   - Audit logging

2. **Data Protection**
   - Input sanitization
   - Output encoding
   - Metadata validation
   - Error message safety
