# EntityValidation Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
EntityValidation              EntityValidation[T]
└── Basic Class               └── Generic Pydantic Model
    └── Limited Type Safety       └── Full Type Safety
    └── Basic Validation         └── Comprehensive Validation
    └── Windows Forms specific   └── Framework Agnostic
```

## 2. Property Transformations

### Validation Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Various properties           EntityValidation:
                            - entity: T
                            - is_valid: bool
                            - results: List[ValidationResult]
                            - context: ValidationContext
                            - metadata: Dict[str, Any]
                            - timestamp: datetime
```

## 3. Supporting Models

### New Models
```
ValidationSeverity (Enum):
- ERROR
- WARNING
- INFO

ValidationCategory (Enum):
- REQUIRED
- FORMAT
- RANGE
- CUSTOM
- BUSINESS
- RELATIONSHIP

ValidationScope (Enum):
- FIELD
- ENTITY
- COLLECTION
- CROSS_ENTITY

ValidationResult (Model):
- field: Optional[str]
- message: str
- severity: ValidationSeverity
- category: ValidationCategory
- scope: ValidationScope
- code: Optional[str]
- params: Dict[str, Any]
- metadata: Dict[str, Any]
- timestamp: datetime

ValidationContext (Model):
- entity_type: str
- operation: str
- user_id: Optional[str]
- metadata: Dict[str, Any]
- timestamp: datetime

ValidationRule (Model):
- name: str
- description: str
- category: ValidationCategory
- scope: ValidationScope
- severity: ValidationSeverity
- message_template: str
- enabled: bool
- metadata: Dict[str, Any]

ValidationRuleSet (Model):
- name: str
- description: str
- entity_type: str
- rules: List[ValidationRule]
- enabled: bool
- metadata: Dict[str, Any]
- created_at: datetime
- modified_at: Optional[datetime]

ValidationSummary (Model):
- total_count: int
- error_count: int
- warning_count: int
- info_count: int
- categories: Dict[ValidationCategory, int]
- scopes: Dict[ValidationScope, int]
- metadata: Dict[str, Any]
- timestamp: datetime
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Various methods              ValidationService:
                            - create_rule_set()
                            - validate_entity()
                            - add_validator()
                            - remove_validator()
                            - get_rule_set()
                            - update_rule_set()
                            - delete_rule_set()
                            - get_rule_sets_for_entity()
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
List                        List[Type]
```

## 6. API Transformations

### Endpoint Mappings
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No API endpoints             FastAPI Endpoints:
                            POST /validation/rule-sets
                            POST /validation/entities
                            GET /validation/rule-sets/{id}
                            PUT /validation/rule-sets/{id}
                            DELETE /validation/rule-sets/{id}
                            GET /validation/rule-sets/entity/{type}
```

## 7. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create enums
   class ValidationSeverity(str, Enum):
       ERROR = "error"
       WARNING = "warning"
       INFO = "info"

   # 2. Create models
   class EntityValidation(GenericModel, Generic[T]):
       entity: T
       is_valid: bool = True
       results: List[ValidationResult]
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create service
   class ValidationService(BaseService, Generic[T]):
       async def validate_entity(
           self,
           entity: T,
           context: ValidationContext
       ) -> EntityValidation[T]:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create endpoints
   @router.post("/validation/entities")
   async def validate_entity(
       entity: Dict[str, Any],
       context: ValidationContext,
       current_user: User = Depends(get_current_user)
   ) -> EntityValidation[Dict[str, Any]]:
       # ...
   ```

## 8. Validation Requirements

1. **Entity Validation**
   - Field validation
   - Entity-level validation
   - Cross-entity validation
   - Business rule validation

2. **Rule Set Validation**
   - Rule set integrity
   - Rule consistency
   - Rule dependencies
   - Rule conflicts

## 9. Error Handling

1. **Input Validation**
   ```python
   # Handle validation errors
   try:
       EntityValidation(...)
   except ValidationError as e:
       handle_validation_error(e)
   ```

2. **Service Errors**
   ```python
   # Handle service errors
   try:
       await validation_service.validate_entity(...)
   except HTTPException as e:
       handle_service_error(e)
   ```

## 10. Performance Considerations

1. **Validation Processing**
   - Efficient validation
   - Rule caching
   - Batch validation
   - Memory management

2. **Rule Management**
   - Efficient rule storage
   - Rule caching
   - Quick lookups
   - Minimal updates

## 11. Security Considerations

1. **Authentication**
   - User authentication
   - Permission checking
   - Rule access control
   - Validation scope

2. **Data Protection**
   - Input validation
   - Output sanitization
   - Rule protection
   - Context validation

## 12. Testing Strategy

1. **Unit Tests**
   - Test validation logic
   - Test rule management
   - Test error handling
   - Test performance

2. **Integration Tests**
   - Test API endpoints
   - Test service integration
   - Test rule flow
   - Test validation flow

3. **Migration Tests**
   - Test data conversion
   - Test rule migration
   - Test validation compatibility
   - Test performance impact

## 13. Documentation Requirements

1. **API Documentation**
   - Endpoint descriptions
   - Validation rules
   - Error handling
   - Examples

2. **Code Documentation**
   - Class documentation
   - Method documentation
   - Type hints
   - Usage examples
