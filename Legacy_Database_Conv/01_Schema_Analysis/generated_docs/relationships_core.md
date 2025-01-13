```mermaid
erDiagram
    %% CORE Domain
    tbl_cmnform {
        PK INT(11) ID
        ENUM(DMERC 01.02A, DMERC 01.02B, DMERC 02.03A, DMERC 02.03B, DMERC 03.02, DMERC 04.03B, DMERC 04.03C, DMERC 06.02B, DMERC 07.02A, DMERC 07.02B, DMERC 08.02, DMERC 09.02, DMERC 10.02A, DMERC 10.02B, DMERC 484.2, DMERC DRORDER, DMERC URO, DME 04.04B, DME 04.04C, DME 06.03B, DME 07.03A, DME 09.03, DME 10.03, DME 484.03) CMNType
        DATE InitialDate
        DATE RevisedDate
        DATE RecertificationDate
        INT(11) POSTypeID
        VARCHAR(50) AnsweringName
        VARCHAR(50) Signature_Name
        DATE Signature_Date
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
    }
    tbl_customer {
        PK INT(11) ID
        INT(11) BillingTypeID
        CHAR(2) CustomerClassCode
        INT(11) CustomerTypeID
        DATE DeceasedDate
        DATE DateofBirth
        VARCHAR(25) FirstName
        VARCHAR(30) LastName
        CHAR(1) MiddleName
        TINYINT(1) BillActive
        VARCHAR(50) BillName
        ENUM(Unknown, Full Time, Part Time, Retired, Student, Unemployed) EmploymentStatus
        ENUM(Unknown, Single, Married, Legaly Separated, Divorced, Widowed) MaritalStatus
        ENUM(N/A, Active, Reserve, Retired) MilitaryStatus
        TINYINT(1) ShipActive
        VARCHAR(50) ShipName
        ENUM(N/A, Full Time, Part Time) StudentStatus
        CHAR(1) SignatureType
        ENUM(Auto, No, Other) AccidentType
        DATE DateOfInjury
        DATE FirstConsultDate
        INT(11) POSTypeID
        DATE ReturnToWorkDate
        DATE SetupDate
        DATE InactiveDate
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
    }
    tbl_order {
        PK INT(11) ID
        DATE OrderDate
        DATE DeliveryDate
        DATE BillDate
        DATE EndDate
        INT(11) POSTypeID
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
        ENUM(Retail, Back Office) SaleType
    }
    tbl_inventory {
        PK INT(11) WarehouseID
        PK INT(11) InventoryItemID
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
    }
    tbl_invoice {
        PK INT(11) ID
        FK INT(11) CustomerID
        FK INT(11) OrderID
        DATE InvoiceDate
        DATE SubmittedDate
        INT(11) POSTypeID
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
    }
    tbl_invoice ||--o{ tbl_order : references
```