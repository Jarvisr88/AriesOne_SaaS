# Table Analysis: tbl_orderdetails

## Table Information
- **Table Name**: tbl_orderdetails
- **Database**: c01
- **Engine**: InnoDB
- **Character Set**: latin1
- **Collation**: latin1_general_ci

## Column Details

| Column Name | Data Type | Nullable | Default | Description |
|-------------|-----------|----------|---------|-------------|
| ID | INT(11) | NO | AUTO_INCREMENT | Primary key |
| OrderID | INT(11) | NO | 0 | Reference to tbl_order |
| CustomerID | INT(11) | NO | 0 | Reference to tbl_customer |
| SerialNumber | VARCHAR(50) | YES | NULL | Equipment serial number |
| InventoryItemID | INT(11) | NO | 0 | Reference to tbl_inventoryitem |
| PriceCodeID | INT(11) | YES | NULL | Reference to price codes |
| SaleRentType | VARCHAR(50) | NO | '' | Sale or rental indicator |
| SerialID | INT(11) | YES | NULL | Reference to serial tracking |
| BillablePrice | DECIMAL(18,2) | NO | 0.00 | Price to bill |
| AllowablePrice | DECIMAL(18,2) | NO | 0.00 | Allowable amount |
| Taxable | TINYINT(1) | NO | 0 | Tax applicability |
| FlatRate | TINYINT(1) | NO | 0 | Flat rate indicator |
| DOSFrom | DATE | YES | NULL | Service start date |
| DOSTo | DATE | YES | NULL | Service end date |
| PickupDate | DATE | YES | NULL | Equipment pickup date |
| ShowSpanDates | TINYINT(1) | NO | 0 | Date span display flag |
| OrderedQuantity | INT(11) | NO | 0 | Quantity ordered |
| OrderedUnits | VARCHAR(50) | NO | '' | Units of measure |
| OrderedWhen | VARCHAR(50) | NO | '' | Order frequency |
| OrderedConverter | DOUBLE | NO | 0 | Unit conversion factor |
| BilledQuantity | INT(11) | NO | 0 | Quantity billed |
| BilledUnits | VARCHAR(50) | NO | '' | Billing units |
| BilledWhen | VARCHAR(50) | NO | '' | Billing frequency |
| BilledConverter | DOUBLE | NO | 0 | Billing conversion factor |
| BillingCode | VARCHAR(50) | NO | '' | HCPCS/billing code |
| Modifier1 | VARCHAR(50) | NO | '' | Billing modifier 1 |
| Modifier2 | VARCHAR(50) | NO | '' | Billing modifier 2 |
| Modifier3 | VARCHAR(50) | NO | '' | Billing modifier 3 |
| Modifier4 | VARCHAR(50) | NO | '' | Billing modifier 4 |
| DXPointer | VARCHAR(50) | NO | '' | Diagnosis pointer |
| BillingMonth | INT(11) | NO | 0 | Billing month counter |
| AuthorizationNumber | VARCHAR(50) | NO | '' | Authorization reference |
| AuthorizationTypeID | INT(11) | YES | NULL | Auth type reference |
| AuthorizationExpirationDate | DATE | YES | NULL | Auth expiration date |

## Primary Key
- Single column: ID (AUTO_INCREMENT)

## Foreign Keys
1. OrderID -> tbl_order(ID)
2. CustomerID -> tbl_customer(ID)
3. InventoryItemID -> tbl_inventoryitem(ID)
4. AuthorizationTypeID -> tbl_authorizationtype(ID)

## Indexes
1. Primary Key: ID
2. IDX_CUSTOMERID_ORDERID_ID (CustomerID, OrderID, ID)
3. IDX_CUSTOMERID_ORDERID_ID_INVENTORYITEMID (CustomerID, OrderID, ID, InventoryItemID)

## Data Characteristics

1. **Order Line Items**
   - Item identification
   - Quantity tracking
   - Serial number tracking
   - Price information

2. **Billing Information**
   - HCPCS codes
   - Modifiers
   - Authorization details
   - Price calculations

3. **Service Dates**
   - Service period tracking
   - Pickup dates
   - Authorization dates

4. **Units and Conversions**
   - Order units
   - Billing units
   - Conversion factors
   - Frequency tracking

## Relationships

1. **Parent Tables**
   - tbl_order (OrderID)
   - tbl_customer (CustomerID)
   - tbl_inventoryitem (InventoryItemID)
   - tbl_authorizationtype (AuthorizationTypeID)

2. **Child Tables**
   - tbl_invoicedetails (references this table)

## Technical Considerations

### Data Integrity
1. **Required Fields**
   - OrderID, CustomerID, InventoryItemID
   - SaleRentType
   - BillingCode
   - Price fields

2. **Optional Fields**
   - SerialNumber
   - PriceCodeID
   - Authorization fields
   - Date fields

### Performance Considerations
1. **Indexing Strategy**
   - Composite indexes for common queries
   - Foreign key indexes
   - Date range queries

2. **Data Volume**
   - High volume table
   - Multiple date fields
   - Text and numeric mix

### Migration Notes
1. **Data Type Mapping**
   - DECIMAL(18,2) maps directly to PostgreSQL
   - DATE fields map directly
   - VARCHAR fields need length validation
   - TINYINT(1) to BOOLEAN conversion

2. **Constraints**
   - Complex foreign key relationships
   - Business rule validation
   - Date range validation

3. **Special Handling**
   - Unit conversion logic
   - Price calculation rules
   - Authorization validation
   - HCPCS code validation
   - Modifier validation
