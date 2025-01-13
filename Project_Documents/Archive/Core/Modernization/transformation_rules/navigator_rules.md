# Navigator System Transformation Rules

## Grid Definition Transformation

### Legacy to Modern Mapping
1. Grid Structure:
   ```
   Legacy (GridTemplate)              Modern (GridDefinition)
   ------------------------           ----------------------
   TemplateID -> id
   Name -> name
   Description -> description
   Columns -> columns
   DefaultSort -> default_sort
   DefaultFilter -> default_filter
   ```

2. Column Definition:
   ```
   Legacy (GridColumn)                Modern (Column)
   ------------------------           ----------------------
   ColumnID -> field
   Header -> label
   DataType -> data_type
   Width -> width
   Sortable -> sortable
   Filterable -> filterable
   Format -> format
   ```

### Data Type Mapping
1. Column Types:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   Text -> string
   Number -> integer/decimal
   Currency -> decimal
   Date -> date
   DateTime -> datetime
   Boolean -> boolean
   Custom -> component
   ```

2. Format Specifications:
   ```json
   {
     "string": { "case": "upper/lower/title" },
     "decimal": { "precision": 2, "currency": "USD" },
     "date": { "format": "YYYY-MM-DD" },
     "datetime": { "format": "YYYY-MM-DD HH:mm:ss" }
   }
   ```

## Grid State Transformation

### State Management
1. Grid State:
   ```
   Legacy (GridState)                 Modern (GridState)
   ------------------------           ----------------------
   StateID -> id
   TemplateID -> grid_definition_id
   UserID -> user_id
   SortOrder -> sort_order
   Filters -> filters
   PageSize -> page_size
   ```

2. Filter Definition:
   ```
   Legacy (GridFilter)                Modern (FilterCondition)
   ------------------------           ----------------------
   FilterID -> id
   ColumnID -> field
   Operator -> operator
   Value -> value
   IsActive -> is_active
   ```

### Filter Operations
1. Operator Mapping:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   Equals -> eq
   NotEquals -> neq
   GreaterThan -> gt
   GreaterThanEqual -> gte
   LessThan -> lt
   LessThanEqual -> lte
   Contains -> contains
   StartsWith -> startswith
   EndsWith -> endswith
   ```

2. Filter Composition:
   ```json
   {
     "operator": "and/or",
     "conditions": [
       {
         "field": "column_name",
         "operator": "eq",
         "value": "filter_value"
       }
     ]
   }
   ```

## Data Retrieval Rules

### Query Building
1. Base Query:
   ```sql
   SELECT * FROM table_name
   ```

2. Query Modifications:
   ```
   1. Apply filters: WHERE clause
   2. Apply sorting: ORDER BY
   3. Apply pagination: OFFSET/LIMIT
   4. Apply search: LIKE/ILIKE
   ```

### Performance Rules
1. Pagination:
   - Default page size: 50
   - Maximum page size: 200
   - Cache total count

2. Sorting:
   - Maximum sort fields: 3
   - Index frequently sorted columns

3. Filtering:
   - Maximum concurrent filters: 10
   - Index frequently filtered columns

## UI Interaction Rules

### Grid Components
1. Component Mapping:
   ```
   Header -> GridHeader
   Row -> GridRow
   Cell -> GridCell
   Filter -> FilterPanel
   Pagination -> PaginationControls
   ```

2. Interaction Rules:
   ```
   1. Click column header to sort
   2. Right-click for context menu
   3. Double-click row for details
   4. Drag columns to reorder
   5. Resize columns from header
   ```

### State Persistence
1. Save State:
   - On column reorder
   - On resize
   - On sort change
   - On filter change
   - On page size change

2. Load State:
   - On grid initialization
   - On user switch
   - On view switch
