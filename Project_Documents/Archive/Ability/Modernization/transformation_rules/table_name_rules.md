# Table Name Transformation Rules

## 1. Class Transformation

### Legacy to Modern Mapping
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
TableName                     TableName, TableCategory
└── Class                     └── Enums
    └── String constants         └── Categorized constants
    └── Dictionary storage       └── Registry pattern

                             TableMetadata
                             └── Pydantic Model
                                 └── Enhanced metadata

                             TableRegistry
                             └── Static registry
                                 └── Metadata storage
```

## 2. Property Transformations

### Table Properties
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
TableName:                    TableName:
- String constants           - Enum values
- Static dictionary          - Categorized constants

                            TableMetadata:
                            - name
                            - category
                            - description
                            - schema_version
                            - created_at
                            - updated_at
```

## 3. Supporting Models

### New Models
```
TableCategory (Enum):
- ABILITY
- AUTHORIZATION
- BILLING
- CMN_FORM
- COMPANY
- COMPLIANCE
- CUSTOMER
- DOCTOR
- ELIGIBILITY
- FACILITY
- INSURANCE
- INVENTORY
- INVOICE
- KIT
- LOCATION
- MEDICAL
- ORDER
- PAYMENT
- PERMISSION
- PREDEFINED
- PRICE
- PROVIDER
- PURCHASE
- REPORT
- SERIAL
- SHIPPING
- USER
- VENDOR

TableMetadata (Model):
- Table information
- Schema versioning
- Timestamps
```

## 4. Method Transformations

### Core Methods
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
TableName:                    TableRegistry:
- Normalize()                - normalize()
                            - register()
                            - get()

                            TableNameService:
                            - get_table_metadata()
                            - get_tables_by_category()
                            - normalize_table_name()
                            - update_table_metadata()
                            - get_all_tables()
                            - get_table_categories()
```

## 5. Integration Points

### API Integration
```
Legacy (C#)                     Modern (Python)
--------------------------------------------------
Direct Usage:                FastAPI Endpoints:
- String constants          - /tables/{table_name}
- Normalize method         - /tables/category/{category}
                          - /tables/normalize/{table_name}
                          - /tables/{table_name}
                          - /tables
                          - /tables/categories
```

## 6. Code Migration Steps

1. **Model Creation**
   ```python
   # 1. Create enums
   class TableCategory(str, Enum):
       ABILITY = "ability"
       # ...

   class TableName(str, Enum):
       ABILITY_ELIGIBILITY_PAYER = "tbl_ability_eligibility_payer"
       # ...

   # 2. Create metadata model
   class TableMetadata(BaseModel):
       name: TableName
       category: TableCategory
       # ...
   ```

2. **Service Implementation**
   ```python
   # 1. Create table name service
   class TableNameService(BaseService):
       async def get_table_metadata(
           self,
           table_name: TableName
       ) -> TableMetadata:
           # ...
   ```

3. **API Implementation**
   ```python
   # 1. Create table name endpoints
   @router.get("/tables/{table_name}")
   async def get_table_metadata(
       table_name: TableName,
       current_user: User = Depends(get_current_user)
   ) -> TableMetadata:
       # ...
   ```

## 7. Table Categories

1. **Business Categories**
   - Ability
   - Authorization
   - Billing
   - CMN Form
   - Company
   - Compliance
   - Customer
   - Doctor

2. **System Categories**
   - User
   - Permission
   - Variable
   - Object

3. **Transaction Categories**
   - Invoice
   - Order
   - Payment
   - Purchase
   - Serial

## 8. State Management

1. **Table State**
   - Name
   - Category
   - Description
   - Schema version
   - Timestamps

2. **Registry State**
   - Table metadata
   - Category mapping
   - Normalization rules

## 9. Performance Considerations

1. **Table Registry**
   - Static initialization
   - Memory usage
   - Lookup performance
   - Cache invalidation

2. **Normalization**
   - String comparison
   - Case sensitivity
   - Validation rules

## 10. Security Considerations

1. **Input Validation**
   - Table name validation
   - Category validation
   - Schema version validation
   - Description sanitization

2. **Access Control**
   - Authentication
   - Authorization
   - Audit logging
   - Rate limiting

## 11. Testing Strategy

1. **Unit Tests**
   - Enum tests
   - Model tests
   - Service tests
   - Registry tests

2. **Integration Tests**
   - API tests
   - Service tests
   - Registry tests
   - Security tests

## 12. Documentation Requirements

1. **Code Documentation**
   - Class documentation
   - Method documentation
   - Type hints
   - Usage examples

2. **API Documentation**
   - Endpoint documentation
   - Parameter schemas
   - Error codes
   - Authentication
