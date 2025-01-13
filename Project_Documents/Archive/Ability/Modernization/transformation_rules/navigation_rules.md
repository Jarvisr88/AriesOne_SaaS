# Navigation System Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Navigator                    NavigationService
└── UserControl              └── BaseService
    └── Grid control            └── Event system

NavigatorEventsHandler      NavigationService
└── Abstract class          └── Event handlers
    └── Event methods          └── Async methods

NavigatorOptions            NavigatorOptions
└── Basic options           └── Enhanced options
    └── Event handlers         └── Configuration
```

## 2. Property Transformations

### Navigator Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Navigator:                   NavigatorData:
- m_tableNames              - metadata.options.table_names
- m_filterQueue            - metadata.filter
- m_reloadQueue           - metadata.state
- grid                    - data
```

## 3. Supporting Models

### New Models
```
NavigatorState (Enum):
- IDLE
- LOADING
- FILTERING
- ERROR

GridAppearance (Model):
- columns
- column_order
- column_widths
- sort_columns
- sort_directions
- row_height
- theme
- metadata

NavigatorOptions (Model):
- table_names
- appearance
- enable_filtering
- enable_sorting
- enable_column_resize
- enable_column_reorder
- enable_row_selection
- page_size
- metadata

NavigatorFilter (Model):
- text
- columns
- case_sensitive
- metadata

NavigatorSort (Model):
- column
- ascending

NavigatorMetadata (Model):
- navigator_id
- state
- created_at
- updated_at
- filter
- sorts
- options
- metadata

NavigatorData (Model):
- metadata
- data
- total_rows
- filtered_rows
- page
- page_count

NavigatorEvent (Model):
- event_type
- navigator_id
- data
- timestamp
- metadata

RowClickEvent (Model):
- navigator_id
- row_index
- row_data
- column
- metadata
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Navigator:                   NavigationService:
- CreateSource()            - create_navigator()
- FillSource()             - get_navigator()
- NavigatorRowClick()      - update_filter()
- InitializeComponent()    - update_sort()
                          - load_data()
                          - handle_row_click()
                          - delete_navigator()
                          - subscribe()
                          - unsubscribe()
```

## 5. Integration Points

### API Integration
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Navigator Operations:       FastAPI Endpoints:
- Direct method calls      - POST /navigators
                          - GET /navigators/{id}
                          - PUT /navigators/{id}/filter
                          - PUT /navigators/{id}/sort
                          - PUT /navigators/{id}/data
                          - POST /navigators/{id}/row-click
                          - DELETE /navigators/{id}
```

## 6. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create navigator models
   class NavigatorData(BaseModel):
       metadata: NavigatorMetadata
       data: List[Dict[str, Any]]
       total_rows: int
       filtered_rows: int
       page: Optional[int]
       page_count: Optional[int]

   # 2. Create event models
   class NavigatorEvent(BaseModel):
       event_type: str
       navigator_id: UUID
       data: Optional[Dict[str, Any]]
       timestamp: datetime
       metadata: Dict[str, Any]
   ```

2. **Service Implementation**
   ```python
   # 1. Create navigation service
   class NavigationService(BaseService):
       async def create_navigator(
           self,
           table_names: Optional[Set[str]] = None,
           options: Optional[NavigatorOptions] = None,
           metadata: Optional[Dict[str, Any]] = None
       ) -> NavigatorData:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create navigator endpoints
   @router.post("/navigators")
   async def create_navigator(
       table_names: Optional[Set[str]] = None,
       options: Optional[NavigatorOptions] = None,
       metadata: Optional[Dict[str, Any]] = None
   ) -> NavigatorData:
       # ...
   ```

## 7. Navigation States

1. **State Management**
   - IDLE: Ready for interaction
   - LOADING: Loading data
   - FILTERING: Applying filters
   - ERROR: Error state

## 8. Navigation Events

1. **Event Types**
   - navigator_created
   - navigator_filtered
   - navigator_sorted
   - navigator_loaded
   - navigator_deleted
   - row_clicked

2. **Event Data**
   - Event type
   - Navigator ID
   - Data payload
   - Timestamp
   - Metadata

## 9. Performance Considerations

1. **Data Management**
   - In-memory data storage
   - Data pagination
   - Filter optimization
   - Sort optimization

2. **Event Processing**
   - Async operations
   - Event queuing
   - Error handling
   - Event publishing

## 10. Security Considerations

1. **Navigator Access**
   - Authentication
   - Authorization
   - Data visibility
   - Navigator permissions

2. **Data Validation**
   - Input validation
   - Filter validation
   - Sort validation
   - Data sanitization

## 11. Testing Strategy

1. **Unit Tests**
   - Navigator creation
   - Data operations
   - Filter/sort
   - Event handling

2. **Integration Tests**
   - API endpoints
   - Data flow
   - Event flow
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
