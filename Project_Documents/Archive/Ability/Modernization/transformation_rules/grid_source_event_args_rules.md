# GridSourceEventArgs Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
GridSourceEventArgs            GridSourceEventArgs[T]
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
Various properties           GridSourceEventArgs:
                            - event_type: GridEventType
                            - data: Optional[List[T]]
                            - sort_info: List[GridSortInfo]
                            - filter_info: List[GridFilterInfo]
                            - paging_info: GridPagingInfo
                            - cancelled: bool
                            - error: Optional[str]
                            - metadata: Dict[str, Any]
                            - timestamp: datetime
```

## 3. Supporting Models

### New Models
```
GridEventType (Enum):
- DATA_FETCH
- DATA_UPDATE
- SELECTION_CHANGE
- SORT_CHANGE
- FILTER_CHANGE
- PAGE_CHANGE
- CUSTOM

GridSortDirection (Enum):
- ASCENDING
- DESCENDING

GridFilterOperator (Enum):
- EQUALS
- NOT_EQUALS
- GREATER_THAN
- LESS_THAN
- CONTAINS
- STARTS_WITH
- ENDS_WITH
- IN
- NOT_IN
- BETWEEN

GridSortInfo (Model):
- field: str
- direction: GridSortDirection
- priority: int

GridFilterInfo (Model):
- field: str
- operator: GridFilterOperator
- value: Any
- logic: Optional[str]

GridPagingInfo (Model):
- page: int
- page_size: int
- total_records: Optional[int]
- total_pages: Optional[int]

GridStateSnapshot (Model):
- sort_info: List[GridSortInfo]
- filter_info: List[GridFilterInfo]
- paging_info: GridPagingInfo
- selected_rows: List[str]
- metadata: Dict[str, Any]
- timestamp: datetime
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Various methods              GridEventService:
                            - create_grid_source()
                            - handle_event()
                            - add_event_handler()
                            - remove_event_handler()
                            - get_grid_state()
                            - update_grid_state()
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
                            POST /grids
                            POST /grids/{id}/events
                            GET /grids/{id}/state
                            PUT /grids/{id}/state
                            POST /grids/{id}/selection
                            POST /grids/{id}/custom
```

## 7. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create enums
   class GridEventType(str, Enum):
       DATA_FETCH = "data_fetch"
       DATA_UPDATE = "data_update"
       # ...

   # 2. Create models
   class GridSourceEventArgs(GenericModel, Generic[T]):
       event_type: GridEventType
       data: Optional[List[T]] = None
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create service
   class GridEventService(BaseService, Generic[T]):
       async def create_grid_source(
           self,
           initial_state: Optional[GridStateSnapshot] = None
       ) -> str:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create endpoints
   @router.post("/grids/{grid_id}/events")
   async def handle_grid_event(
       grid_id: str,
       event: GridSourceEventArgs[Dict[str, Any]],
       current_user: User = Depends(get_current_user)
   ) -> GridSourceEventArgs[Dict[str, Any]]:
       # ...
   ```

## 8. Validation Requirements

1. **Event Validation**
   - Event type must be valid
   - Sort info must be valid
   - Filter info must be valid
   - Paging info must be valid

2. **State Validation**
   - Grid ID must exist
   - State must be consistent
   - Timestamps must be valid
   - Data must be valid

## 9. Error Handling

1. **Input Validation**
   ```python
   # Handle validation errors
   try:
       GridSourceEventArgs(...)
   except ValidationError as e:
       handle_validation_error(e)
   ```

2. **Service Errors**
   ```python
   # Handle service errors
   try:
       await grid_event_service.handle_event(...)
   except HTTPException as e:
       handle_service_error(e)
   ```

## 10. Performance Considerations

1. **Event Processing**
   - Efficient event handling
   - Optimized state updates
   - Batch operations
   - Memory management

2. **State Management**
   - Efficient state storage
   - State caching
   - Minimal updates
   - Quick lookups

## 11. Security Considerations

1. **Authentication**
   - User authentication
   - Permission checking
   - Event validation
   - State protection

2. **Data Protection**
   - Input validation
   - Output sanitization
   - State validation
   - Event filtering

## 12. Testing Strategy

1. **Unit Tests**
   - Test event handling
   - Test state management
   - Test validation
   - Test error handling

2. **Integration Tests**
   - Test API endpoints
   - Test service integration
   - Test event flow
   - Test state persistence

3. **Migration Tests**
   - Test data conversion
   - Test event compatibility
   - Test state preservation
   - Test performance impact

## 13. Documentation Requirements

1. **API Documentation**
   - Endpoint descriptions
   - Event types
   - State management
   - Error handling

2. **Code Documentation**
   - Class documentation
   - Method documentation
   - Type hints
   - Usage examples
