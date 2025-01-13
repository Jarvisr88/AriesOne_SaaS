# Form System Transformation Rules

## Form Definition Transformation

### Legacy to Modern Mapping
1. Form Structure:
   ```
   Legacy (FormTemplate)              Modern (FormDefinition)
   ------------------------           ----------------------
   TemplateID -> id
   Name -> name
   Description -> description
   Fields -> schema
   ValidationRules -> validation_rules
   Version -> version
   IsPublished -> is_published
   ```

2. Field Definition:
   ```
   Legacy (FormField)                 Modern (Schema Field)
   ------------------------           ----------------------
   FieldID                           field_name
   FieldType -> data_type
   Label -> label
   Required -> required
   DefaultValue -> default
   Options -> enum_values
   ```

### Validation Rules Transformation
1. Field Types:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   Text -> string
   Number -> integer/decimal
   Date -> date
   DateTime -> datetime
   Boolean -> boolean
   List -> array
   Object -> object
   ```

2. Validation Rules:
   ```json
   {
     "required": true,
     "min_length": 3,
     "max_length": 50,
     "pattern": "^[A-Za-z]+$",
     "minimum": 0,
     "maximum": 100,
     "enum": ["value1", "value2"]
   }
   ```

## Form State Transformation

### State Management
1. Form State:
   ```
   Legacy (FormData)                  Modern (FormState)
   ------------------------           ----------------------
   DataID -> id
   TemplateID -> form_definition_id
   EntityID -> entity_id
   FieldValues -> data
   Status -> status
   ```

2. State History:
   ```
   Legacy (FormHistory)               Modern (AuditLog)
   ------------------------           ----------------------
   HistoryID -> id
   DataID -> entity_id
   FieldName -> field_name
   OldValue -> old_value
   NewValue -> new_value
   ChangedBy -> user_id
   ChangedDate -> timestamp
   ```

### Validation Process
1. Validation Steps:
   ```
   1. Type validation
   2. Required fields
   3. Length/range constraints
   4. Pattern matching
   5. Custom validation rules
   6. Cross-field validation
   ```

2. Error Format:
   ```json
   {
     "field": "field_name",
     "error_type": "validation_type",
     "error_message": "Error description",
     "severity": "error/warning"
   }
   ```

## Form Rendering Rules

### UI Components
1. Field Types to Components:
   ```
   string -> TextInput/TextArea
   integer/decimal -> NumberInput
   date -> DatePicker
   datetime -> DateTimePicker
   boolean -> Checkbox/Switch
   array -> MultiSelect/Checkboxes
   object -> FieldGroup
   ```

2. Layout Rules:
   ```
   1. Group related fields
   2. Required fields first
   3. Logical tab order
   4. Responsive grid layout
   5. Consistent spacing
   ```

### Interaction Rules
1. Real-time Validation:
   - Validate on blur
   - Show inline errors
   - Highlight invalid fields

2. State Management:
   - Auto-save on change
   - Track dirty state
   - Confirmation on exit with changes
