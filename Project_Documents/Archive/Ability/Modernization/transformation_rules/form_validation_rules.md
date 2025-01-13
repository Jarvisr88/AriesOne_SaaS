# Form Validation Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
IValidationResult             ValidationResult
└── Interface                 └── Pydantic Model
    └── Values property          └── values field
    └── Basic validation         └── Enhanced validation

IError                        ValidationError
└── Interface                 └── Pydantic Model
    └── Message property         └── message field
    └── IsError property         └── is_error field
```

## 2. Property Transformations

### Validation Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
IValidationResult:           ValidationResult:
- Values                     - values: Dict[str, List[ValidationError]]
                            - metadata: Dict[str, Any]
                            - timestamp: datetime

IError:                      ValidationError:
- Message                    - field: Optional[str]
- IsError                    - message: str
                            - is_error: bool
                            - code: Optional[str]
                            - params: Dict[str, Any]
                            - metadata: Dict[str, Any]
                            - timestamp: datetime
```

## 3. Supporting Models

### New Models
```
ErrorSeverity (Enum):
- ERROR
- WARNING
- INFO

EntityValidator[T] (Model):
- entity: T
- metadata: Dict[str, Any]
+ validate() -> ValidationResult
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Adapter.Validate()           FormValidationService:
                            - validate_entity()
                            - add_validator()
                            - remove_validator()
                            - format_validation_message()

ValidationResult:            ValidationResult:
                            - add_error()
                            - has_errors()
                            - has_warnings()
                            - get_error_messages()
                            - get_warning_messages()
```

## 5. Integration Points

### Form Entity Integration
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
FormEntityMaintain:          FormEntityService:
- PrivateValidateEntity()    - validate_entity()
- LoadValidationResult()     - load_validation_result()
```

## 6. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create validation error model
   class ValidationError(BaseModel):
       field: Optional[str] = None
       message: str
       is_error: bool = True
       # ...

   # 2. Create validation result model
   class ValidationResult(BaseModel):
       values: Dict[str, List[ValidationError]]
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create validation service
   class FormValidationService(BaseService, Generic[T]):
       async def validate_entity(
           self,
           entity_type: str,
           entity: T
       ) -> ValidationResult:
           # ...
   ```

3. **Integration Implementation**
   ```python
   # 1. Integrate with form entity service
   class FormEntityService(BaseService, Generic[T]):
       async def validate_entity(
           self,
           entity: T
       ) -> ValidationResult:
           # ...
   ```

## 7. Validation Requirements

1. **Error Handling**
   - Field-level validation
   - Entity-level validation
   - Custom validation rules
   - Error message formatting

2. **Warning Handling**
   - Warning detection
   - Warning message formatting
   - User confirmation handling

## 8. Error Message Format

1. **Error Messages**
   ```
   There are some errors in the input data:
   - [Error Message 1]
   - [Error Message 2]
   ...
   Cannot proceed.
   ```

2. **Warning Messages**
   ```
   There are some warnings in the input data:
   - [Warning Message 1]
   - [Warning Message 2]
   ...
   Do you want to proceed?
   ```

## 9. Performance Considerations

1. **Validation Processing**
   - Efficient validation
   - Early termination
   - Batch validation
   - Result caching

2. **Message Formatting**
   - Efficient string building
   - Message caching
   - Template usage

## 10. Security Considerations

1. **Input Validation**
   - Data sanitization
   - Type checking
   - Size limits
   - Format validation

2. **Error Messages**
   - No sensitive data
   - Generic messages
   - Sanitized output
   - Limited detail

## 11. Testing Strategy

1. **Unit Tests**
   - Test validation logic
   - Test error handling
   - Test message formatting
   - Test integration

2. **Integration Tests**
   - Test form integration
   - Test service integration
   - Test error flow
   - Test warning flow

## 12. Documentation Requirements

1. **Code Documentation**
   - Class documentation
   - Method documentation
   - Type hints
   - Usage examples

2. **Error Documentation**
   - Error codes
   - Error messages
   - Warning types
   - Validation rules
