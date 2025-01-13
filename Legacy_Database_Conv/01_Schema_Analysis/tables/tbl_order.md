# Table Analysis: tbl_order

## Table Information
- **Table Name**: tbl_order
- **Database**: c01
- **Engine**: InnoDB
- **Character Set**: latin1
- **Collation**: latin1_general_ci

## Column Details

| Column Name | Data Type | Nullable | Default | Description |
|-------------|-----------|----------|---------|-------------|
| ID | INT(11) | NO | AUTO_INCREMENT | Primary key |
| CustomerID | INT(11) | NO | 0 | Reference to tbl_customer |
| Approved | TINYINT(1) | NO | 0 | Order approval flag |
| RetailSales | TINYINT(1) | NO | 0 | Retail sales indicator |
| OrderDate | DATE | YES | NULL | Date order was placed |
| DeliveryDate | DATE | YES | NULL | Date of delivery |
| PickupDate | DATE | YES | NULL | Date of pickup |
| Status | VARCHAR(50) | NO | '' | Order status |
| OrderNumber | VARCHAR(50) | NO | '' | Order reference number |
| PONumber | VARCHAR(50) | NO | '' | Purchase order number |
| ReferralTypeID | INT(11) | YES | NULL | Reference to tbl_referraltype |
| DoctorID | INT(11) | YES | NULL | Reference to tbl_doctor |
| LocationID | INT(11) | YES | NULL | Reference to tbl_location |
| LastUpdateUserID | SMALLINT(6) | YES | NULL | Last update user |
| LastUpdateDatetime | TIMESTAMP | NO | CURRENT_TIMESTAMP | Last update timestamp |

## Primary Key
- Single column: ID (AUTO_INCREMENT)

## Foreign Keys
1. CustomerID -> tbl_customer(ID)
2. ReferralTypeID -> tbl_referraltype(ID)
3. DoctorID -> tbl_doctor(ID)
4. LocationID -> tbl_location(ID)

## Indexes
1. Primary Key: ID
2. CustomerID (for joins)
3. OrderNumber (for lookups)
4. ReferralTypeID, DoctorID, LocationID (for joins)

## Data Characteristics

1. **Order Tracking**
   - Unique order number
   - Multiple status tracking
   - Approval tracking
   - Retail vs. non-retail distinction

2. **Timeline Information**
   - Order date
   - Delivery date
   - Pickup date
   - Last update tracking

3. **References**
   - Customer link
   - Doctor reference
   - Location tracking
   - Referral type

## Relationships

1. **Parent Tables**
   - tbl_customer (CustomerID)
   - tbl_referraltype (ReferralTypeID)
   - tbl_doctor (DoctorID)
   - tbl_location (LocationID)

2. **Child Tables**
   - tbl_orderdetails (OrderID)
   - tbl_invoicedetails (OrderID)

## Technical Considerations

### Data Integrity
1. **Required Fields**
   - CustomerID
   - OrderNumber
   - Status
   - LastUpdateDatetime

2. **Optional Fields**
   - ReferralTypeID
   - DoctorID
   - LocationID
   - Dates (except LastUpdateDatetime)

### Performance Considerations
1. **Indexing Strategy**
   - Primary key for unique identification
   - Foreign keys for joins
   - OrderNumber for lookups

2. **Data Volume**
   - Row length: Fixed + Variable text
   - Key fields: Moderate size
   - Date fields: Fixed length

### Migration Notes
1. **Data Type Mapping**
   - INT(11) maps to INTEGER in PostgreSQL
   - TINYINT(1) maps to BOOLEAN in PostgreSQL
   - DATE fields map directly
   - TIMESTAMP handling needs review

2. **Constraints**
   - Foreign key relationships must be maintained
   - NOT NULL constraints must be preserved
   - Default values must be mapped

3. **Special Handling**
   - Order number format validation
   - Status value validation
   - Date range validation
   - Boolean field mapping
