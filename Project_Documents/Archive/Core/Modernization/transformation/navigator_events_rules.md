# Navigator Events Transformation Rules

## Overview
This document defines the transformation rules for converting the legacy NavigatorEventsHandler component to the modern implementation.

## Class Mappings

### Core Classes
```
Legacy (C#)                   Modern (Python)
NavigatorEventsHandler       NavigatorEventsService
CreateSourceEventArgs        NavigatorSourceConfig
FillSourceEventArgs         NavigatorSourceResult
NavigatorRowClickEventArgs  NavigatorRowData
GridAppearanceBase          NavigatorAppearanceConfig
```

### Additional Classes
New classes added in modern implementation:
```python
NavigatorEventContext
NavigatorEventResult
NavigatorSourceType
NavigatorEventHandler
BaseNavigatorEventHandler
```

## Field Transformations

### Basic Fields
1. Event Context:
   ```python
   Legacy                    Modern
   sender                   context.source
   args                     context.metadata
   ```

2. Source Configuration:
   ```python
   Legacy                    Modern
   connection               config.connection
   query                    config.query
   parameters               config.params
   ```

3. Event Results:
   ```python
   Legacy                    Modern
   success                  result.success
   message                  result.message
   data                     result.data
   error                    result.error
   ```

## Method Transformations

### Core Methods
```python
Legacy                          Modern
CreateSource()                 create_source()
FillSource()                   fill_source()
NavigatorRowClick()            handle_row_click()
InitializeAppearance()         initialize_appearance()
```

### New Methods
```python
async def _create_database_source()
async def _create_api_source()
async def _create_file_source()
async def _create_memory_source()
async def _create_custom_source()
```

## Database Schema Changes

### New Tables

1. navigator_events
   ```sql
   CREATE TABLE navigator_events (
       id SERIAL PRIMARY KEY,
       user_id VARCHAR(100) NOT NULL,
       navigator_id VARCHAR(100) NOT NULL,
       session_id VARCHAR(100) NOT NULL,
       event_type VARCHAR(50) NOT NULL,
       event_data JSONB NOT NULL,
       source VARCHAR(100),
       metadata JSONB,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. navigator_sources
   ```sql
   CREATE TABLE navigator_sources (
       id SERIAL PRIMARY KEY,
       user_id VARCHAR(100) NOT NULL,
       navigator_id VARCHAR(100) NOT NULL,
       type VARCHAR(50) NOT NULL,
       config JSONB NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   ```

### Indexes
```sql
CREATE INDEX idx_navigator_events_user ON navigator_events(user_id);
CREATE INDEX idx_navigator_events_navigator ON navigator_events(navigator_id);
CREATE INDEX idx_navigator_events_session ON navigator_events(session_id);
CREATE INDEX idx_navigator_events_type ON navigator_events(event_type);
CREATE INDEX idx_navigator_sources_user ON navigator_sources(user_id);
CREATE INDEX idx_navigator_sources_navigator ON navigator_sources(navigator_id);
CREATE INDEX idx_navigator_sources_type ON navigator_sources(type);
```

## API Transformations

### Endpoints
1. Source:
   - POST /api/v1/navigator/events/source/create
   - POST /api/v1/navigator/events/source/fill
   - Request: NavigatorEventContext, NavigatorSourceConfig
   - Response: NavigatorSourceResult[T]

2. Row:
   - POST /api/v1/navigator/events/row/click
   - Request: NavigatorEventContext, NavigatorRowData
   - Response: NavigatorEventResult

3. Appearance:
   - POST /api/v1/navigator/events/appearance/initialize
   - Request: NavigatorEventContext, NavigatorAppearanceConfig
   - Response: NavigatorEventResult

## Validation Rules

1. Event Context:
   ```python
   - User ID required
   - Session ID required
   - Navigator ID required
   - Valid timestamp
   ```

2. Source Config:
   ```python
   - Valid source type
   - Connection details if required
   - Query validation
   - Parameter validation
   ```

## Security Rules

1. Access Control:
   ```python
   - Require authentication
   - Validate user permissions
   - Check source access
   - Log all events
   ```

2. Data Protection:
   ```python
   - Validate input
   - Sanitize output
   - Rate limit requests
   - Prevent SQL injection
   ```

## Migration Steps

1. Data Migration:
   ```sql
   -- Create events from legacy data
   INSERT INTO navigator_events (
       user_id,
       navigator_id,
       session_id,
       event_type,
       event_data,
       source,
       metadata
   )
   SELECT 
       user_id,
       navigator_id,
       session_id,
       event_type,
       event_data,
       source,
       metadata
   FROM legacy_events;

   -- Create sources from legacy data
   INSERT INTO navigator_sources (
       user_id,
       navigator_id,
       type,
       config
   )
   SELECT 
       user_id,
       navigator_id,
       source_type,
       source_config
   FROM legacy_sources;
   ```

2. Code Updates:
   - Replace event handlers
   - Update event processing
   - Migrate source handling
   - Update dependencies

3. Testing:
   - Unit tests for handlers
   - Integration tests for API
   - Event processing tests
   - Source handling tests

## Rollback Plan

1. Database:
   ```sql
   -- Revert to legacy tables
   DROP TABLE navigator_events;
   DROP TABLE navigator_sources;
   ```

2. Code:
   - Restore event handlers
   - Remove new components
   - Update references
   - Revert API changes

## Monitoring

1. Metrics:
   - Event processing time
   - Source creation time
   - Error rates
   - Cache hit rates

2. Alerts:
   - Failed events
   - Slow processing
   - High error rates
   - Cache misses
