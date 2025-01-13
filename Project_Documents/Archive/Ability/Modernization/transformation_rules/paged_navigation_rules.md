# Paged Navigation System Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
PagedNavigator               PagedNavigationService
└── Navigator                └── NavigationService
    └── UserControl              └── Paging support

PagedNavigatorOptions        NavigatorOptions
└── NavigatorOptions        └── Enhanced options
    └── Basic options          └── Page size config

PagedFillSourceEventArgs     NavigatorEvent
└── FillSourceEventArgs     └── Event model
    └── Event args             └── Page metadata
```

## 2. Property Transformations

### Navigator Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
PagedNavigator:              NavigatorData:
- PageSize                  - metadata.options.page_size
- queue                    - metadata.state
- grid                    - data
```

## 3. Supporting Models

### Enhanced Models
```
NavigatorOptions (Extended):
- page_size: int
- enable_paging: bool

NavigatorData (Extended):
- page: int
- page_count: int
- total_rows: int
- filtered_rows: int

NavigatorEvent (Extended):
- page: int
- page_count: int
- total_rows: int
- filtered_rows: int
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
PagedNavigator:              PagedNavigationService:
- FillSource()             - create_navigator()
- btnMore_Click()         - load_page()
- worker_DoWork()         - clear_data()
- worker_RunWorkerCompleted() - update_filter()
                          - update_sort()
```

## 5. Integration Points

### API Integration
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Paged Operations:           FastAPI Endpoints:
- Direct method calls      - POST /paged-navigators
                          - GET /paged-navigators/{id}
                          - PUT /paged-navigators/{id}/page
                          - PUT /paged-navigators/{id}/filter
                          - PUT /paged-navigators/{id}/sort
                          - POST /paged-navigators/{id}/clear
                          - POST /paged-navigators/{id}/row-click
                          - DELETE /paged-navigators/{id}
```

## 6. Code Migration Steps

1. **Service Extension**
   ```python
   # 1. Extend navigation service
   class PagedNavigationService(NavigationService):
       DEFAULT_PAGE_SIZE = 100
       
       async def create_navigator(
           self,
           table_names: Optional[Set[str]] = None,
           options: Optional[NavigatorOptions] = None,
           metadata: Optional[Dict[str, Any]] = None,
           page_size: int = DEFAULT_PAGE_SIZE
       ) -> NavigatorData:
           # ...
   ```

2. **Page Loading**
   ```python
   # 1. Load page data
   async def load_page(
       self,
       navigator_id: UUID,
       page: int,
       data: List[Dict[str, Any]],
       total_rows: int,
       filtered_rows: Optional[int] = None
   ) -> NavigatorData:
       # ...
   ```

## 7. Paging Strategy

1. **Page Management**
   - Fixed page size
   - Page tracking
   - Total rows tracking
   - Filtered rows tracking

2. **Data Loading**
   - Incremental loading
   - Page caching
   - Clear on filter/sort
   - Memory management

## 8. Event Types

1. **Paging Events**
   - navigator_page_loaded
   - navigator_cleared

2. **Event Data**
   - Page number
   - Page count
   - Total rows
   - Filtered rows

## 9. Performance Considerations

1. **Memory Management**
   - Page data caching
   - Clear old pages
   - Memory limits
   - Data cleanup

2. **Loading Strategy**
   - Async loading
   - Background processing
   - Progress tracking
   - Error handling

## 10. Security Considerations

1. **Data Access**
   - Page permissions
   - Data visibility
   - Row-level security
   - Column-level security

2. **Input Validation**
   - Page size limits
   - Page number validation
   - Data validation
   - Filter validation

## 11. Testing Strategy

1. **Unit Tests**
   - Page loading
   - Data clearing
   - Filter/sort
   - Event handling

2. **Integration Tests**
   - API endpoints
   - Paging flow
   - Memory usage
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
