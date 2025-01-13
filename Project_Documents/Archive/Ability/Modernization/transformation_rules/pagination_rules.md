# Pagination Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
PagedFilter                   PaginationFilter
└── Class                     └── Pydantic Model
    └── Properties               └── Fields

PagedFillSourceEventArgs      PaginatedSourceEvent
└── Class                     └── Pydantic Model
    └── Properties               └── Fields

PagedNavigator               PaginationService
└── UserControl             └── Service class
    └── Events                └── Event handlers
    └── Grid control          └── Grid state

PagedNavigatorOptions        PaginatedNavigatorOptions
└── Class                    └── Pydantic Model
    └── Properties              └── Fields
```

## 2. Property Transformations

### Filter Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
PagedFilter:                  PaginationFilter:
- Filter                      - filter_text
- Start                       - start
- Count                       - count
                             - sort_field
                             - sort_order
                             - metadata

PagedNavigatorOptions:        PaginatedNavigatorOptions:
- Caption                     - caption
- Switchable                 - switchable
                            - page_size
                            - enable_infinite_scroll
                            - enable_manual_pagination
                            - metadata
```

## 3. Supporting Models

### New Models
```
SortOrder (Enum):
- ASC
- DESC

PageInfo (Model):
- total_count
- page_size
- current_page
- total_pages
- has_next
- has_previous
- metadata

PaginatedData[T] (Model):
- items
- page_info
- filter
- metadata
- timestamp

PaginatedNavigatorState (Model):
- filter
- options
- is_loading
- is_loading_more
- error
- metadata
- timestamp
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
PagedNavigator:               PaginationService:
- CreateSource event         - create_navigator()
- FillSource event          - get_navigator_state()
- NavigatorRowClick event   - set_filter()
                            - load_more()
                            - add_source_handler()
```

## 5. Integration Points

### API Integration
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
PagedNavigator UI Control:    FastAPI Endpoints:
- User interaction           - /paginated-navigators
                            - /paginated-navigators/{id}
                            - /paginated-navigators/{id}/filter
                            - /paginated-navigators/{id}/load-more
```

## 6. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create pagination filter model
   class PaginationFilter(BaseModel):
       filter_text: Optional[str] = None
       start: int = 0
       count: int = 100
       # ...

   # 2. Create navigator options model
   class PaginatedNavigatorOptions(BaseModel):
       caption: str = "Search"
       switchable: bool = True
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create pagination service
   class PaginationService(BaseService, Generic[T]):
       async def create_navigator(
           self,
           options: PaginatedNavigatorOptions
       ) -> str:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create pagination endpoints
   @router.post("/paginated-navigators")
   async def create_paginated_navigator(
       options: PaginatedNavigatorOptions,
       current_user: User = Depends(get_current_user)
   ) -> str:
       # ...
   ```

## 7. Event Handling

1. **Event Types**
   - Source event
   - Filter event
   - Load more event

2. **Event Flow**
   ```
   User Action -> API Endpoint -> Service -> Event Handlers -> State Update
   ```

## 8. State Management

1. **Navigator State**
   - Filter state
   - Loading state
   - Error state
   - Metadata

2. **Page State**
   - Total count
   - Page size
   - Current page
   - Navigation info

## 9. Performance Considerations

1. **Data Loading**
   - Lazy loading
   - Infinite scroll
   - Manual pagination
   - Caching

2. **State Updates**
   - Efficient updates
   - Background loading
   - Error handling
   - Progress tracking

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
