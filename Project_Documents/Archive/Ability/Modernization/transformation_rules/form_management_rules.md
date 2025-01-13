# Form Management Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
FormMaintainBase             FormManagementService
└── DmeForm                  └── BaseService
    └── IParameters             └── Generic[T]

FormMaintain                 FormManagementService
└── FormMaintainBase        └── BaseService
    └── Object operations      └── CRUD operations

FormEntityMaintain          EntityFormService
└── FormMaintainBase        └── FormManagementService
    └── Entity operations      └── Entity operations
```

## 2. Property Transformations

### Form Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
FormMaintainBase:            FormData:
- _ButtonClone              - buttons.button_clone
- _ButtonClose             - buttons.button_close
- _ButtonDelete            - buttons.button_delete
- _ButtonMissing           - buttons.button_missing
- _ButtonNew               - buttons.button_new
- _ButtonReload            - buttons.button_reload
- FStateStack              - metadata.state
- m_changesTracker        - changes
```

## 3. Supporting Models

### New Models
```
FormState (Enum):
- NEW
- EXISTING
- MODIFIED
- DELETED
- LOADING
- SAVING
- VALIDATING
- ERROR

ButtonConfig (Model):
- button_clone
- button_close
- button_delete
- button_missing
- button_new
- button_reload
- button_save
- button_search
- button_print
- button_goto
- button_actions
- button_filter

ValidationMessage (Model):
- field
- message
- severity
- code

ValidationResult (Model):
- is_valid
- messages
- metadata

FormMetadata (Model):
- form_id
- form_type
- title
- state
- created_at
- updated_at
- entity_id
- validation
- metadata

FormData (Model):
- metadata
- data
- changes
- buttons

FormEvent (Model):
- event_type
- form_id
- entity_id
- data
- timestamp
- metadata
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
FormMaintainBase:            FormManagementService:
- AddNavigator()            - create_form()
- ClearObject()            - get_form()
- CloneObject()            - update_form()
- DeleteObject()           - validate_form()
- LoadObject()             - save_form()
- SaveObject()             - delete_form()
- ValidateObject()         - subscribe()
                          - unsubscribe()
                          - _publish_event()
```

## 5. Integration Points

### API Integration
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Form Operations:            FastAPI Endpoints:
- Direct method calls      - POST /forms
                          - GET /forms/{form_id}
                          - PUT /forms/{form_id}
                          - POST /forms/{form_id}/validate
                          - POST /forms/{form_id}/save
                          - DELETE /forms/{form_id}
```

## 6. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create form models
   class FormData(BaseModel):
       metadata: FormMetadata
       data: Dict[str, Any]
       changes: Dict[str, Any]
       buttons: ButtonConfig

   # 2. Create validation models
   class ValidationResult(BaseModel):
       is_valid: bool
       messages: List[ValidationMessage]
       metadata: Dict[str, Any]
   ```

2. **Service Implementation**
   ```python
   # 1. Create form service
   class FormManagementService(BaseService, Generic[T]):
       async def create_form(
           self,
           form_type: str,
           title: str,
           # ...
       ) -> FormData:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create form endpoints
   @router.post("/forms")
   async def create_form(
       form_type: str,
       title: str,
       # ...
   ) -> FormData:
       # ...
   ```

## 7. Form States

1. **State Management**
   - NEW: Initial form state
   - EXISTING: Loaded form
   - MODIFIED: Changed form
   - DELETED: Deleted form
   - LOADING: Loading data
   - SAVING: Saving data
   - VALIDATING: Validating data
   - ERROR: Validation failed

## 8. Form Events

1. **Event Types**
   - form_created
   - form_updated
   - form_validated
   - form_saved
   - form_deleted

2. **Event Data**
   - Event type
   - Form ID
   - Entity ID
   - Data payload
   - Timestamp
   - Metadata

## 9. Performance Considerations

1. **Form Management**
   - In-memory form storage
   - Form state tracking
   - Change tracking
   - Event handling

2. **Data Processing**
   - Async operations
   - Validation
   - Error handling
   - Event publishing

## 10. Security Considerations

1. **Form Access**
   - Authentication
   - Authorization
   - Data visibility
   - Form permissions

2. **Data Validation**
   - Input validation
   - Schema validation
   - Type checking
   - Data sanitization

## 11. Testing Strategy

1. **Unit Tests**
   - Form creation
   - Form operations
   - Validation
   - Event handling

2. **Integration Tests**
   - API endpoints
   - Form flow
   - Data persistence
   - Security tests

## 12. Documentation Requirements

1. **Code Documentation**
   - Class documentation
   - Method documentation
   - Type hints
   - Usage examples

2. **API Documentation**
   - Endpoint documentation
   - Request/response schemas
   - Error codes
   - Authentication
