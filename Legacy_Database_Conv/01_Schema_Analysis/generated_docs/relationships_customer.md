```mermaid
erDiagram
    %% CUSTOMER Domain
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
```