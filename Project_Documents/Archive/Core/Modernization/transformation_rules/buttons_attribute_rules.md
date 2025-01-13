# ButtonsAttribute Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
ButtonsAttribute               ButtonsAttribute
└── Attribute Class           └── Descriptor Class
    └── No Type Safety            └── Full Type Safety with Pydantic

[ButtonsAttribute]             [ButtonDefinition + ButtonsAttribute]
- Class Attribute             - Pydantic Model + Descriptor
- No Validation              - Full Validation
- Limited Type Safety        - Strong Type Safety
- Windows Forms specific     - Framework Agnostic
```

## 2. Property Transformations

### Button Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No explicit properties         ButtonDefinition:
                              - id: str
                              - type: ButtonType
                              - label: str
                              - icon: Optional[str]
                              - tooltip: Optional[str]
                              - disabled: bool
                              - visible: bool
                              - permission: Optional[str]
                              - order: int
                              - custom_class: Optional[str]
```

## 3. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No explicit methods           ButtonsAttribute:
                             - get_visible_buttons()
                             - enable_button()
                             - disable_button()
                             - show_button()
                             - hide_button()
                             - update_button_label()
```

## 4. Data Type Transformations

### Type Mappings
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
string                        str
bool                         bool
implicit null                Optional[Type]
no enums                     ButtonType(Enum)
```

## 5. Validation Rules

### Input Validation
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No validation                 Pydantic Validation:
                             - Required fields
                             - Type checking
                             - Enum validation
                             - Optional fields
                             - Custom validators
```

## 6. API Transformations

### Endpoint Mappings
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No API endpoints             FastAPI Endpoints:
                            GET /buttons/{form_id}
                            PATCH /buttons/{form_id}/{button_id}/state
                            PATCH /buttons/{form_id}/{button_id}/label
```

## 7. Service Layer Transformations

### Service Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
No service layer             ButtonService:
                            - get_form_buttons()
                            - update_button_state()
                            - update_button_label()
                            - _get_buttons_attribute()
                            - _save_buttons_attribute()
```

## 8. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create ButtonType enum
   class ButtonType(str, Enum):
       SUBMIT = "submit"
       CANCEL = "cancel"
       # ...

   # 2. Create ButtonDefinition model
   class ButtonDefinition(BaseModel):
       id: str
       type: ButtonType
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create ButtonService class
   class ButtonService(BaseService):
       async def get_form_buttons(self, form_id: str) -> List[ButtonDefinition]:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create API router
   router = APIRouter()

   # 2. Implement endpoints
   @router.get("/buttons/{form_id}")
   async def get_form_buttons(form_id: str):
       # ...
   ```

## 9. Testing Strategy

1. **Unit Tests**
   - Test ButtonDefinition validation
   - Test ButtonsAttribute methods
   - Test ButtonService methods

2. **Integration Tests**
   - Test API endpoints
   - Test service integration
   - Test database operations

3. **Migration Tests**
   - Test data conversion
   - Test backward compatibility
   - Test performance impact

## 10. Deployment Considerations

1. **Database Updates**
   - Create new button tables/collections
   - Migrate existing button data
   - Update references

2. **API Versioning**
   - Version new endpoints
   - Maintain compatibility
   - Document changes

3. **Frontend Updates**
   - Update button components
   - Update form handling
   - Update state management

## 11. Validation Requirements

1. **Data Validation**
   - Button IDs must be unique
   - Button orders must be unique
   - Required fields must be present
   - Types must match specifications

2. **Business Rules**
   - Buttons must have unique IDs
   - Orders must be sequential
   - Permissions must be valid
   - States must be consistent

## 12. Error Handling

1. **Input Validation Errors**
   ```python
   # Handle validation errors
   try:
       ButtonDefinition(...)
   except ValidationError as e:
       handle_validation_error(e)
   ```

2. **Service Errors**
   ```python
   # Handle service errors
   try:
       await button_service.update_button_state(...)
   except HTTPException as e:
       handle_service_error(e)
   ```

## 13. Performance Considerations

1. **Caching**
   - Cache button definitions
   - Cache permission checks
   - Cache visible buttons

2. **Optimization**
   - Batch button updates
   - Minimize database calls
   - Use efficient queries
