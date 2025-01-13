# Navigator Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Navigator                     NavigatorService
└── UserControl              └── Service class
    └── Events                  └── Event handlers
    └── Grid control            └── Grid state

NavigatorEventsHandler       NavigatorService
└── Abstract class          └── Service class
    └── Event methods          └── Event handlers

NavigatorOptions            NavigatorOptions
└── Class                   └── Pydantic Model
    └── Properties             └── Fields

NavigatorRowClickEventArgs  NavigatorRowClickEvent
└── Class                   └── Pydantic Model
    └── Properties             └── Fields
```

## 2. Property Transformations

### Navigator Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Navigator:                    NavigatorService:
- m_tableNames               - _navigators
- m_filterQueue              - _create_source_handlers
- m_reloadQueue             - _fill_source_handlers
- grid                      - _row_click_handlers

NavigatorOptions:            NavigatorOptions:
- Caption                    - caption
- Switchable                - switchable
- TableNames                - table_names
- InitializeAppearance      - appearance
```

## 3. Supporting Models

### New Models
```
GridSortDirection (Enum):
- ASCENDING
- DESCENDING
- NONE

GridFilterType (Enum):
- TEXT
- NUMBER
- DATE
- BOOLEAN
- CUSTOM

GridColumnDefinition (Model):
- field
- title
- width
- sortable
- filterable
- visible
- filter_type
- format
- template
- metadata

GridAppearance (Model):
- columns
- allow_sorting
- allow_filtering
- allow_column_reorder
- allow_column_resize
- row_height
- header_height
- metadata

GridState (Model):
- filter_text
- sort_field
- sort_direction
- selected_rows
- visible_columns
- metadata

NavigatorState (Model):
- grid_state
- options
- is_loading
- error
- metadata
- timestamp
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Navigator:                    NavigatorService:
- CreateSource event         - create_navigator()
- FillSource event          - get_navigator_state()
- NavigatorRowClick event   - update_grid_state()
                            - set_filter()
                            - set_sort()
                            - handle_row_click()

NavigatorEventsHandler:      NavigatorService:
- CreateSource()            - add_create_source_handler()
- FillSource()             - add_fill_source_handler()
- NavigatorRowClick()      - add_row_click_handler()
```

## 5. Integration Points

### API Integration
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Navigator UI Control:        FastAPI Endpoints:
- User interaction          - /navigators
                           - /navigators/{id}
                           - /navigators/{id}/grid-state
                           - /navigators/{id}/filter
                           - /navigators/{id}/sort
                           - /navigators/{id}/row-click
```

## 6. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create navigator models
   class NavigatorOptions(BaseModel):
       caption: str = "Search"
       switchable: bool = True
       # ...

   # 2. Create grid models
   class GridState(BaseModel):
       filter_text: Optional[str] = None
       sort_field: Optional[str] = None
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create navigator service
   class NavigatorService(BaseService):
       async def create_navigator(
           self,
           options: NavigatorOptions
       ) -> str:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create navigator endpoints
   @router.post("/navigators")
   async def create_navigator(
       options: NavigatorOptions,
       current_user: User = Depends(get_current_user)
   ) -> str:
       # ...
   ```

## 7. Event Handling

1. **Event Types**
   - Create source event
   - Fill source event
   - Row click event

2. **Event Flow**
   ```
   User Action -> API Endpoint -> Service -> Event Handlers -> State Update
   ```

## 8. State Management

1. **Navigator State**
   - Grid state
   - Options
   - Loading state
   - Error state

2. **Grid State**
   - Filter state
   - Sort state
   - Selection state
   - Column state

## 9. Performance Considerations

1. **State Updates**
   - Efficient state updates
   - Minimal rerendering
   - Event debouncing
   - Batch updates

2. **Data Loading**
   - Lazy loading
   - Pagination
   - Caching
   - Background updates

## 10. Security Considerations

1. **Authentication**
   - User authentication
   - Session management
   - Token validation
   - Permission checks

2. **Data Access**
   - Row-level security
   - Column-level security
   - Data filtering
   - Audit logging

## 11. Testing Strategy

1. **Unit Tests**
   - Service tests
   - Model tests
   - Event tests
   - State tests

2. **Integration Tests**
   - API tests
   - Event flow tests
   - State flow tests
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
