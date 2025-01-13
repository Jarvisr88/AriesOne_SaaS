# Table Analysis: tbl_customer

## Table Information
- **Table Name**: tbl_customer
- **Database**: c01
- **Engine**: InnoDB
- **Character Set**: latin1
- **Collation**: latin1_general_ci

## Column Details

| Column Name | Data Type | Nullable | Default | Description |
|-------------|-----------|----------|---------|-------------|
| AccountNumber | VARCHAR(40) | NO | '' | Customer account identifier |
| Address1 | VARCHAR(40) | NO | '' | Primary address line |
| Address2 | VARCHAR(40) | NO | '' | Secondary address line |
| BillingTypeID | INT(11) | YES | NULL | Reference to tbl_billingtype |
| City | VARCHAR(25) | NO | '' | City name |
| ICD9_01 | VARCHAR(8) | YES | NULL | ICD-9 diagnosis code 1 |
| ICD9_02 | VARCHAR(8) | YES | NULL | ICD-9 diagnosis code 2 |
| ICD9_03 | VARCHAR(8) | YES | NULL | ICD-9 diagnosis code 3 |
| ICD9_04 | VARCHAR(8) | YES | NULL | ICD-9 diagnosis code 4 |
| ICD9_05 | VARCHAR(8) | YES | NULL | ICD-9 diagnosis code 5 |
| ICD9_06 | VARCHAR(8) | YES | NULL | ICD-9 diagnosis code 6 |
| ICD10_01 | VARCHAR(8) | YES | NULL | ICD-10 diagnosis code 1 |
| ICD10_02 | VARCHAR(8) | YES | NULL | ICD-10 diagnosis code 2 |
| ICD10_03 | VARCHAR(8) | YES | NULL | ICD-10 diagnosis code 3 |
| ICD10_04 | VARCHAR(8) | YES | NULL | ICD-10 diagnosis code 4 |
| ICD10_05 | VARCHAR(8) | YES | NULL | ICD-10 diagnosis code 5 |
| ICD10_06 | VARCHAR(8) | YES | NULL | ICD-10 diagnosis code 6 |

## Primary Key
- Single column: ID (AUTO_INCREMENT)

## Foreign Keys
1. BillingTypeID -> tbl_billingtype(ID)

## Indexes
1. Primary Key: ID
2. AccountNumber (for lookups)
3. BillingTypeID (for joins)

## Data Characteristics
1. **Patient Information**
   - Basic demographic data
   - Contact information
   - Address details

2. **Medical Coding**
   - Supports both ICD-9 and ICD-10
   - Up to 6 diagnosis codes each
   - Nullable diagnosis fields

3. **Billing Information**
   - Billing type reference
   - Account number tracking

## Relationships
1. **Parent Tables**
   - tbl_billingtype (BillingTypeID)

2. **Child Tables**
   - tbl_order (CustomerID)
   - tbl_orderdetails (CustomerID)
   - tbl_invoicedetails (CustomerID)

## Technical Considerations

### Data Integrity
1. **Required Fields**
   - AccountNumber
   - Address1
   - City
   - Name fields
   - Contact information

2. **Optional Fields**
   - Address2
   - All ICD codes
   - BillingTypeID

### Performance Considerations
1. **Indexing Strategy**
   - Primary key for unique identification
   - AccountNumber for lookups
   - BillingTypeID for joins

2. **Data Volume**
   - Row length: Variable
   - Key fields: Moderate size
   - Text fields: Limited length

### Migration Notes
1. **Data Type Mapping**
   - VARCHAR fields map directly to PostgreSQL
   - INT(11) maps to INTEGER in PostgreSQL
   - TIMESTAMP handling needs review

2. **Constraints**
   - Foreign key relationships must be maintained
   - NOT NULL constraints must be preserved
   - Default values must be mapped

3. **Special Handling**
   - ICD code validation
   - Address formatting
   - Account number format validation
