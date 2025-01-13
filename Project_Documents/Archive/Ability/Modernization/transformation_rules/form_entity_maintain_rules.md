# FormEntityMaintain Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
FormEntityMaintain            FormEntity[T]
└── Form-specific Class       └── Generic Pydantic Model
    └── Limited Type Safety       └── Full Type Safety
    └── No Validation            └── Full Validation
    └── Windows Forms specific   └── Framework Agnostic
```

## 2. Property Transformations

### Entity Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Various properties           FormEntity:
                            - id: str
                            - state: EntityState
                            - data: T
                            - validation: EntityValidation
                            - audit: EntityAudit
                            - metadata: Dict[str, Any]
```

## 3. Supporting Models

### New Models
```
EntityState (Enum):
- NEW
- MODIFIED
- DELETED
- UNCHANGED

ValidationSeverity (Enum):
- ERROR
- WARNING
- INFO

ValidationResult (Model):
- field: str
- message: str
- severity: ValidationSeverity
- code: Optional[str]
- params: Dict[str, Any]

EntityValidation (Model):
- is_valid: bool
- results: List[ValidationResult]
- metadata: Dict[str, Any]

EntityAudit (Model):
- created_at: datetime
- created_by: str
- modified_at: Optional[datetime]
- modified_by: Optional[str]
- version: int

FormEntityCollection (Model):
- entities: Dict[str, FormEntity[T]]
- validation: EntityValidation
- metadata: Dict[str, Any]
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Various methods              FormEntityService:
                            - create_collection()
                            - add_entity()
                            - update_entity()
                            - delete_entity()
                            - get_entity()
                            - get_modified_entities()
                            - add_validator()
```

## 5. Data Type Transformations

### Type Mappings
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
object                        Generic[T]
string                       str
bool                         bool
DateTime                     datetime
null                         Optional[Type]
Dictionary                   Dict[str, Any]
```

## 6. API Transformations

### Endpoint Mappings
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No API endpoints             FastAPI Endpoints:
                            POST /collections
                            POST /collections/{id}/entities
                            PUT /collections/{id}/entities/{id}
                            DELETE /collections/{id}/entities/{id}
                            GET /collections/{id}/entities/{id}
                            GET /collections/{id}/entities/modified
```

## 7. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create enums
   class EntityState(str, Enum):
       NEW = "new"
       MODIFIED = "modified"
       # ...

   # 2. Create models
   class FormEntity(BaseModel, Generic[T]):
       id: str
       state: EntityState
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create service
   class FormEntityService(BaseService, Generic[T]):
       async def create_collection(self) -> str:
           # ...
       
       async def add_entity(
           self,
           collection_id: str,
           data: T,
           user_id: str
       ) -> FormEntity[T]:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create endpoints
   @router.post("/collections/{collection_id}/entities")
   async def add_entity(
       collection_id: str,
       data: Dict[str, Any],
       current_user: User = Depends(get_current_user)
   ) -> FormEntity[Dict[str, Any]]:
       # ...
   ```

## 8. Validation Requirements

1. **Entity Validation**
   - Entity state must be valid
   - Required fields must be present
   - Data must match schema
   - Audit trail must be maintained

2. **Collection Validation**
   - Entity IDs must be unique
   - Collection must be valid
   - Modified entities tracked
   - State consistency maintained

## 9. Error Handling

1. **Input Validation**
   ```python
   # Handle validation errors
   try:
       FormEntity(...)
   except ValidationError as e:
       handle_validation_error(e)
   ```

2. **Service Errors**
   ```python
   # Handle service errors
   try:
       await form_entity_service.add_entity(...)
   except HTTPException as e:
       handle_service_error(e)
   ```

## 10. Performance Considerations

1. **Collection Management**
   - Efficient entity storage
   - Optimized lookups
   - Batch operations
   - Memory management

2. **Validation**
   - Cached validators
   - Efficient validation
   - Minimal revalidation
   - Quick state checks

## 11. Security Considerations

1. **Authentication**
   - User authentication
   - Permission checking
   - Audit logging
   - Session validation

2. **Data Protection**
   - Input validation
   - Output sanitization
   - State protection
   - Version control

## 12. Testing Strategy

1. **Unit Tests**
   - Test entity operations
   - Test validation logic
   - Test state management
   - Test error handling

2. **Integration Tests**
   - Test API endpoints
   - Test service integration
   - Test collection management
   - Test data persistence

3. **Migration Tests**
   - Test data conversion
   - Test state preservation
   - Test audit trail
   - Test performance impact

## 13. Documentation Requirements

1. **API Documentation**
   - Endpoint descriptions
   - Request/response formats
   - Error codes
   - Examples

2. **Code Documentation**
   - Class documentation
   - Method documentation
   - Type hints
   - Usage examples
