# Entity Event Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
CreateSourceEventArgs         CreateSourceEvent
└── EventArgs                └── EntityEvent[GridSource]
    └── IGridSource             └── Enhanced metadata

EntityCreatedEventArgs       EntityCreatedEvent
└── EventArgs                └── EntityEvent[T]
    └── ID property            └── Generic payload

IEntityCreatedEventListener  EntityEventService
└── Interface                └── Service class
    └── Event handling         └── Event pub/sub
```

## 2. Property Transformations

### Event Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
CreateSourceEventArgs:        CreateSourceEvent:
- Source                     - metadata
                            - entity_type
                            - entity_id
                            - payload (GridSource)

EntityCreatedEventArgs:      EntityCreatedEvent:
- ID                        - metadata
                           - entity_type
                           - entity_id
                           - payload (Generic[T])
```

## 3. Supporting Models

### New Models
```
EventType (Enum):
- CREATED
- UPDATED
- DELETED
- SOURCE_CREATED
- SOURCE_UPDATED
- SOURCE_DELETED

EventStatus (Enum):
- PENDING
- PROCESSING
- COMPLETED
- FAILED

EventMetadata (Model):
- event_id
- event_type
- status
- timestamp
- source
- correlation_id
- causation_id
- metadata

GridSourceType (Enum):
- DATABASE
- FILE
- API
- MEMORY
- CUSTOM

GridSourceConfig (Model):
- source_type
- connection_string
- query
- parameters
- metadata

GridSource (Model):
- id
- name
- config
- created_at
- updated_at
- metadata
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
IEntityCreatedEventListener: EntityEventService:
- Handle()                   - publish_event()
- Unhook event              - subscribe()
                           - unsubscribe()
                           - create_entity_event()
                           - create_source_event()
                           - get_event()
                           - get_events_by_type()
                           - get_events_by_entity()
```

## 5. Integration Points

### API Integration
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Event Handling:              FastAPI Endpoints:
- Direct event handling     - /events/entity
                           - /events/source
                           - /events/{event_id}
                           - /events/type/{event_type}
                           - /events/entity/{type}/{id}
```

## 6. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create event models
   class EntityEvent(BaseModel, Generic[T]):
       metadata: EventMetadata
       entity_type: str
       entity_id: Optional[EntityID] = None
       payload: Optional[T] = None

   # 2. Create source models
   class GridSource(BaseModel):
       id: UUID
       name: str
       config: GridSourceConfig
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create event service
   class EntityEventService(BaseService, Generic[T]):
       async def publish_event(
           self,
           event: EntityEvent[T]
       ):
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create event endpoints
   @router.post("/events/entity")
   async def create_entity_event(
       entity_type: str,
       entity_id: Union[int, str, UUID],
       # ...
   ) -> EntityCreatedEvent:
       # ...
   ```

## 7. Event Types

1. **Entity Events**
   - Created
   - Updated
   - Deleted

2. **Source Events**
   - Created
   - Updated
   - Deleted

## 8. Event Metadata

1. **Core Metadata**
   - Event ID
   - Event type
   - Status
   - Timestamp
   - Source

2. **Tracing Metadata**
   - Correlation ID
   - Causation ID
   - Custom metadata

## 9. Performance Considerations

1. **Event Storage**
   - In-memory storage
   - Event persistence
   - Event retrieval
   - Event cleanup

2. **Event Processing**
   - Async processing
   - Handler execution
   - Error handling
   - Retry logic

## 10. Security Considerations

1. **Event Access**
   - Authentication
   - Authorization
   - Event visibility
   - Data protection

2. **Event Validation**
   - Payload validation
   - Schema validation
   - Type checking
   - Input sanitization

## 11. Testing Strategy

1. **Unit Tests**
   - Event creation
   - Event processing
   - Handler execution
   - Error handling

2. **Integration Tests**
   - API endpoints
   - Event flow
   - Handler integration
   - Security tests

## 12. Documentation Requirements

1. **Code Documentation**
   - Class documentation
   - Method documentation
   - Type hints
   - Usage examples

2. **API Documentation**
   - Endpoint documentation
   - Event schemas
   - Error codes
   - Authentication
