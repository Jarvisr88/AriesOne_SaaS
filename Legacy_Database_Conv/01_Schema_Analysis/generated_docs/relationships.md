```mermaid
erDiagram
    tbl_ability_eligibility_request {
        ( tbl_ability_eligibility_request
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL CustomerID
        INT(11) NOT NULL CustomerInsuranceID
        DATETIME NOT NULL RequestTime
        MEDIUMTEXT NOT NULL RequestText
        DATETIME NULL DEFAULT NULL ResponseTime
        MEDIUMTEXT NULL DEFAULT NULL ResponseText
        DATETIME NULL DEFAULT NULL SubmissionTime
        MEDIUMTEXT NULL DEFAULT NULL SubmissionText
        -- ----------------------------------------------------- tbl_authorizationtype
    }
    tbl_authorizationtype {
        ( tbl_authorizationtype
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_batchpayment
    }
    tbl_batchpayment {
        ( tbl_batchpayment
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL InsuranceCompanyID
        VARCHAR(14) NOT NULL CheckNumber
        DATE NOT NULL CheckDate
        DECIMAL(18 CheckAmount
        DECIMAL(18 AmountUsed
        SMALLINT(6) NOT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_billingtype
    }
    tbl_billingtype {
        ( tbl_billingtype
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_changes
    }
    tbl_changes {
        ( tbl_changes
        VARCHAR(64) NOT NULL TableName
        INT(11) NOT NULL SessionID
        SMALLINT(6) NOT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_cmnform
    }
    tbl_cmnform {
        ( tbl_cmnform
        INT(11) NOT NULL AUTO_INCREMENT ID
        ENUM('DMERC 01.02A' CMNType
        DATE NULL DEFAULT NULL InitialDate
        DATE NULL DEFAULT NULL RevisedDate
        DATE NULL DEFAULT NULL RecertificationDate
        INT(11) NULL DEFAULT NULL CustomerID
        VARCHAR(8) NULL DEFAULT NULL Customer_ICD9_1
        VARCHAR(8) NULL DEFAULT NULL Customer_ICD9_2
        VARCHAR(8) NULL DEFAULT NULL Customer_ICD9_3
        VARCHAR(8) NULL DEFAULT NULL Customer_ICD9_4
        INT(11) NULL DEFAULT NULL DoctorID
        INT(11) NULL DEFAULT NULL POSTypeID
        INT(11) NULL DEFAULT NULL FacilityID
        VARCHAR(50) NOT NULL DEFAULT '' AnsweringName
        VARCHAR(50) NOT NULL DEFAULT '' AnsweringTitle
        VARCHAR(50) NOT NULL DEFAULT '' AnsweringEmployer
        INT(11) NOT NULL DEFAULT '0' EstimatedLengthOfNeed
        VARCHAR(50) NOT NULL DEFAULT '' Signature_Name
        DATE NULL DEFAULT NULL Signature_Date
        TINYINT(1) NOT NULL DEFAULT '0' OnFile
        INT(11) NULL DEFAULT NULL OrderID
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        SET('CMNType' MIR
        TINYINT(1) NOT NULL DEFAULT '0' Customer_UsingICD10
        -- ----------------------------------------------------- tbl_cmnform_0102a
    }
    tbl_cmnform_0102a {
        ( tbl_cmnform_0102a
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        ENUM('Y' Answer3
        ENUM('Y' Answer4
        ENUM('Y' Answer5
        ENUM('Y' Answer6
        ENUM('Y' Answer7
        -- ----------------------------------------------------- tbl_cmnform_0102b
    }
    tbl_cmnform_0102b {
        ( tbl_cmnform_0102b
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer12
        ENUM('Y' Answer13
        ENUM('Y' Answer14
        ENUM('Y' Answer15
        ENUM('Y' Answer16
        ENUM('Y' Answer19
        ENUM('Y' Answer20
        VARCHAR(30) NULL DEFAULT NULL Answer21_Ulcer1_Stage
        DOUBLE NULL DEFAULT NULL Answer21_Ulcer1_MaxLength
        DOUBLE NULL DEFAULT NULL Answer21_Ulcer1_MaxWidth
        VARCHAR(30) NULL DEFAULT NULL Answer21_Ulcer2_Stage
        DOUBLE NULL DEFAULT NULL Answer21_Ulcer2_MaxLength
        DOUBLE NULL DEFAULT NULL Answer21_Ulcer2_MaxWidth
        VARCHAR(30) NULL DEFAULT NULL Answer21_Ulcer3_Stage
        DOUBLE NULL DEFAULT NULL Answer21_Ulcer3_MaxLength
        DOUBLE NULL DEFAULT NULL Answer21_Ulcer3_MaxWidth
        ENUM('1' Answer22
        -- ----------------------------------------------------- tbl_cmnform_0203a
    }
    tbl_cmnform_0203a {
        ( tbl_cmnform_0203a
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        ENUM('Y' Answer2
        ENUM('Y' Answer3
        ENUM('Y' Answer4
        INT(11) NULL DEFAULT NULL Answer5
        ENUM('Y' Answer6
        ENUM('Y' Answer7
        -- ----------------------------------------------------- tbl_cmnform_0203b
    }
    tbl_cmnform_0203b {
        ( tbl_cmnform_0203b
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        ENUM('Y' Answer2
        ENUM('Y' Answer3
        ENUM('Y' Answer4
        INT(11) NULL DEFAULT NULL Answer5
        ENUM('Y' Answer8
        ENUM('Y' Answer9
        -- ----------------------------------------------------- tbl_cmnform_0302
    }
    tbl_cmnform_0302 {
        ( tbl_cmnform_0302
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        INT(11) NULL DEFAULT NULL Answer12
        ENUM('Y' Answer14
        -- ----------------------------------------------------- tbl_cmnform_0403b
    }
    tbl_cmnform_0403b {
        ( tbl_cmnform_0403b
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        ENUM('Y' Answer2
        ENUM('Y' Answer3
        ENUM('Y' Answer4
        ENUM('Y' Answer5
        -- ----------------------------------------------------- tbl_cmnform_0403c
    }
    tbl_cmnform_0403c {
        ( tbl_cmnform_0403c
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer6a
        INT(11) NOT NULL DEFAULT '0' Answer6b
        ENUM('Y' Answer7a
        INT(11) NOT NULL DEFAULT '0' Answer7b
        ENUM('Y' Answer8
        ENUM('Y' Answer9a
        INT(11) NOT NULL DEFAULT '0' Answer9b
        ENUM('Y' Answer10a
        INT(11) NOT NULL DEFAULT '0' Answer10b
        INT(11) NOT NULL DEFAULT '0' Answer10c
        ENUM('Y' Answer11a
        INT(11) NOT NULL DEFAULT '0' Answer11b
        -- ----------------------------------------------------- tbl_cmnform_0404b
    }
    tbl_cmnform_0404b {
        ( tbl_cmnform_0404b
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        ENUM('Y' Answer2
        ENUM('Y' Answer3
        ENUM('Y' Answer4
        ENUM('Y' Answer5
        -- ----------------------------------------------------- tbl_cmnform_0404c
    }
    tbl_cmnform_0404c {
        ( tbl_cmnform_0404c
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer6
        ENUM('Y' Answer7a
        VARCHAR(10) NULL DEFAULT NULL Answer7b
        ENUM('Y' Answer8
        ENUM('Y' Answer9a
        VARCHAR(10) NULL DEFAULT NULL Answer9b
        ENUM('Y' Answer10a
        VARCHAR(10) NULL DEFAULT NULL Answer10b
        VARCHAR(10) NULL DEFAULT NULL Answer10c
        ENUM('Y' Answer11
        ENUM('Y' Answer12
        -- ----------------------------------------------------- tbl_cmnform_0602b
    }
    tbl_cmnform_0602b {
        ( tbl_cmnform_0602b
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        DATE NULL DEFAULT NULL Answer2
        ENUM('Y' Answer3
        INT(11) NULL DEFAULT NULL Answer4
        ENUM('1' Answer5
        ENUM('Y' Answer6
        ENUM('Y' Answer7
        DATE NULL DEFAULT NULL Answer8_begun
        DATE NULL DEFAULT NULL Answer8_ended
        DATE NULL DEFAULT NULL Answer9
        ENUM('1' Answer10
        ENUM('Y' Answer11
        ENUM('2' Answer12
        -- ----------------------------------------------------- tbl_cmnform_0603b
    }
    tbl_cmnform_0603b {
        ( tbl_cmnform_0603b
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        INT(11) NULL DEFAULT NULL Answer2
        ENUM('1' Answer3
        ENUM('Y' Answer4
        ENUM('Y' Answer5
        DATE NULL DEFAULT NULL Answer6
        -- ----------------------------------------------------- tbl_cmnform_0702a
    }
    tbl_cmnform_0702a {
        ( tbl_cmnform_0702a
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        ENUM('Y' Answer2
        ENUM('Y' Answer3
        ENUM('Y' Answer4
        ENUM('Y' Answer5
        -- ----------------------------------------------------- tbl_cmnform_0702b
    }
    tbl_cmnform_0702b {
        ( tbl_cmnform_0702b
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer6
        ENUM('Y' Answer7
        ENUM('Y' Answer8
        ENUM('Y' Answer12
        ENUM('Y' Answer13
        ENUM('Y' Answer14
        -- ----------------------------------------------------- tbl_cmnform_0703a
    }
    tbl_cmnform_0703a {
        ( tbl_cmnform_0703a
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        ENUM('Y' Answer2
        ENUM('Y' Answer3
        ENUM('Y' Answer4
        ENUM('Y' Answer5
        -- ----------------------------------------------------- tbl_cmnform_0802
    }
    tbl_cmnform_0802 {
        ( tbl_cmnform_0802
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        VARCHAR(5) NOT NULL DEFAULT '' Answer1_HCPCS
        INT(11) NULL DEFAULT NULL Answer1_MG
        INT(11) NULL DEFAULT NULL Answer1_Times
        VARCHAR(5) NOT NULL DEFAULT '' Answer2_HCPCS
        INT(11) NULL DEFAULT NULL Answer2_MG
        INT(11) NULL DEFAULT NULL Answer2_Times
        VARCHAR(5) NOT NULL DEFAULT '' Answer3_HCPCS
        INT(11) NULL DEFAULT NULL Answer3_MG
        INT(11) NULL DEFAULT NULL Answer3_Times
        ENUM('Y' Answer4
        ENUM('1' Answer5_1
        ENUM('1' Answer5_2
        ENUM('1' Answer5_3
        VARCHAR(60) NOT NULL DEFAULT '' Answer8
        VARCHAR(20) NOT NULL DEFAULT '' Answer9
        VARCHAR(2) NOT NULL DEFAULT '' Answer10
        DATE NULL DEFAULT NULL Answer11
        ENUM('Y' Answer12
        -- ----------------------------------------------------- tbl_cmnform_0902
    }
    tbl_cmnform_0902 {
        ( tbl_cmnform_0902
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('1' Answer1
        VARCHAR(50) NOT NULL DEFAULT '' Answer2
        VARCHAR(50) NOT NULL DEFAULT '' Answer3
        ENUM('1' Answer4
        ENUM('1' Answer5
        INT(11) NOT NULL DEFAULT '1' Answer6
        ENUM('Y' Answer7
        -- ----------------------------------------------------- tbl_cmnform_0903
    }
    tbl_cmnform_0903 {
        ( tbl_cmnform_0903
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        VARCHAR(10) NULL DEFAULT NULL Answer1a
        VARCHAR(10) NULL DEFAULT NULL Answer1b
        VARCHAR(10) NULL DEFAULT NULL Answer1c
        VARCHAR(50) NULL DEFAULT NULL Answer2a
        VARCHAR(50) NULL DEFAULT NULL Answer2b
        VARCHAR(50) NULL DEFAULT NULL Answer2c
        ENUM('1' Answer3
        ENUM('1' Answer4
        -- ----------------------------------------------------- tbl_cmnform_1002a
    }
    tbl_cmnform_1002a {
        ( tbl_cmnform_1002a
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        INT(11) NULL DEFAULT NULL Answer3
        DOUBLE NULL DEFAULT NULL Concentration_AminoAcid
        DOUBLE NULL DEFAULT NULL Concentration_Dextrose
        DOUBLE NULL DEFAULT NULL Concentration_Lipids
        DOUBLE NULL DEFAULT NULL Dose_AminoAcid
        DOUBLE NULL DEFAULT NULL Dose_Dextrose
        DOUBLE NULL DEFAULT NULL Dose_Lipids
        DOUBLE NULL DEFAULT NULL DaysPerWeek_Lipids
        DOUBLE NULL DEFAULT NULL GmsPerDay_AminoAcid
        ENUM('1' Answer5
        -- ----------------------------------------------------- tbl_cmnform_1002b
    }
    tbl_cmnform_1002b {
        ( tbl_cmnform_1002b
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer7
        ENUM('Y' Answer8
        VARCHAR(50) NOT NULL DEFAULT '' Answer10a
        VARCHAR(50) NOT NULL DEFAULT '' Answer10b
        VARCHAR(50) NOT NULL DEFAULT '' Answer11a
        VARCHAR(50) NOT NULL DEFAULT '' Answer11b
        INT(11) NULL DEFAULT NULL Answer12
        ENUM('1' Answer13
        ENUM('Y' Answer14
        VARCHAR(50) NOT NULL DEFAULT '' Answer15
        -- ----------------------------------------------------- tbl_cmnform_1003
    }
    tbl_cmnform_1003 {
        ( tbl_cmnform_1003
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        ENUM('Y' Answer1
        ENUM('Y' Answer2
        VARCHAR(10) NULL DEFAULT NULL Answer3a
        VARCHAR(10) NULL DEFAULT NULL Answer3b
        INT(11) NULL DEFAULT NULL Answer4a
        INT(11) NULL DEFAULT NULL Answer4b
        ENUM('1' Answer5
        INT(11) NULL DEFAULT NULL Answer6
        ENUM('Y' Answer7
        INT(11) NULL DEFAULT NULL Answer8a
        INT(11) NULL DEFAULT NULL Answer8b
        INT(11) NULL DEFAULT NULL Answer8c
        INT(11) NULL DEFAULT NULL Answer8d
        INT(11) NULL DEFAULT NULL Answer8e
        INT(11) NULL DEFAULT NULL Answer8f
        INT(11) NULL DEFAULT NULL Answer8g
        INT(11) NULL DEFAULT NULL Answer8h
        ENUM('1' Answer9
        -- ----------------------------------------------------- tbl_cmnform_48403
    }
    tbl_cmnform_48403 {
        ( tbl_cmnform_48403
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        INT(11) NULL DEFAULT NULL Answer1a
        INT(11) NULL DEFAULT NULL Answer1b
        DATE NULL DEFAULT NULL Answer1c
        ENUM('1' Answer2
        ENUM('1' Answer3
        ENUM('Y' Answer4
        VARCHAR(10) NULL DEFAULT NULL Answer5
        INT(11) NULL DEFAULT NULL Answer6a
        INT(11) NULL DEFAULT NULL Answer6b
        DATE NULL DEFAULT NULL Answer6c
        ENUM('Y' Answer7
        ENUM('Y' Answer8
        ENUM('Y' Answer9
        -- ----------------------------------------------------- tbl_cmnform_4842
    }
    tbl_cmnform_4842 {
        ( tbl_cmnform_4842
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        INT(11) NULL DEFAULT NULL Answer1a
        INT(11) NULL DEFAULT NULL Answer1b
        DATE NULL DEFAULT NULL Answer1c
        ENUM('Y' Answer2
        ENUM('1' Answer3
        VARCHAR(50) NOT NULL DEFAULT '' PhysicianAddress
        VARCHAR(50) NOT NULL DEFAULT '' PhysicianCity
        VARCHAR(50) NOT NULL DEFAULT '' PhysicianState
        VARCHAR(50) NOT NULL DEFAULT '' PhysicianZip
        VARCHAR(50) NOT NULL DEFAULT '' PhysicianName
        ENUM('Y' Answer5
        VARCHAR(10) NULL DEFAULT NULL Answer6
        INT(11) NULL DEFAULT NULL Answer7a
        INT(11) NULL DEFAULT NULL Answer7b
        DATE NULL DEFAULT NULL Answer7c
        ENUM('Y' Answer8
        ENUM('Y' Answer9
        ENUM('Y' Answer10
        -- ----------------------------------------------------- tbl_cmnform_details
    }
    tbl_cmnform_details {
        ( tbl_cmnform_details
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        VARCHAR(50) NULL DEFAULT NULL BillingCode
        INT(11) NOT NULL DEFAULT '0' InventoryItemID
        DOUBLE NOT NULL DEFAULT '0' OrderedQuantity
        VARCHAR(50) NULL DEFAULT NULL OrderedUnits
        DOUBLE NOT NULL DEFAULT '0' BillablePrice
        DOUBLE NOT NULL DEFAULT '0' AllowablePrice
        ENUM('One time' Period
        VARCHAR(8) NOT NULL DEFAULT '' Modifier1
        VARCHAR(8) NOT NULL DEFAULT '' Modifier2
        VARCHAR(8) NOT NULL DEFAULT '' Modifier3
        VARCHAR(8) NOT NULL DEFAULT '' Modifier4
        INT(11) NULL DEFAULT NULL PredefinedTextID
        INT(11) NOT NULL AUTO_INCREMENT ID
        -- ----------------------------------------------------- tbl_cmnform_drorder
    }
    tbl_cmnform_drorder {
        ( tbl_cmnform_drorder
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        VARCHAR(50) NOT NULL DEFAULT '' Prognosis
        LONGTEXT NOT NULL MedicalJustification
        -- ----------------------------------------------------- tbl_cmnform_uro
    }
    tbl_cmnform_uro {
        ( tbl_cmnform_uro
        INT(11) NOT NULL DEFAULT '0' CMNFormID
        VARCHAR(50) NOT NULL DEFAULT '' Prognosis
        -- ----------------------------------------------------- tbl_company
    }
    tbl_company {
        ( tbl_company
        VARCHAR(40) NOT NULL DEFAULT '' Address1
        VARCHAR(40) NOT NULL DEFAULT '' Address2
        TINYINT(1) NOT NULL DEFAULT '0' BillCustomerCopayUpfront
        VARCHAR(25) NOT NULL DEFAULT '' City
        VARCHAR(50) NOT NULL DEFAULT '' Fax
        VARCHAR(9) NOT NULL DEFAULT '' FederalTaxID
        VARCHAR(20) NOT NULL DEFAULT '332B00000X' TaxonomyCode
        VARCHAR(20) NOT NULL DEFAULT '' EIN
        VARCHAR(20) NOT NULL DEFAULT '' SSN
        ENUM('SSN' TaxIDType
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        TINYINT(1) NOT NULL DEFAULT '0' ParticipatingProvider
        VARCHAR(50) NOT NULL DEFAULT '' Phone
        VARCHAR(50) NOT NULL DEFAULT '' Phone2
        TINYINT(1) NOT NULL DEFAULT '0' POAuthorizationCodeReqiered
        TINYINT(1) NOT NULL DEFAULT '0' Print_PricesOnOrders
        MEDIUMBLOB NULL DEFAULT NULL Picture
        INT(11) NULL DEFAULT '12' POSTypeID
        CHAR(2) NOT NULL DEFAULT '' State
        TINYINT(1) NOT NULL DEFAULT '0' SystemGenerate_BlanketAssignments
        TINYINT(1) NOT NULL DEFAULT '0' SystemGenerate_CappedRentalLetters
        TINYINT(1) NOT NULL DEFAULT '0' SystemGenerate_CustomerAccountNumbers
        TINYINT(1) NOT NULL DEFAULT '0' SystemGenerate_DeliveryPickupTickets
        TINYINT(1) NOT NULL DEFAULT '0' SystemGenerate_DroctorsOrder
        TINYINT(1) NOT NULL DEFAULT '0' SystemGenerate_HIPPAForms
        TINYINT(1) NOT NULL DEFAULT '0' SystemGenerate_PatientBillOfRights
        TINYINT(1) NOT NULL DEFAULT '0' SystemGenerate_PurchaseOrderNumber
        TINYINT(1) NOT NULL DEFAULT '0' WriteoffDifference
        VARCHAR(10) NOT NULL DEFAULT '' Zip
        TINYINT(1) NOT NULL DEFAULT '0' IncludeLocationInfo
        VARCHAR(50) NOT NULL DEFAULT '' Contact
        TINYINT(1) NOT NULL DEFAULT '0' Print_CompanyInfoOnInvoice
        TINYINT(1) NOT NULL DEFAULT '0' Print_CompanyInfoOnDelivery
        TINYINT(1) NOT NULL DEFAULT '0' Print_CompanyInfoOnPickup
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        TINYINT(1) NOT NULL DEFAULT '0' Show_InactiveCustomers
        INT(11) NULL DEFAULT NULL WarehouseID
        VARCHAR(10) NULL DEFAULT NULL NPI
        INT(11) NULL DEFAULT NULL TaxRateID
        VARCHAR(250) NULL DEFAULT NULL ImagingServer
        VARCHAR(20) NOT NULL DEFAULT '' ZirmedNumber
        TINYINT(1) NOT NULL DEFAULT '1' AutomaticallyReorderInventory
        VARCHAR(50) NOT NULL DEFAULT '' AvailityNumber
        TINYINT(1) NOT NULL DEFAULT '0' Show_QuantityOnHand
        TINYINT(1) NOT NULL DEFAULT '0' Use_Icd10ForNewCmnRx
        INT(11) NULL DEFAULT NULL OrderSurveyID
        MEDIUMTEXT NOT NULL AbilityIntegrationSettings
        -- ----------------------------------------------------- tbl_compliance
    }
    tbl_compliance {
        ( tbl_compliance
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' CustomerID
        INT(11) NULL DEFAULT NULL OrderID
        DATE NOT NULL DEFAULT '0000-00-00' DeliveryDate
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_compliance_items
    }
    tbl_compliance_items {
        ( tbl_compliance_items
        INT(11) NOT NULL DEFAULT '0' ComplianceID
        INT(11) NOT NULL DEFAULT '0') InventoryItemID
        -- ----------------------------------------------------- tbl_compliance_notes
    }
    tbl_compliance_notes {
        ( tbl_compliance_notes
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' ComplianceID
        DATE NOT NULL DEFAULT '0000-00-00' Date
        TINYINT(1) NOT NULL DEFAULT '0' Done
        LONGTEXT NOT NULL Notes
    }
    tbl_customer {
        ( tbl_customer
        VARCHAR(40) NOT NULL DEFAULT '' AccountNumber
        VARCHAR(40) NOT NULL DEFAULT '' Address1
        VARCHAR(40) NOT NULL DEFAULT '' Address2
        INT(11) NULL DEFAULT NULL BillingTypeID
        VARCHAR(25) NOT NULL DEFAULT '' City
        ENUM('Dr.' Courtesy
        DOUBLE NULL DEFAULT NULL CustomerBalance
        CHAR(2) NULL DEFAULT NULL CustomerClassCode
        INT(11) NULL DEFAULT NULL CustomerTypeID
        DATE NULL DEFAULT NULL DeceasedDate
        DATE NULL DEFAULT NULL DateofBirth
        VARCHAR(25) NOT NULL DEFAULT '' FirstName
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(30) NOT NULL DEFAULT '' LastName
        INT(11) NULL DEFAULT NULL LocationID
        CHAR(1) NOT NULL DEFAULT '' MiddleName
        VARCHAR(50) NOT NULL DEFAULT '' Phone
        VARCHAR(50) NOT NULL DEFAULT '' Phone2
        CHAR(2) NOT NULL DEFAULT '' State
        VARCHAR(4) NOT NULL DEFAULT '' Suffix
        DOUBLE NULL DEFAULT NULL TotalBalance
        VARCHAR(10) NOT NULL DEFAULT '' Zip
        TINYINT(1) NOT NULL DEFAULT '0' BillActive
        VARCHAR(40) NOT NULL DEFAULT '' BillAddress1
        VARCHAR(40) NOT NULL DEFAULT '' BillAddress2
        VARCHAR(25) NOT NULL DEFAULT '' BillCity
        VARCHAR(50) NOT NULL DEFAULT '' BillName
        CHAR(2) NOT NULL DEFAULT '' BillState
        VARCHAR(10) NOT NULL DEFAULT '' BillZip
        TINYINT(1) NULL DEFAULT NULL CommercialAccount
        LONGTEXT NOT NULL DeliveryDirections
        ENUM('Unknown' EmploymentStatus
        ENUM('Male' Gender
        DOUBLE NULL DEFAULT NULL Height
        VARCHAR(50) NOT NULL DEFAULT '' License
        ENUM('Unknown' MaritalStatus
        ENUM('N/A' MilitaryBranch
        ENUM('N/A' MilitaryStatus
        TINYINT(1) NOT NULL DEFAULT '0' ShipActive
        VARCHAR(40) NOT NULL DEFAULT '' ShipAddress1
        VARCHAR(40) NOT NULL DEFAULT '' ShipAddress2
        VARCHAR(25) NOT NULL DEFAULT '' ShipCity
        VARCHAR(50) NOT NULL DEFAULT '' ShipName
        CHAR(2) NOT NULL DEFAULT '' ShipState
        VARCHAR(10) NOT NULL DEFAULT '' ShipZip
        VARCHAR(50) NOT NULL DEFAULT '' SSNumber
        ENUM('N/A' StudentStatus
        DOUBLE NULL DEFAULT NULL Weight
        ENUM('Bill' Basis
        TINYINT(1) NOT NULL DEFAULT '0' Block12HCFA
        TINYINT(1) NOT NULL DEFAULT '0' Block13HCFA
        DOUBLE NULL DEFAULT NULL CommercialAcctCreditLimit
        VARCHAR(50) NOT NULL DEFAULT '' CommercialAcctTerms
        DOUBLE NULL DEFAULT NULL CopayDollar
        DOUBLE NULL DEFAULT NULL Deductible
        ENUM('Per Visit' Frequency
        TINYINT(1) NOT NULL DEFAULT '0' Hardship
        INT(11) NOT NULL DEFAULT '0' MonthsValid
        DOUBLE NULL DEFAULT NULL OutOfPocket
        DATE NULL DEFAULT NULL SignatureOnFile
        CHAR(1) NULL DEFAULT NULL SignatureType
        INT(11) NULL DEFAULT NULL TaxRateID
        INT(11) NULL DEFAULT NULL Doctor1_ID
        INT(11) NULL DEFAULT NULL Doctor2_ID
        LONGTEXT NOT NULL EmergencyContact
        INT(11) NULL DEFAULT NULL FacilityID
        INT(11) NULL DEFAULT NULL LegalRepID
        INT(11) NULL DEFAULT NULL ReferralID
        INT(11) NULL DEFAULT NULL SalesRepID
        ENUM('Auto' AccidentType
        CHAR(2) NOT NULL DEFAULT '' StateOfAccident
        DATE NULL DEFAULT NULL DateOfInjury
        TINYINT(1) NOT NULL DEFAULT '0' Emergency
        TINYINT(1) NOT NULL DEFAULT '0' EmploymentRelated
        DATE NULL DEFAULT NULL FirstConsultDate
        VARCHAR(6) NULL DEFAULT NULL ICD9_1
        VARCHAR(6) NULL DEFAULT NULL ICD9_2
        VARCHAR(6) NULL DEFAULT NULL ICD9_3
        VARCHAR(6) NULL DEFAULT NULL ICD9_4
        INT(11) NULL DEFAULT NULL POSTypeID
        DATE NULL DEFAULT NULL ReturnToWorkDate
        DOUBLE NULL DEFAULT NULL CopayPercent
        DATE NOT NULL DEFAULT '0000-00-00' SetupDate
        TINYINT(1) NOT NULL DEFAULT '0' HIPPANote
        TINYINT(1) NOT NULL DEFAULT '0' SupplierStandards
        DATE NULL DEFAULT NULL InactiveDate
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        INT(11) NULL DEFAULT '4' InvoiceFormID
        SET('AccountNumber' MIR
        VARCHAR(150) NULL DEFAULT NULL Email
        BIT(1) NOT NULL DEFAULT b'0' Collections
        VARCHAR(8) NULL DEFAULT NULL ICD10_01
        VARCHAR(8) NULL DEFAULT NULL ICD10_02
        VARCHAR(8) NULL DEFAULT NULL ICD10_03
        VARCHAR(8) NULL DEFAULT NULL ICD10_04
        VARCHAR(8) NULL DEFAULT NULL ICD10_05
        VARCHAR(8) NULL DEFAULT NULL ICD10_06
        VARCHAR(8) NULL DEFAULT NULL ICD10_07
        VARCHAR(8) NULL DEFAULT NULL ICD10_08
        VARCHAR(8) NULL DEFAULT NULL ICD10_09
        VARCHAR(8) NULL DEFAULT NULL ICD10_10
        VARCHAR(8) NULL DEFAULT NULL ICD10_11
        VARCHAR(8) NULL DEFAULT NULL ICD10_12
        (`AccountNumber` ASC) VISIBLE AccountNumber
        (`FirstName` ASC IDX_FIRST_LAST_DOB_MIDDLE
        ASC LastName
        ASC DateofBirth
        ASC) VISIBLE MiddleName
        (`InactiveDate` ASC) VISIBLE) IX_customer_InactiveDate
        -- ----------------------------------------------------- tbl_customer_insurance
    }
    tbl_customer_insurance {
        ( tbl_customer_insurance
        VARCHAR(40) NOT NULL DEFAULT '' Address1
        VARCHAR(40) NOT NULL DEFAULT '' Address2
        VARCHAR(25) NOT NULL DEFAULT '' City
        CHAR(2) NOT NULL DEFAULT '' State
        VARCHAR(10) NOT NULL DEFAULT '' Zip
        ENUM('Bill' Basis
        INT(11) NOT NULL DEFAULT '0' CustomerID
        DATE NULL DEFAULT NULL DateofBirth
        ENUM('Male' Gender
        VARCHAR(50) NOT NULL DEFAULT '' GroupNumber
        INT(11) NOT NULL AUTO_INCREMENT ID
        DATE NULL DEFAULT NULL InactiveDate
        INT(11) NOT NULL DEFAULT '0' InsuranceCompanyID
        CHAR(2) NULL DEFAULT NULL InsuranceType
        VARCHAR(25) NOT NULL DEFAULT '' FirstName
        VARCHAR(30) NOT NULL DEFAULT '' LastName
        CHAR(1) NOT NULL DEFAULT '' MiddleName
        VARCHAR(50) NOT NULL DEFAULT '' Employer
        VARCHAR(50) NOT NULL DEFAULT '' Mobile
        INT(11) NULL DEFAULT NULL PaymentPercent
        VARCHAR(50) NOT NULL DEFAULT '' Phone
        VARCHAR(50) NOT NULL DEFAULT '' PolicyNumber
        INT(11) NULL DEFAULT NULL Rank
        CHAR(2) NULL DEFAULT NULL RelationshipCode
        TINYINT(1) NOT NULL DEFAULT '0' RequestEligibility
        DATE NULL DEFAULT NULL RequestEligibilityOn
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        SET('FirstName' MIR
        VARCHAR(4) NOT NULL DEFAULT '' Suffix
        -- ----------------------------------------------------- tbl_customer_notes
    }
    tbl_customer_notes {
        ( tbl_customer_notes
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL CustomerID
        LONGTEXT NOT NULL Notes
        TINYINT(1) NOT NULL DEFAULT '0' Active
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        VARCHAR(50) NULL DEFAULT NULL Operator
        DATETIME NULL DEFAULT NULL CallbackDate
    }
    tbl_customerclass {
        ( tbl_customerclass
        CHAR(2) NOT NULL DEFAULT '' Code
        VARCHAR(50) NOT NULL DEFAULT '' Description
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_customertype
    }
    tbl_customertype {
        ( tbl_customertype
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_denial
    }
    tbl_denial {
        ( tbl_denial
        VARCHAR(6) NOT NULL Code
        VARCHAR(50) NOT NULL Description
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_order
    }
    tbl_order {
        ( tbl_order
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' CustomerID
        TINYINT(1) NOT NULL DEFAULT '0' Approved
        TINYINT(1) NOT NULL DEFAULT '0' RetailSales
        DATE NULL DEFAULT NULL OrderDate
        DATE NULL DEFAULT NULL DeliveryDate
        DATE NULL DEFAULT NULL BillDate
        DATE NULL DEFAULT NULL EndDate
        INT(11) NULL DEFAULT NULL ShippingMethodID
        TEXT NULL DEFAULT NULL SpecialInstructions
        VARCHAR(50) NULL DEFAULT NULL TicketMesage
        INT(11) NULL DEFAULT NULL CustomerInsurance1_ID
        INT(11) NULL DEFAULT NULL CustomerInsurance2_ID
        INT(11) NULL DEFAULT NULL CustomerInsurance3_ID
        INT(11) NULL DEFAULT NULL CustomerInsurance4_ID
        VARCHAR(6) NULL DEFAULT NULL ICD9_1
        VARCHAR(6) NULL DEFAULT NULL ICD9_2
        VARCHAR(6) NULL DEFAULT NULL ICD9_3
        VARCHAR(6) NULL DEFAULT NULL ICD9_4
        INT(11) NULL DEFAULT NULL DoctorID
        INT(11) NULL DEFAULT NULL POSTypeID
        VARCHAR(50) NULL DEFAULT '' TakenBy
        DOUBLE NULL DEFAULT NULL Discount
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        ENUM('Retail' SaleType
        ENUM('New' State
        SET('BillDate' MIR
        TINYINT(1) NOT NULL DEFAULT '0' AcceptAssignment
        VARCHAR(80) NULL DEFAULT NULL ClaimNote
        INT(11) NULL DEFAULT NULL FacilityID
        INT(11) NULL DEFAULT NULL ReferralID
        INT(11) NULL DEFAULT NULL SalesrepID
        INT(11) NULL DEFAULT NULL LocationID
        TINYINT(1) NOT NULL DEFAULT '0' Archived
        DATETIME NULL DEFAULT NULL TakenAt
        VARCHAR(8) NULL DEFAULT NULL ICD10_01
        VARCHAR(8) NULL DEFAULT NULL ICD10_02
        VARCHAR(8) NULL DEFAULT NULL ICD10_03
        VARCHAR(8) NULL DEFAULT NULL ICD10_04
        VARCHAR(8) NULL DEFAULT NULL ICD10_05
        VARCHAR(8) NULL DEFAULT NULL ICD10_06
        VARCHAR(8) NULL DEFAULT NULL ICD10_07
        VARCHAR(8) NULL DEFAULT NULL ICD10_08
        VARCHAR(8) NULL DEFAULT NULL ICD10_09
        VARCHAR(8) NULL DEFAULT NULL ICD10_10
        VARCHAR(8) NULL DEFAULT NULL ICD10_11
        VARCHAR(8) NULL DEFAULT NULL ICD10_12
        VARCHAR(100) NOT NULL DEFAULT '' UserField1
        VARCHAR(100) NOT NULL DEFAULT '' UserField2
        (`CustomerID` ASC IDX_CUSTOMERID_ID
        ASC) VISIBLE) ID
        -- ----------------------------------------------------- tbl_deposits
    }
    tbl_deposits {
        ( tbl_deposits
        INT(11) NOT NULL CustomerID
        INT(11) NOT NULL OrderID
        DECIMAL(18 Amount
        DATE NOT NULL Date
        ENUM('Cash' PaymentMethod
        TEXT NOT NULL Notes
        SMALLINT(6) NOT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        FOREIGN KEY (`CustomerID` FK_DEPOSITS_ORDER
        (`CustomerID` tbl_order
        -- ----------------------------------------------------- tbl_orderdetails
    }
    tbl_orderdetails {
        ( tbl_orderdetails
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' OrderID
        INT(11) NOT NULL DEFAULT '0' CustomerID
        VARCHAR(50) NULL DEFAULT NULL SerialNumber
        INT(11) NOT NULL DEFAULT '0' InventoryItemID
        INT(11) NOT NULL DEFAULT '0' PriceCodeID
        ENUM('Medicare Oxygen Rental' SaleRentType
        INT(11) NULL DEFAULT NULL SerialID
        DECIMAL(18 BillablePrice
        DECIMAL(18 AllowablePrice
        TINYINT(1) NOT NULL DEFAULT '0' Taxable
        TINYINT(1) NOT NULL DEFAULT '0' FlatRate
        DATE NOT NULL DEFAULT '0000-00-00' DOSFrom
        DATE NULL DEFAULT NULL DOSTo
        DATE NULL DEFAULT NULL PickupDate
        TINYINT(1) NOT NULL DEFAULT '0' ShowSpanDates
        DOUBLE NOT NULL DEFAULT '0' OrderedQuantity
        VARCHAR(50) NULL DEFAULT NULL OrderedUnits
        ENUM('One time' OrderedWhen
        DOUBLE NOT NULL DEFAULT '1' OrderedConverter
        DOUBLE NOT NULL DEFAULT '0' BilledQuantity
        VARCHAR(50) NULL DEFAULT NULL BilledUnits
        ENUM('One time' BilledWhen
        DOUBLE NOT NULL DEFAULT '1' BilledConverter
        DOUBLE NOT NULL DEFAULT '0' DeliveryQuantity
        VARCHAR(50) NULL DEFAULT NULL DeliveryUnits
        DOUBLE NOT NULL DEFAULT '1' DeliveryConverter
        VARCHAR(50) NULL DEFAULT NULL BillingCode
        VARCHAR(8) NOT NULL DEFAULT '' Modifier1
        VARCHAR(8) NOT NULL DEFAULT '' Modifier2
        VARCHAR(8) NOT NULL DEFAULT '' Modifier3
        VARCHAR(8) NOT NULL DEFAULT '' Modifier4
        VARCHAR(50) NULL DEFAULT NULL DXPointer
        INT(11) NOT NULL DEFAULT '1' BillingMonth
        ENUM('Day of Delivery' BillItemOn
        VARCHAR(50) NULL DEFAULT NULL AuthorizationNumber
        INT(11) NULL DEFAULT NULL AuthorizationTypeID
        VARCHAR(50) NULL DEFAULT NULL ReasonForPickup
        TINYINT(1) NOT NULL DEFAULT '0' SendCMN_RX_w_invoice
        TINYINT(1) NOT NULL DEFAULT '0' MedicallyUnnecessary
        TINYINT(1) NOT NULL DEFAULT '0' Sale
        VARCHAR(50) NULL DEFAULT NULL SpecialCode
        VARCHAR(50) NULL DEFAULT NULL ReviewCode
        INT(11) NULL DEFAULT NULL NextOrderID
        INT(11) NULL DEFAULT NULL ReoccuringID
        INT(11) NULL DEFAULT NULL CMNFormID
        VARCHAR(10) NULL DEFAULT NULL HAOCode
        ENUM('New' State
        TINYINT(1) NOT NULL DEFAULT '1' BillIns1
        TINYINT(1) NOT NULL DEFAULT '1' BillIns2
        TINYINT(1) NOT NULL DEFAULT '1' BillIns3
        TINYINT(1) NOT NULL DEFAULT '1' BillIns4
        DATE NULL DEFAULT NULL EndDate
        SET('InventoryItemID' MIR
        DATE NULL DEFAULT NULL NextBillingDate
        INT(11) NOT NULL WarehouseID
        TINYINT(1) NOT NULL DEFAULT '0' AcceptAssignment
        VARCHAR(20) NULL DEFAULT NULL DrugNoteField
        VARCHAR(50) NULL DEFAULT NULL DrugControlNumber
        TINYINT(1) NOT NULL DEFAULT '0' NopayIns1
        SMALLINT(6) NOT NULL DEFAULT '0' PointerICD10
        VARCHAR(50) NULL DEFAULT NULL DXPointer10
        VARCHAR(100) NULL DEFAULT NULL HaoDescription
        VARCHAR(100) NOT NULL DEFAULT '' UserField1
        VARCHAR(100) NOT NULL DEFAULT '' UserField2
        DATE NULL DEFAULT NULL AuthorizationExpirationDate
        (`CustomerID` ASC IDX_CUSTOMERID_ORDERID_ID
        ASC OrderID
        ASC) VISIBLE ID
        (`CustomerID` ASC IDX_CUSTOMERID_ORDERID_ID_INVENTORYITEMID
        ASC OrderID
        ASC ID
        ASC) VISIBLE InventoryItemID
        (`CustomerID` ASC IDX_CUSTOMERID_NEXTORDERID
        ASC) VISIBLE NextOrderID
        (`InventoryItemID` ASC IDX_InventoryItemID_SerialNumber
        ASC) VISIBLE SerialNumber
        FOREIGN KEY (`CustomerID` FK_NEXTORDER
        (`CustomerID` tbl_order
        FOREIGN KEY (`CustomerID` FK_ORDER
        (`CustomerID` tbl_order
        -- ----------------------------------------------------- tbl_depositdetails
    }
    tbl_depositdetails {
        ( tbl_depositdetails
        INT(11) NOT NULL OrderDetailsID
        INT(11) NOT NULL OrderID
        INT(11) NOT NULL CustomerID
        DECIMAL(18 Amount
        SMALLINT(6) NOT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        (`CustomerID` ASC IDX_DEPOSITS
        ASC OrderID
        ASC) VISIBLE OrderDetailsID
        FOREIGN KEY (`CustomerID` FK_DEPOSITDETAILS_DEPOSITS
        (`CustomerID` tbl_deposits
        FOREIGN KEY (`OrderDetailsID`) FK_DEPOSITDETAILS_ORDERDETAILS
        (`ID`) tbl_orderdetails
        -- ----------------------------------------------------- tbl_eligibilityrequest
    }
    tbl_eligibilityrequest {
        ( tbl_eligibilityrequest
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' CustomerID
        INT(11) NOT NULL DEFAULT '0' CustomerInsuranceID
        ENUM('Region A' Region
        INT(11) NULL DEFAULT NULL RequestBatchID
        DATETIME NOT NULL DEFAULT '1900-01-01 00:00:00' RequestTime
        MEDIUMTEXT NOT NULL RequestText
        INT(11) NULL DEFAULT NULL ResponseBatchID
        DATETIME NULL DEFAULT NULL ResponseTime
        MEDIUMTEXT NULL DEFAULT NULL ResponseText
        DATETIME NULL DEFAULT NULL SubmissionTime
        MEDIUMTEXT NULL DEFAULT NULL SubmissionText
        -- ----------------------------------------------------- tbl_facility
    }
    tbl_facility {
        ( tbl_facility
        VARCHAR(40) NOT NULL Address1
        VARCHAR(40) NOT NULL Address2
        VARCHAR(25) NOT NULL City
        VARCHAR(50) NOT NULL Contact
        ENUM('1st week of month' DefaultDeliveryWeek
        LONGTEXT NULL DEFAULT NULL Directions
        VARCHAR(50) NOT NULL Fax
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL MedicaidID
        VARCHAR(50) NOT NULL MedicareID
        VARCHAR(50) NOT NULL Name
        VARCHAR(50) NOT NULL Phone
        VARCHAR(50) NOT NULL Phone2
        INT(11) NULL DEFAULT '12' POSTypeID
        VARCHAR(2) NOT NULL State
        VARCHAR(10) NOT NULL Zip
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        VARCHAR(10) NULL DEFAULT NULL NPI
        SET('Name' MIR
        -- ----------------------------------------------------- tbl_hao
    }
    tbl_hao {
        ( tbl_hao
        VARCHAR(10) NOT NULL Code
        LONGTEXT NOT NULL Description
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_image
    }
    tbl_image {
        ( tbl_image
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        VARCHAR(50) NOT NULL DEFAULT '' Type
        TEXT NULL DEFAULT NULL Description
        INT(11) NULL DEFAULT NULL CustomerID
        INT(11) NULL DEFAULT NULL OrderID
        INT(11) NULL DEFAULT NULL InvoiceID
        INT(11) NULL DEFAULT NULL DoctorID
        INT(11) NULL DEFAULT NULL CMNFormID
        BLOB NULL DEFAULT NULL Thumbnail
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_insurancetype
    }
    tbl_insurancetype {
        ( tbl_insurancetype
        VARCHAR(2) NOT NULL Code
        VARCHAR(40) NOT NULL Description
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_inventory
    }
    tbl_inventory {
        ( tbl_inventory
        INT(11) NOT NULL DEFAULT '0' WarehouseID
        INT(11) NOT NULL DEFAULT '0' InventoryItemID
        DOUBLE NOT NULL DEFAULT '0' OnHand
        DOUBLE NOT NULL DEFAULT '0' Committed
        DOUBLE NOT NULL DEFAULT '0' OnOrder
        DOUBLE NOT NULL DEFAULT '0' UnAvailable
        DOUBLE NOT NULL DEFAULT '0' Rented
        DOUBLE NOT NULL DEFAULT '0' Sold
        DOUBLE NOT NULL DEFAULT '0' BackOrdered
        DOUBLE NOT NULL DEFAULT '0' ReOrderPoint
        DECIMAL(18 CostPerUnit
        DECIMAL(18 TotalCost
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_inventory_transaction
    }
    tbl_inventory_transaction {
        ( tbl_inventory_transaction
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' InventoryItemID
        INT(11) NOT NULL DEFAULT '0' WarehouseID
        INT(11) NOT NULL DEFAULT '0' TypeID
        DATE NOT NULL DEFAULT '0000-00-00' Date
        DOUBLE NULL DEFAULT NULL Quantity
        DECIMAL(18 Cost
        VARCHAR(30) NULL DEFAULT NULL Description
        INT(11) NULL DEFAULT NULL SerialID
        INT(11) NULL DEFAULT NULL VendorID
        INT(11) NULL DEFAULT NULL CustomerID
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        INT(11) NULL DEFAULT NULL PurchaseOrderID
        INT(11) NULL DEFAULT NULL PurchaseOrderDetailsID
        INT(11) NULL DEFAULT NULL InvoiceID
        INT(11) NULL DEFAULT NULL ManufacturerID
        INT(11) NULL DEFAULT NULL OrderDetailsID
        INT(11) NULL DEFAULT NULL OrderID
        (`TypeID` ASC idx_typeid_custid_orid_ordetailsid_itemid_warehouseid
        ASC CustomerID
        ASC OrderID
        ASC OrderDetailsID
        ASC InventoryItemID
        ASC) VISIBLE WarehouseID
        (`TypeID` ASC idx_typeid_itemid_warehouseid
        ASC InventoryItemID
        ASC) VISIBLE WarehouseID
        (`TypeID` ASC idx_typeid_poid_podetailsid_itemid_warehouseid
        ASC PurchaseOrderID
        ASC PurchaseOrderDetailsID
        ASC InventoryItemID
        ASC) VISIBLE) WarehouseID
        -- ----------------------------------------------------- tbl_inventory_transaction_type
    }
    tbl_inventory_transaction_type {
        ( tbl_inventory_transaction_type
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        INT(11) NOT NULL DEFAULT '0' OnHand
        INT(11) NOT NULL DEFAULT '0' Committed
        INT(11) NOT NULL DEFAULT '0' OnOrder
        INT(11) NOT NULL DEFAULT '0' UnAvailable
        INT(11) NOT NULL DEFAULT '0' Rented
        INT(11) NOT NULL DEFAULT '0' Sold
        INT(11) NOT NULL DEFAULT '0' BackOrdered
        INT(11) NOT NULL DEFAULT '0' AdjTotalCost
        -- ----------------------------------------------------- tbl_inventoryitem
    }
    tbl_inventoryitem {
        ( tbl_inventoryitem
        VARCHAR(50) NOT NULL DEFAULT '' Barcode
        VARCHAR(50) NOT NULL DEFAULT '' BarcodeType
        ENUM('Bill' Basis
        ENUM('Billing' CommissionPaidAt
        INT(11) NULL DEFAULT NULL VendorID
        TINYINT(1) NOT NULL DEFAULT '0' FlatRate
        DOUBLE NULL DEFAULT NULL FlatRateAmount
        ENUM('One time' Frequency
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' InventoryCode
        VARCHAR(50) NOT NULL DEFAULT '' ModelNumber
        VARCHAR(100) NOT NULL DEFAULT '' Name
        TINYINT(1) NOT NULL DEFAULT '0' O2Tank
        TINYINT(1) NOT NULL DEFAULT '0' Percentage
        DOUBLE NOT NULL DEFAULT '0' PercentageAmount
        INT(11) NULL DEFAULT NULL PredefinedTextID
        INT(11) NULL DEFAULT NULL ProductTypeID
        TINYINT(1) NOT NULL DEFAULT '0' Serialized
        TINYINT(1) NOT NULL DEFAULT '0' Service
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        TINYINT(1) NOT NULL DEFAULT '0' Inactive
        INT(11) NULL DEFAULT NULL ManufacturerID
        DECIMAL(18 PurchasePrice
        VARCHAR(100) NOT NULL DEFAULT '' UserField1
        VARCHAR(100) NOT NULL DEFAULT '' UserField2
        -- ----------------------------------------------------- tbl_invoice
    }
    tbl_invoice {
        ( tbl_invoice
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' CustomerID
        INT(11) NULL DEFAULT NULL OrderID
        TINYINT(1) NOT NULL DEFAULT '0' Approved
        DATE NULL DEFAULT NULL InvoiceDate
        DECIMAL(18 InvoiceBalance
        ENUM('Ins1' SubmittedTo
        VARCHAR(50) NULL DEFAULT NULL SubmittedBy
        DATE NULL DEFAULT NULL SubmittedDate
        VARCHAR(50) NULL DEFAULT NULL SubmittedBatch
        INT(11) NULL DEFAULT NULL CustomerInsurance1_ID
        INT(11) NULL DEFAULT NULL CustomerInsurance2_ID
        INT(11) NULL DEFAULT NULL CustomerInsurance3_ID
        INT(11) NULL DEFAULT NULL CustomerInsurance4_ID
        VARCHAR(6) NULL DEFAULT NULL ICD9_1
        VARCHAR(6) NULL DEFAULT NULL ICD9_2
        VARCHAR(6) NULL DEFAULT NULL ICD9_3
        VARCHAR(6) NULL DEFAULT NULL ICD9_4
        INT(11) NULL DEFAULT NULL DoctorID
        INT(11) NULL DEFAULT NULL POSTypeID
        INT(11) NULL DEFAULT NULL TaxRateID
        DOUBLE NULL DEFAULT NULL TaxRatePercent
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        DOUBLE NULL DEFAULT '0' Discount
        TINYINT(1) NOT NULL DEFAULT '0' AcceptAssignment
        VARCHAR(80) NULL DEFAULT NULL ClaimNote
        INT(11) NULL DEFAULT NULL FacilityID
        INT(11) NULL DEFAULT NULL ReferralID
        INT(11) NULL DEFAULT NULL SalesrepID
        TINYINT(1) NOT NULL DEFAULT '0' Archived
        VARCHAR(8) NULL DEFAULT NULL ICD10_01
        VARCHAR(8) NULL DEFAULT NULL ICD10_02
        VARCHAR(8) NULL DEFAULT NULL ICD10_03
        VARCHAR(8) NULL DEFAULT NULL ICD10_04
        VARCHAR(8) NULL DEFAULT NULL ICD10_05
        VARCHAR(8) NULL DEFAULT NULL ICD10_06
        VARCHAR(8) NULL DEFAULT NULL ICD10_07
        VARCHAR(8) NULL DEFAULT NULL ICD10_08
        VARCHAR(8) NULL DEFAULT NULL ICD10_09
        VARCHAR(8) NULL DEFAULT NULL ICD10_10
        VARCHAR(8) NULL DEFAULT NULL ICD10_11
        VARCHAR(8) NULL DEFAULT NULL ICD10_12
        (`CustomerID` ASC IDX_CUSTOMERID_ID
        ASC) VISIBLE ID
        (`CustomerID` ASC IDX_CUSTOMERID_ORDERID
        ASC) VISIBLE OrderID
        FOREIGN KEY (`CustomerID` FK_ORDER_2
        (`CustomerID` tbl_order
        -- ----------------------------------------------------- tbl_invoicedetails
    }
    tbl_invoicedetails {
        ( tbl_invoicedetails
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' InvoiceID
        INT(11) NOT NULL DEFAULT '0' CustomerID
        INT(11) NOT NULL DEFAULT '0' InventoryItemID
        INT(11) NOT NULL DEFAULT '0' PriceCodeID
        INT(11) NULL DEFAULT NULL OrderID
        INT(11) NULL DEFAULT NULL OrderDetailsID
        DECIMAL(18 Balance
        DECIMAL(18 BillableAmount
        DECIMAL(18 AllowableAmount
        DECIMAL(18 Taxes
        DOUBLE NOT NULL DEFAULT '0' Quantity
        DATE NULL DEFAULT NULL InvoiceDate
        DATE NOT NULL DEFAULT '0000-00-00' DOSFrom
        DATE NULL DEFAULT NULL DOSTo
        VARCHAR(50) NULL DEFAULT NULL BillingCode
        VARCHAR(8) NOT NULL DEFAULT '' Modifier1
        VARCHAR(8) NOT NULL DEFAULT '' Modifier2
        VARCHAR(8) NOT NULL DEFAULT '' Modifier3
        VARCHAR(8) NOT NULL DEFAULT '' Modifier4
        VARCHAR(50) NULL DEFAULT NULL DXPointer
        INT(11) NOT NULL DEFAULT '0' BillingMonth
        TINYINT(1) NOT NULL DEFAULT '0' SendCMN_RX_w_invoice
        VARCHAR(50) NULL DEFAULT NULL SpecialCode
        VARCHAR(50) NULL DEFAULT NULL ReviewCode
        TINYINT(1) NOT NULL DEFAULT '0' MedicallyUnnecessary
        VARCHAR(50) NULL DEFAULT NULL AuthorizationNumber
        INT(11) NULL DEFAULT NULL AuthorizationTypeID
        VARCHAR(255) NULL DEFAULT NULL InvoiceNotes
        VARCHAR(255) NULL DEFAULT NULL InvoiceRecord
        INT(11) NULL DEFAULT NULL CMNFormID
        VARCHAR(10) NULL DEFAULT NULL HAOCode
        TINYINT(1) NOT NULL DEFAULT '1' BillIns1
        TINYINT(1) NOT NULL DEFAULT '1' BillIns2
        TINYINT(1) NOT NULL DEFAULT '1' BillIns3
        TINYINT(1) NOT NULL DEFAULT '1' BillIns4
        TINYINT(1) NOT NULL DEFAULT '0' Hardship
        TINYINT(1) NOT NULL DEFAULT '0' ShowSpanDates
        DECIMAL(18 PaymentAmount
        DECIMAL(18 WriteoffAmount
        ENUM('Ins1' CurrentPayer
        TINYINT(4) NOT NULL DEFAULT '0' Pendings
        TINYINT(4) NOT NULL DEFAULT '0' Submits
        TINYINT(4) NOT NULL DEFAULT '0' Payments
        DATE NULL DEFAULT NULL SubmittedDate
        TINYINT(1) NOT NULL DEFAULT '0' Submitted
        INT(11) NULL DEFAULT NULL CurrentInsuranceCompanyID
        INT(11) NULL DEFAULT NULL CurrentCustomerInsuranceID
        TINYINT(1) NOT NULL DEFAULT '0' AcceptAssignment
        DECIMAL(18 DeductibleAmount
        VARCHAR(20) NULL DEFAULT NULL DrugNoteField
        VARCHAR(50) NULL DEFAULT NULL DrugControlNumber
        TINYINT(1) NOT NULL DEFAULT '0' NopayIns1
        SMALLINT(6) NOT NULL DEFAULT '0' PointerICD10
        VARCHAR(50) NULL DEFAULT NULL DXPointer10
        VARCHAR(100) NULL DEFAULT NULL HaoDescription
        (`CustomerID` ASC IDX_CUSTOMERID_INVOICEID_ID
        ASC InvoiceID
        ASC) VISIBLE ID
        FOREIGN KEY (`CustomerID` FK_INVOICE
        (`CustomerID` tbl_invoice
        -- ----------------------------------------------------- tbl_invoice_transaction
    }
    tbl_invoice_transaction {
        ( tbl_invoice_transaction
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' InvoiceDetailsID
        INT(11) NOT NULL DEFAULT '0' InvoiceID
        INT(11) NOT NULL DEFAULT '0' CustomerID
        INT(11) NULL DEFAULT NULL InsuranceCompanyID
        INT(11) NULL DEFAULT NULL CustomerInsuranceID
        INT(11) NOT NULL DEFAULT '0' TransactionTypeID
        DATE NULL DEFAULT NULL TransactionDate
        DECIMAL(18 Amount
        DOUBLE NOT NULL DEFAULT '0' Quantity
        DECIMAL(18 Taxes
        VARCHAR(20) NOT NULL DEFAULT '' BatchNumber
        TEXT NULL DEFAULT NULL Comments
        TEXT NULL DEFAULT NULL Extra
        TINYINT(1) NOT NULL DEFAULT '0' Approved
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        DECIMAL(18 Deductible
        (`CustomerID` ASC IDX_CUSTOMERID_INVOICEID_INVOICEDETAILSID
        ASC InvoiceID
        ASC) VISIBLE InvoiceDetailsID
        FOREIGN KEY (`CustomerID` FK_INVOICE_TRANSACTION_INVOICE
        (`CustomerID` tbl_invoicedetails
        -- ----------------------------------------------------- tbl_invoice_transactiontype
    }
    tbl_invoice_transactiontype {
        ( tbl_invoice_transactiontype
        INT(11) NOT NULL DEFAULT '0' ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        INT(11) NOT NULL DEFAULT '0' Balance
        INT(11) NOT NULL DEFAULT '0' Allowable
        INT(11) NOT NULL DEFAULT '0' Amount
        INT(11) NOT NULL DEFAULT '0' Taxes
        (`Name` ASC) VISIBLE) IX_invoice_transactiontype_name
        -- ----------------------------------------------------- tbl_invoiceform
    }
    tbl_invoiceform {
        ( tbl_invoiceform
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        VARCHAR(50) NOT NULL ReportFileName
        DOUBLE NOT NULL DEFAULT '0.25' MarginTop
        DOUBLE NOT NULL DEFAULT '0.19' MarginLeft
        DOUBLE NOT NULL DEFAULT '0.18' MarginBottom
        DOUBLE NOT NULL DEFAULT '0.22' MarginRight
        VARCHAR(20) NULL DEFAULT NULL SpecialCoding
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_invoicenotes
    }
    tbl_invoicenotes {
        ( tbl_invoicenotes
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' InvoiceDetailsID
        INT(11) NOT NULL DEFAULT '0' InvoiceID
        INT(11) NOT NULL DEFAULT '0' CustomerID
        DATE NULL DEFAULT NULL CallbackDate
        TINYINT(1) NOT NULL DEFAULT '0' Done
        LONGTEXT NOT NULL Notes
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_kit
    }
    tbl_kit {
        ( tbl_kit
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NULL DEFAULT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_kitdetails
    }
    tbl_kitdetails {
        ( tbl_kitdetails
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL KitID
        INT(11) NOT NULL WarehouseID
        INT(11) NOT NULL InventoryItemID
        INT(11) NULL DEFAULT NULL PriceCodeID
        INT(11) NOT NULL Quantity
        -- ----------------------------------------------------- tbl_legalrep
    }
    tbl_legalrep {
        ( tbl_legalrep
        VARCHAR(40) NOT NULL Address1
        VARCHAR(40) NOT NULL Address2
        VARCHAR(25) NOT NULL City
        ENUM('Dr.' Courtesy
        VARCHAR(25) NOT NULL FirstName
        VARCHAR(50) NOT NULL OfficePhone
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(30) NOT NULL LastName
        VARCHAR(1) NOT NULL MiddleName
        VARCHAR(50) NOT NULL Mobile
        VARCHAR(50) NOT NULL Pager
        VARCHAR(2) NOT NULL State
        VARCHAR(4) NOT NULL Suffix
        VARCHAR(10) NOT NULL Zip
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        VARCHAR(50) NULL DEFAULT NULL FirmName
        -- ----------------------------------------------------- tbl_location
    }
    tbl_location {
        ( tbl_location
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Contact
        VARCHAR(50) NOT NULL DEFAULT '' Name
        VARCHAR(40) NOT NULL DEFAULT '' Code
        VARCHAR(25) NOT NULL DEFAULT '' City
        VARCHAR(40) NOT NULL DEFAULT '' Address1
        VARCHAR(40) NOT NULL DEFAULT '' Address2
        CHAR(2) NOT NULL DEFAULT '' State
        VARCHAR(10) NOT NULL DEFAULT '' Zip
        VARCHAR(50) NOT NULL DEFAULT '' Fax
        VARCHAR(50) NOT NULL DEFAULT '' FEDTaxID
        ENUM('SSN' TaxIDType
        VARCHAR(50) NOT NULL DEFAULT '' Phone
        VARCHAR(50) NOT NULL DEFAULT '' Phone2
        TINYINT(1) NULL DEFAULT NULL PrintInfoOnDelPupTicket
        TINYINT(1) NULL DEFAULT NULL PrintInfoOnInvoiceAcctStatements
        TINYINT(1) NULL DEFAULT NULL PrintInfoOnPartProvider
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        VARCHAR(10) NULL DEFAULT NULL NPI
        INT(11) NULL DEFAULT NULL InvoiceFormID
        INT(11) NULL DEFAULT NULL PriceCodeID
        TINYINT(1) NULL DEFAULT NULL ParticipatingProvider
        VARCHAR(50) NULL DEFAULT NULL Email
        INT(11) NULL DEFAULT NULL WarehouseID
        INT(11) NULL DEFAULT '12' POSTypeID
        INT(11) NULL DEFAULT NULL TaxRateID
        -- ----------------------------------------------------- tbl_manufacturer
    }
    tbl_manufacturer {
        ( tbl_manufacturer
        VARCHAR(40) NOT NULL AccountNumber
        VARCHAR(40) NOT NULL Address1
        VARCHAR(40) NOT NULL Address2
        VARCHAR(25) NOT NULL City
        VARCHAR(50) NOT NULL Contact
        VARCHAR(50) NOT NULL Fax
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        VARCHAR(50) NOT NULL Phone
        VARCHAR(50) NOT NULL Phone2
        VARCHAR(2) NOT NULL State
        VARCHAR(10) NOT NULL Zip
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_medicalconditions
    }
    tbl_medicalconditions {
        ( tbl_medicalconditions
        VARCHAR(6) NOT NULL Code
        VARCHAR(50) NOT NULL Description
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_object
    }
    tbl_object {
        ( tbl_object
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Description
        VARCHAR(50) NOT NULL Name
        -- ----------------------------------------------------- tbl_order_survey
    }
    tbl_order_survey {
        ( tbl_order_survey
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL SurveyID
        INT(11) NOT NULL OrderID
        TEXT NOT NULL Form
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        (`OrderID` ASC) VISIBLE) OrderID
        -- ----------------------------------------------------- tbl_orderdeposits
    }
    tbl_orderdeposits {
        ( tbl_orderdeposits
        INT(11) NOT NULL OrderDetailsID
        INT(11) NOT NULL OrderID
        INT(11) NOT NULL CustomerID
        DECIMAL(18 Amount
        DATE NOT NULL Date
        SMALLINT(6) NOT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        (`CustomerID` ASC IDX_ORDERDEPOSITS
        ASC OrderID
        ASC) VISIBLE OrderDetailsID
        FOREIGN KEY (`CustomerID` FK_ORDERDEPOSITS_ORDER
        (`CustomerID` tbl_order
        FOREIGN KEY (`OrderDetailsID`) FK_ORDERDEPOSITS_ORDERDETAILS
        (`ID`) tbl_orderdetails
        -- ----------------------------------------------------- tbl_payer
    }
    tbl_payer {
        ( tbl_payer
        INT(11) NOT NULL InsuranceCompanyID
        TINYINT(1) NOT NULL DEFAULT '0' ParticipatingProvider
        SMALLINT(6) NOT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        TINYINT(1) NOT NULL DEFAULT '1' ExtractOrderingPhysician
        TINYINT(1) NOT NULL DEFAULT '0' ExtractReferringPhysician
        TINYINT(1) NOT NULL DEFAULT '0' ExtractRenderingProvider
        VARCHAR(10) NOT NULL DEFAULT '' TaxonomyCodePrefix
        -- ----------------------------------------------------- tbl_paymentplan
    }
    tbl_paymentplan {
        ( tbl_paymentplan
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL CustomerID
        ENUM('Weekly' Period
        DATE NOT NULL DEFAULT '1900-01-01' FirstPayment
        INT(11) NOT NULL PaymentCount
        DECIMAL(18 PaymentAmount
        MEDIUMTEXT NULL DEFAULT NULL Details
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_paymentplan_payments
    }
    tbl_paymentplan_payments {
        ( tbl_paymentplan_payments
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL PaymentPlanID
        INT(11) NOT NULL CustomerID
        INT(11) NOT NULL Index
        DATE NOT NULL DEFAULT '1900-01-01' DueDate
        DECIMAL(18 DueAmount
        DATE NULL DEFAULT NULL PaymentDate
        DECIMAL(18 PaymentAmount
        MEDIUMTEXT NULL DEFAULT NULL Details
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_permissions
    }
    tbl_permissions {
        ( tbl_permissions
        SMALLINT(6) NOT NULL UserID
        SMALLINT(6) NOT NULL ObjectID
        TINYINT(1) NOT NULL DEFAULT '0' ADD_EDIT
        TINYINT(1) NOT NULL DEFAULT '0' DELETE
        TINYINT(1) NOT NULL DEFAULT '0' PROCESS
        TINYINT(1) NOT NULL DEFAULT '0' VIEW
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_postype
    }
    tbl_postype {
        ( tbl_postype
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_predefinedtext
    }
    tbl_predefinedtext {
        ( tbl_predefinedtext
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        ENUM('Document Text' Type
        LONGTEXT NOT NULL Text
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_pricecode
    }
    tbl_pricecode {
        ( tbl_pricecode
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_pricecode_item
    }
    tbl_pricecode_item {
        ( tbl_pricecode_item
        TINYINT(1) NOT NULL DEFAULT '0' AcceptAssignment
        DOUBLE NOT NULL DEFAULT '0' OrderedQuantity
        VARCHAR(50) NULL DEFAULT NULL OrderedUnits
        ENUM('One time' OrderedWhen
        DOUBLE NOT NULL DEFAULT '1' OrderedConverter
        VARCHAR(50) NULL DEFAULT NULL BilledUnits
        ENUM('One time' BilledWhen
        DOUBLE NOT NULL DEFAULT '1' BilledConverter
        VARCHAR(50) NULL DEFAULT NULL DeliveryUnits
        DOUBLE NOT NULL DEFAULT '1' DeliveryConverter
        VARCHAR(50) NULL DEFAULT NULL BillingCode
        ENUM('Day of Delivery' BillItemOn
        ENUM('DMERC 02.03A' DefaultCMNType
        ENUM('Sale' DefaultOrderType
        INT(11) NULL DEFAULT NULL AuthorizationTypeID
        TINYINT(1) NOT NULL DEFAULT '0' FlatRate
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' InventoryItemID
        VARCHAR(8) NOT NULL DEFAULT '' Modifier1
        VARCHAR(8) NOT NULL DEFAULT '' Modifier2
        VARCHAR(8) NOT NULL DEFAULT '' Modifier3
        VARCHAR(8) NOT NULL DEFAULT '' Modifier4
        INT(11) NOT NULL DEFAULT '0' PriceCodeID
        INT(11) NULL DEFAULT NULL PredefinedTextID
        DECIMAL(18 Rent_AllowablePrice
        DECIMAL(18 Rent_BillablePrice
        DECIMAL(18 Sale_AllowablePrice
        DECIMAL(18 Sale_BillablePrice
        ENUM('Medicare Oxygen Rental' RentalType
        TINYINT(1) NOT NULL DEFAULT '0' ReoccuringSale
        TINYINT(1) NOT NULL DEFAULT '0' ShowSpanDates
        TINYINT(1) NOT NULL DEFAULT '0' Taxable
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        TINYINT(1) NOT NULL DEFAULT '1' BillInsurance
        VARCHAR(20) NULL DEFAULT NULL DrugNoteField
        VARCHAR(50) NULL DEFAULT NULL DrugControlNumber
        VARCHAR(100) NOT NULL DEFAULT '' UserField1
        VARCHAR(100) NOT NULL DEFAULT '' UserField2
        (`InventoryItemID` ASC InventoryItemID
        ASC) VISIBLE) PriceCodeID
        -- ----------------------------------------------------- tbl_producttype
    }
    tbl_producttype {
        ( tbl_producttype
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_provider
    }
    tbl_provider {
        ( tbl_provider
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' LocationID
        INT(11) NOT NULL DEFAULT '0' InsuranceCompanyID
        VARCHAR(25) NOT NULL DEFAULT '' ProviderNumber
        VARCHAR(20) NOT NULL DEFAULT '' Password
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        VARCHAR(6) NOT NULL DEFAULT '1C' ProviderNumberType
        -- ----------------------------------------------------- tbl_providernumbertype
    }
    tbl_providernumbertype {
        ( tbl_providernumbertype
        VARCHAR(6) NOT NULL Code
        VARCHAR(100) NOT NULL Description
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_purchaseorder
    }
    tbl_purchaseorder {
        ( tbl_purchaseorder
        TINYINT(1) NOT NULL DEFAULT '0' Approved
        DECIMAL(18 Cost
        DECIMAL(18 Freight
        INT(11) NOT NULL AUTO_INCREMENT ID
        DECIMAL(18 Tax
        DECIMAL(18 TotalDue
        INT(11) NOT NULL VendorID
        VARCHAR(50) NOT NULL ShipToName
        VARCHAR(40) NOT NULL ShipToAddress1
        VARCHAR(40) NOT NULL ShipToAddress2
        VARCHAR(25) NOT NULL ShipToCity
        VARCHAR(2) NOT NULL ShipToState
        VARCHAR(10) NOT NULL ShipToZip
        VARCHAR(50) NOT NULL ShipToPhone
        DATE NULL DEFAULT NULL OrderDate
        VARCHAR(50) NOT NULL CompanyName
        VARCHAR(40) NOT NULL CompanyAddress1
        VARCHAR(40) NOT NULL CompanyAddress2
        VARCHAR(25) NOT NULL CompanyCity
        VARCHAR(2) NOT NULL CompanyState
        VARCHAR(10) NOT NULL CompanyZip
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        ENUM('BEST WAY' ShipVia
        VARCHAR(50) NULL DEFAULT NULL FOB
        VARCHAR(50) NULL DEFAULT NULL VendorSalesRep
        TEXT NULL DEFAULT NULL Terms
        VARCHAR(50) NULL DEFAULT NULL CompanyPhone
        INT(11) NULL DEFAULT NULL TaxRateID
        TINYINT(1) NOT NULL DEFAULT '0' Reoccuring
    }
    tbl_purchaseorderdetails {
        ( tbl_purchaseorderdetails
        INT(11) NOT NULL DEFAULT '0' BackOrder
        INT(11) NOT NULL DEFAULT '0' Ordered
        INT(11) NOT NULL DEFAULT '0' Received
        DOUBLE NOT NULL DEFAULT '0' Price
        VARCHAR(50) NULL DEFAULT NULL Customer
        DATE NULL DEFAULT NULL DatePromised
        DATE NULL DEFAULT NULL DateReceived
        TINYINT(1) NOT NULL DEFAULT '0' DropShipToCustomer
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL InventoryItemID
        INT(11) NULL DEFAULT NULL PurchaseOrderID
        INT(11) NULL DEFAULT NULL WarehouseID
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        VARCHAR(50) NULL DEFAULT NULL VendorSTKNumber
        VARCHAR(50) NULL DEFAULT NULL ReferenceNumber
        (`PurchaseOrderID` ASC) VISIBLE) ix_purchaseorderdetails_parent
        -- ----------------------------------------------------- tbl_referral
    }
    tbl_referral {
        ( tbl_referral
        VARCHAR(40) NOT NULL Address1
        VARCHAR(40) NOT NULL Address2
        VARCHAR(25) NOT NULL City
        ENUM('Dr.' Courtesy
        VARCHAR(50) NOT NULL Employer
        VARCHAR(50) NOT NULL Fax
        VARCHAR(25) NOT NULL FirstName
        VARCHAR(50) NOT NULL HomePhone
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(30) NOT NULL LastName
        VARCHAR(1) NOT NULL MiddleName
        VARCHAR(50) NOT NULL Mobile
        INT(11) NULL DEFAULT NULL ReferralTypeID
        VARCHAR(2) NOT NULL State
        VARCHAR(4) NOT NULL Suffix
        VARCHAR(50) NOT NULL WorkPhone
        VARCHAR(10) NOT NULL Zip
        DATE NULL DEFAULT NULL LastContacted
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_referraltype
    }
    tbl_referraltype {
        ( tbl_referraltype
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_relationship
    }
    tbl_relationship {
        ( tbl_relationship
        CHAR(2) NOT NULL DEFAULT '' Code
        VARCHAR(100) NOT NULL DEFAULT '' Description
        -- ----------------------------------------------------- tbl_salesrep
    }
    tbl_salesrep {
        ( tbl_salesrep
        VARCHAR(40) NOT NULL Address1
        VARCHAR(40) NOT NULL Address2
        VARCHAR(25) NOT NULL City
        ENUM('Dr.' Courtesy
        VARCHAR(25) NOT NULL FirstName
        VARCHAR(50) NOT NULL HomePhone
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(30) NOT NULL LastName
        VARCHAR(1) NOT NULL MiddleName
        VARCHAR(50) NOT NULL Mobile
        VARCHAR(50) NOT NULL Pager
        VARCHAR(2) NOT NULL State
        VARCHAR(4) NOT NULL Suffix
        VARCHAR(10) NOT NULL Zip
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_serial
    }
    tbl_serial {
        ( tbl_serial
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NULL DEFAULT NULL CurrentCustomerID
        INT(11) NOT NULL DEFAULT '0' InventoryItemID
        INT(11) NULL DEFAULT NULL LastCustomerID
        INT(11) NULL DEFAULT NULL ManufacturerID
        INT(11) NULL DEFAULT NULL VendorID
        INT(11) NULL DEFAULT NULL WarehouseID
        VARCHAR(50) NOT NULL DEFAULT '' LengthOfWarranty
        VARCHAR(50) NOT NULL DEFAULT '' LotNumber
        LONGTEXT NOT NULL MaintenanceRecord
        VARCHAR(50) NOT NULL DEFAULT '' ManufaturerSerialNumber
        VARCHAR(50) NOT NULL DEFAULT '' ModelNumber
        VARCHAR(50) NOT NULL DEFAULT '' MonthsRented
        DATE NULL DEFAULT NULL NextMaintenanceDate
        INT(11) NULL DEFAULT NULL PurchaseOrderID
        DOUBLE NOT NULL DEFAULT '0' PurchaseAmount
        DATE NULL DEFAULT NULL PurchaseDate
        VARCHAR(50) NOT NULL DEFAULT '' SerialNumber
        DATE NULL DEFAULT NULL SoldDate
        ENUM('Empty' Status
        VARCHAR(50) NOT NULL DEFAULT '' Warranty
        ENUM('Own' OwnRent
        DATE NULL DEFAULT NULL FirstRented
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        DECIMAL(18 SalvageValue
        DECIMAL(18 SalePrice
        VARCHAR(20) NULL DEFAULT NULL ConsignmentType
        VARCHAR(50) NULL DEFAULT NULL ConsignmentName
        DATETIME NULL DEFAULT NULL ConsignmentDate
        VARCHAR(20) NULL DEFAULT NULL VendorStockNumber
        DATETIME NULL DEFAULT NULL LotNumberExpires
        (`InventoryItemID` ASC IDX_InventoryItemID_SerialNumber
        ASC) VISIBLE) SerialNumber
        -- ----------------------------------------------------- tbl_serial_maintenance
    }
    tbl_serial_maintenance {
        ( tbl_serial_maintenance
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL SerialID
        TEXT NULL DEFAULT NULL AdditionalEquipment
        TEXT NULL DEFAULT NULL DescriptionOfProblem
        TEXT NULL DEFAULT NULL DescriptionOfWork
        TEXT NULL DEFAULT NULL MaintenanceRecord
        VARCHAR(255) NULL DEFAULT NULL LaborHours
        VARCHAR(255) NULL DEFAULT NULL Technician
        DATE NULL DEFAULT NULL MaintenanceDue
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        DECIMAL(18 MaintenanceCost
        -- ----------------------------------------------------- tbl_serial_transaction
    }
    tbl_serial_transaction {
        ( tbl_serial_transaction
        INT(11) NOT NULL AUTO_INCREMENT ID
        INT(11) NOT NULL DEFAULT '0' TypeID
        INT(11) NOT NULL DEFAULT '0' SerialID
        DATETIME NOT NULL TransactionDatetime
        INT(11) NULL DEFAULT NULL VendorID
        INT(11) NULL DEFAULT NULL WarehouseID
        INT(11) NULL DEFAULT NULL CustomerID
        INT(11) NULL DEFAULT NULL OrderID
        INT(11) NULL DEFAULT NULL OrderDetailsID
        VARCHAR(50) NOT NULL DEFAULT '' LotNumber
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_serial_transaction_type
    }
    tbl_serial_transaction_type {
        ( tbl_serial_transaction_type
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        -- ----------------------------------------------------- tbl_sessions
    }
    tbl_sessions {
        ( tbl_sessions
        INT(11) NOT NULL AUTO_INCREMENT ID
        SMALLINT(6) NOT NULL UserID
        DATETIME NOT NULL LoginTime
        DATETIME NOT NULL LastUpdateTime
        -- ----------------------------------------------------- tbl_shippingmethod
    }
    tbl_shippingmethod {
        ( tbl_shippingmethod
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        VARCHAR(50) NULL DEFAULT NULL Type
        -- ----------------------------------------------------- tbl_signaturetype
    }
    tbl_signaturetype {
        ( tbl_signaturetype
        CHAR(1) NOT NULL DEFAULT '' Code
        VARCHAR(100) NOT NULL DEFAULT '' Description
        -- ----------------------------------------------------- tbl_submitter
    }
    tbl_submitter {
        ( tbl_submitter
        INT(11) NOT NULL AUTO_INCREMENT ID
        ENUM('Region A' ECSFormat
        VARCHAR(50) NOT NULL DEFAULT '' Name
        VARCHAR(16) NOT NULL DEFAULT '' Number
        VARCHAR(50) NOT NULL DEFAULT '' Password
        TINYINT(1) NOT NULL DEFAULT '0' Production
        VARCHAR(50) NOT NULL DEFAULT '' ContactName
        VARCHAR(40) NOT NULL DEFAULT '' Address1
        VARCHAR(40) NOT NULL DEFAULT '' Address2
        VARCHAR(25) NOT NULL DEFAULT '' City
        CHAR(2) NOT NULL DEFAULT '' State
        VARCHAR(10) NOT NULL DEFAULT '' Zip
        VARCHAR(50) NOT NULL DEFAULT '' Phone1
        VARCHAR(50) NOT NULL DEFAULT '' LastBatchNumber
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_survey
    }
    tbl_survey {
        ( tbl_survey
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(100) NOT NULL Name
        VARCHAR(200) NOT NULL Description
        MEDIUMTEXT NOT NULL Template
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_taxrate
    }
    tbl_taxrate {
        ( tbl_taxrate
        INT(11) NOT NULL AUTO_INCREMENT ID
        DOUBLE NULL DEFAULT NULL CityTax
        DOUBLE NULL DEFAULT NULL CountyTax
        VARCHAR(50) NOT NULL Name
        DOUBLE NULL DEFAULT NULL OtherTax
        DOUBLE NULL DEFAULT NULL StateTax
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_user
    }
    tbl_user {
        ( tbl_user
        SMALLINT(6) NOT NULL AUTO_INCREMENT ID
        VARCHAR(16) NOT NULL Login
        VARCHAR(32) NOT NULL Password
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        VARCHAR(150) NOT NULL DEFAULT '' Email
        (`Login` ASC) VISIBLE) Login
        -- ----------------------------------------------------- tbl_user_location
    }
    tbl_user_location {
        ( tbl_user_location
        SMALLINT(6) NOT NULL UserID
        INT(11) NOT NULL LocationID
        (`LocationID` ASC LocationID
        ASC) VISIBLE) UserID
        -- ----------------------------------------------------- tbl_user_notifications
    }
    tbl_user_notifications {
        ( tbl_user_notifications
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Type
        VARCHAR(255) NOT NULL Args
        SMALLINT(6) NOT NULL UserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP Datetime
        -- ----------------------------------------------------- tbl_variables
    }
    tbl_variables {
        ( tbl_variables
        VARCHAR(31) NOT NULL Name
        VARCHAR(255) NOT NULL Value
        -- ----------------------------------------------------- tbl_vendor
    }
    tbl_vendor {
        ( tbl_vendor
        VARCHAR(40) NOT NULL AccountNumber
        VARCHAR(40) NOT NULL Address1
        VARCHAR(40) NOT NULL Address2
        VARCHAR(25) NOT NULL City
        VARCHAR(50) NOT NULL Contact
        VARCHAR(50) NOT NULL Fax
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        VARCHAR(50) NOT NULL Phone
        VARCHAR(50) NOT NULL Phone2
        VARCHAR(2) NOT NULL State
        VARCHAR(10) NOT NULL Zip
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        TEXT NULL DEFAULT NULL Comments
        VARCHAR(50) NULL DEFAULT NULL FOBDelivery
        VARCHAR(50) NULL DEFAULT NULL Terms
        VARCHAR(50) NULL DEFAULT NULL ShipVia
        -- ----------------------------------------------------- tbl_warehouse
    }
    tbl_warehouse {
        ( tbl_warehouse
        VARCHAR(40) NOT NULL DEFAULT '' Address1
        VARCHAR(40) NOT NULL DEFAULT '' Address2
        VARCHAR(25) NOT NULL DEFAULT '' City
        VARCHAR(50) NOT NULL DEFAULT '' Contact
        VARCHAR(50) NOT NULL DEFAULT '' Fax
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        VARCHAR(50) NOT NULL DEFAULT '' Phone
        VARCHAR(50) NOT NULL DEFAULT '' Phone2
        CHAR(2) NOT NULL DEFAULT '' State
        VARCHAR(10) NOT NULL DEFAULT '' Zip
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        ; repository
        -- ----------------------------------------------------- tbl_batches
    }
    tbl_batches {
        ( tbl_batches
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NULL DEFAULT NULL Region
        VARCHAR(50) NULL DEFAULT NULL Company
        VARCHAR(50) NULL DEFAULT NULL Workflow
        VARCHAR(250) NULL DEFAULT NULL FileName
        VARCHAR(255) NULL DEFAULT NULL Location
        VARCHAR(50) NULL DEFAULT NULL FileType
        VARCHAR(50) NULL DEFAULT NULL Status
    }
    tbl_certificates {
        ( tbl_certificates
        VARCHAR(50) NOT NULL Name
        VARCHAR(100) NULL DEFAULT NULL Description
        MEDIUMBLOB NULL DEFAULT NULL Data
        -- ----------------------------------------------------- tbl_companies
    }
    tbl_companies {
        ( tbl_companies
        VARCHAR(50) NOT NULL Name
        VARCHAR(50) NULL DEFAULT NULL ODBCDSN
        VARCHAR(50) NULL DEFAULT NULL Server
        INT(11) NULL DEFAULT NULL Port
        VARCHAR(50) NULL DEFAULT NULL Database
        -- ----------------------------------------------------- tbl_globals
    }
    tbl_globals {
        ( tbl_globals
        VARCHAR(50) NOT NULL Name
        VARCHAR(255) NULL DEFAULT NULL Value
        -- ----------------------------------------------------- tbl_regions
    }
    tbl_regions {
        ( tbl_regions
        VARCHAR(50) NOT NULL Name
        VARCHAR(50) NULL DEFAULT NULL ReceiverID
        VARCHAR(50) NULL DEFAULT NULL ReceiverName
        VARCHAR(50) NULL DEFAULT NULL ReceiverCode
        VARCHAR(50) NULL DEFAULT NULL SubmitterID
        VARCHAR(50) NULL DEFAULT NULL SubmitterName
        VARCHAR(50) NULL DEFAULT NULL SubmitterNumber
        VARCHAR(50) NULL DEFAULT NULL SubmitterContact
        VARCHAR(50) NULL DEFAULT NULL SubmitterPhone
        VARCHAR(50) NULL DEFAULT NULL SubmitterAddress1
        VARCHAR(50) NULL DEFAULT NULL SubmitterAddress2
        VARCHAR(50) NULL DEFAULT NULL SubmitterCity
        VARCHAR(50) NULL DEFAULT NULL SubmitterState
        VARCHAR(50) NULL DEFAULT NULL SubmitterZip
        TINYINT(1) NULL DEFAULT NULL Production
        VARCHAR(50) NULL DEFAULT NULL Login
        VARCHAR(50) NULL DEFAULT NULL Password
        VARCHAR(250) NULL DEFAULT NULL Phone
        TINYINT(1) NULL DEFAULT NULL ZipAbility
        TINYINT(1) NULL DEFAULT NULL UpdateAllowable
        TINYINT(1) NULL DEFAULT NULL PostZeroPay
        VARCHAR(255) NULL DEFAULT NULL UploadMask
        VARCHAR(255) NULL DEFAULT NULL DownloadMask
        -- ----------------------------------------------------- tbl_variables
    }
    tbl_variables {
        ( tbl_variables
        VARCHAR(31) NOT NULL Name
        VARCHAR(255) NOT NULL Value
        ; dmeworks
        -- ----------------------------------------------------- tbl_ability_eligibility_payer
    }
    tbl_ability_eligibility_payer {
        ( tbl_ability_eligibility_payer
        INT(11) NOT NULL AUTO_INCREMENT Id
        VARCHAR(50) NOT NULL Code
        VARCHAR(100) NOT NULL Name
        VARCHAR(100) NOT NULL Comments
        MEDIUMTEXT NOT NULL SearchOptions
        TINYINT(1) NOT NULL DEFAULT '1' AllowsSubmission
        (`Code` ASC) VISIBLE) uq_ability_eligibility_payer
        -- ----------------------------------------------------- tbl_doctor
    }
    tbl_doctor {
        ( tbl_doctor
        VARCHAR(40) NOT NULL Address1
        VARCHAR(40) NOT NULL Address2
        VARCHAR(25) NOT NULL City
        VARCHAR(50) NOT NULL Contact
        ENUM('Dr.' Courtesy
        VARCHAR(50) NOT NULL Fax
        VARCHAR(25) NOT NULL FirstName
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(30) NOT NULL LastName
        VARCHAR(16) NOT NULL LicenseNumber
        DATE NULL DEFAULT NULL LicenseExpired
        VARCHAR(16) NOT NULL MedicaidNumber
        VARCHAR(1) NOT NULL MiddleName
        VARCHAR(16) NOT NULL OtherID
        VARCHAR(9) NOT NULL DEFAULT '' FEDTaxID
        VARCHAR(20) NOT NULL DEFAULT '' DEANumber
        VARCHAR(50) NOT NULL Phone
        VARCHAR(50) NOT NULL Phone2
        VARCHAR(2) NOT NULL State
        VARCHAR(4) NOT NULL Suffix
        VARCHAR(50) NOT NULL Title
        INT(11) NULL DEFAULT NULL TypeID
        VARCHAR(11) NOT NULL UPINNumber
        VARCHAR(10) NOT NULL Zip
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        SET('FirstName' MIR
        VARCHAR(10) NULL DEFAULT NULL NPI
        TINYINT(1) NOT NULL DEFAULT '0' PecosEnrolled
        -- ----------------------------------------------------- tbl_doctortype
    }
    tbl_doctortype {
        ( tbl_doctortype
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_icd10
    }
    tbl_icd10 {
        ( tbl_icd10
        VARCHAR(8) NOT NULL Code
        VARCHAR(255) NOT NULL DEFAULT '' Description
        TINYINT(1) NOT NULL DEFAULT '0' Header
        DATE NULL DEFAULT NULL ActiveDate
        DATE NULL DEFAULT NULL InactiveDate
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_icd9
    }
    tbl_icd9 {
        ( tbl_icd9
        VARCHAR(6) NOT NULL DEFAULT '' Code
        VARCHAR(255) NOT NULL DEFAULT '' Description
        DATE NULL DEFAULT NULL ActiveDate
        DATE NULL DEFAULT NULL InactiveDate
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_insurancecompany
    }
    tbl_insurancecompany {
        ( tbl_insurancecompany
        VARCHAR(40) NOT NULL DEFAULT '' Address1
        VARCHAR(40) NOT NULL DEFAULT '' Address2
        ENUM('Bill' Basis
        VARCHAR(25) NOT NULL DEFAULT '' City
        VARCHAR(50) NOT NULL DEFAULT '' Contact
        ENUM('Region A' ECSFormat
        DOUBLE NULL DEFAULT NULL ExpectedPercent
        VARCHAR(50) NOT NULL DEFAULT '' Fax
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        VARCHAR(50) NOT NULL DEFAULT '' Phone
        VARCHAR(50) NOT NULL DEFAULT '' Phone2
        INT(11) NULL DEFAULT NULL PriceCodeID
        TINYINT(1) NULL DEFAULT NULL PrintHAOOnInvoice
        TINYINT(1) NULL DEFAULT NULL PrintInvOnInvoice
        CHAR(2) NOT NULL DEFAULT '' State
        VARCHAR(50) NOT NULL DEFAULT '' Title
        INT(11) NULL DEFAULT NULL Type
        VARCHAR(10) NOT NULL DEFAULT '' Zip
        VARCHAR(50) NOT NULL DEFAULT '' MedicareNumber
        VARCHAR(50) NOT NULL DEFAULT '' OfficeAllyNumber
        VARCHAR(50) NOT NULL DEFAULT '' ZirmedNumber
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        INT(11) NULL DEFAULT NULL InvoiceFormID
        VARCHAR(50) NOT NULL DEFAULT '' MedicaidNumber
        SET('MedicareNumber') NOT NULL DEFAULT '' MIR
        INT(11) NULL DEFAULT NULL GroupID
        VARCHAR(50) NOT NULL DEFAULT '' AvailityNumber
        VARCHAR(50) NOT NULL DEFAULT '' AbilityNumber
        INT(11) NULL DEFAULT NULL AbilityEligibilityPayerId
        -- ----------------------------------------------------- tbl_insurancecompanygroup
    }
    tbl_insurancecompanygroup {
        ( tbl_insurancecompanygroup
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        SMALLINT(6) NULL DEFAULT NULL LastUpdateUserID
        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP LastUpdateDatetime
        -- ----------------------------------------------------- tbl_insurancecompanytype
    }
    tbl_insurancecompanytype {
        ( tbl_insurancecompanytype
        INT(11) NOT NULL AUTO_INCREMENT ID
        VARCHAR(50) NOT NULL DEFAULT '' Name
        -- ----------------------------------------------------- tbl_variables
    }
    tbl_variables {
        ( tbl_variables
        VARCHAR(31) NOT NULL Name
        VARCHAR(255) NOT NULL Value
        -- ----------------------------------------------------- tbl_zipcode
    }
    tbl_zipcode {
        ( tbl_zipcode
        VARCHAR(10) NOT NULL Zip
        VARCHAR(2) NOT NULL State
        VARCHAR(30) NOT NULL City
        ; c01
        -- ----------------------------------------------------- tbl_ability_eligibility_payer
    }
    tbl_ability_eligibility_payer {
        (`Id` INT tbl_ability_eligibility_payer
        INT Code
        INT Name
        INT Comments
        INT SearchOptions
        INT); AllowsSubmission
        -- ----------------------------------------------------- tbl_doctor
    }
    tbl_doctor {
        (`Address1` INT tbl_doctor
        INT Address2
        INT City
        INT Contact
        INT Courtesy
        INT Fax
        INT FirstName
        INT ID
        INT LastName
        INT LicenseNumber
        INT LicenseExpired
        INT MedicaidNumber
        INT MiddleName
        INT OtherID
        INT FEDTaxID
        INT DEANumber
        INT Phone
        INT Phone2
        INT State
        INT Suffix
        INT Title
        INT TypeID
        INT UPINNumber
        INT Zip
        INT LastUpdateUserID
        INT LastUpdateDatetime
        INT MIR
        INT NPI
        INT); PecosEnrolled
        -- ----------------------------------------------------- tbl_doctortype
    }
    tbl_doctortype {
        (`ID` INT tbl_doctortype
        INT Name
        INT LastUpdateUserID
        INT); LastUpdateDatetime
        -- ----------------------------------------------------- tbl_icd10
    }
    tbl_icd10 {
        (`Code` INT tbl_icd10
        INT Description
        INT Header
        INT ActiveDate
        INT InactiveDate
        INT LastUpdateUserID
        INT); LastUpdateDatetime
        -- ----------------------------------------------------- tbl_icd9
    }
    tbl_icd9 {
        (`Code` INT tbl_icd9
        INT Description
        INT ActiveDate
        INT InactiveDate
        INT LastUpdateUserID
        INT); LastUpdateDatetime
        -- ----------------------------------------------------- tbl_insurancecompany
    }
    tbl_insurancecompany {
        (`Address1` INT tbl_insurancecompany
        INT Address2
        INT Basis
        INT City
        INT Contact
        INT ECSFormat
        INT ExpectedPercent
        INT Fax
        INT ID
        INT Name
        INT Phone
        INT Phone2
        INT PriceCodeID
        INT PrintHAOOnInvoice
        INT PrintInvOnInvoice
        INT State
        INT Title
        INT Type
        INT Zip
        INT MedicareNumber
        INT OfficeAllyNumber
        INT ZirmedNumber
        INT LastUpdateUserID
        INT LastUpdateDatetime
        INT InvoiceFormID
        INT MedicaidNumber
        INT MIR
        INT GroupID
        INT AvailityNumber
        INT AbilityNumber
        INT); AbilityEligibilityPayerId
        -- ----------------------------------------------------- tbl_insurancecompanygroup
    }
    tbl_insurancecompanygroup {
        (`ID` INT tbl_insurancecompanygroup
        INT Name
        INT LastUpdateUserID
        INT); LastUpdateDatetime
        -- ----------------------------------------------------- tbl_insurancecompanytype
    }
    tbl_insurancecompanytype {
        (`ID` INT tbl_insurancecompanytype
        INT); Name
        -- ----------------------------------------------------- tbl_zipcode
    }
    tbl_zipcode {
        (`Zip` INT tbl_zipcode
        INT State
        INT); City
        -- ----------------------------------------------------- view_billinglist
    }
    view_billinglist {
        (`OrderID` INT view_billinglist
        INT BillingMonth
        INT BillingFlags
        INT); BillingTypeID
        -- ----------------------------------------------------- view_invoicetransaction_statistics
    }
    view_invoicetransaction_statistics {
        (`CustomerID` INT view_invoicetransaction_statistics
        INT OrderID
        INT InvoiceID
        INT InvoiceDetailsID
        INT BillableAmount
        INT AllowableAmount
        INT Quantity
        INT Hardship
        INT BillingCode
        INT InventoryItemID
        INT DOSFrom
        INT DOSTo
        INT Insurance1_ID
        INT Insurance2_ID
        INT Insurance3_ID
        INT Insurance4_ID
        INT InsuranceCompany1_ID
        INT InsuranceCompany2_ID
        INT InsuranceCompany3_ID
        INT InsuranceCompany4_ID
        INT Percent
        INT Basis
        INT PaymentAmount
        INT WriteoffAmount
        INT Insurances
        INT PendingSubmissions
        INT Submits
        INT Payments
        INT CurrentInsuranceID
        INT CurrentInsuranceCompanyID
        INT InvoiceSubmitted
        INT SubmittedDate
        INT CurrentPayer
        INT); NopayIns1
        -- ----------------------------------------------------- view_mir
    }
    view_mir {
        (`OrderDetailsID` INT view_mir
        INT OrderID
        INT OrderApproved
        INT CustomerID
        INT CustomerName
        INT CustomerInsuranceID_1
        INT InsuranceCompanyID_1
        INT CustomerInsuranceID_2
        INT InsuranceCompanyID_2
        INT CMNFormID
        INT FacilityID
        INT DoctorID
        INT SaleRentType
        INT BillingCode
        INT Payers
        INT InventoryItem
        INT PriceCode
        INT MIR
        INT); Details
        -- ----------------------------------------------------- view_orderdetails
    }
    view_orderdetails {
        (`ID` INT view_orderdetails
        INT OrderID
        INT CustomerID
        INT SerialNumber
        INT InventoryItemID
        INT PriceCodeID
        INT SaleRentType
        INT SerialID
        INT BillablePrice
        INT AllowablePrice
        INT Taxable
        INT FlatRate
        INT DOSFrom
        INT DOSTo
        INT PickupDate
        INT ShowSpanDates
        INT OrderedQuantity
        INT OrderedUnits
        INT OrderedWhen
        INT OrderedConverter
        INT BilledQuantity
        INT BilledUnits
        INT BilledWhen
        INT BilledConverter
        INT DeliveryQuantity
        INT DeliveryUnits
        INT DeliveryConverter
        INT BillingCode
        INT Modifier1
        INT Modifier2
        INT Modifier3
        INT Modifier4
        INT DXPointer
        INT BillingMonth
        INT BillItemOn
        INT AuthorizationNumber
        INT AuthorizationTypeID
        INT ReasonForPickup
        INT SendCMN_RX_w_invoice
        INT MedicallyUnnecessary
        INT Sale
        INT SpecialCode
        INT ReviewCode
        INT NextOrderID
        INT ReoccuringID
        INT CMNFormID
        INT HAOCode
        INT State
        INT BillIns1
        INT BillIns2
        INT BillIns3
        INT BillIns4
        INT EndDate
        INT MIR
        INT NextBillingDate
        INT WarehouseID
        INT AcceptAssignment
        INT DrugNoteField
        INT DrugControlNumber
        INT NopayIns1
        INT PointerICD10
        INT DXPointer10
        INT HaoDescription
        INT UserField1
        INT UserField2
        INT AuthorizationExpirationDate
        INT IsActive
        INT IsCanceled
        INT IsSold
        INT IsRented
        INT ActualSaleRentType
        INT ActualBillItemOn
        INT ActualOrderedWhen
        INT ActualBilledWhen
        INT ActualDosTo
        INT InvoiceDate
        INT IsOxygen
        INT IsZeroAmount
        INT); IsPickedup
        -- ----------------------------------------------------- view_orderdetails_core
    }
    view_orderdetails_core {
        (`ID` INT view_orderdetails_core
        INT OrderID
        INT CustomerID
        INT SerialNumber
        INT InventoryItemID
        INT PriceCodeID
        INT SaleRentType
        INT SerialID
        INT BillablePrice
        INT AllowablePrice
        INT Taxable
        INT FlatRate
        INT DOSFrom
        INT DOSTo
        INT PickupDate
        INT ShowSpanDates
        INT OrderedQuantity
        INT OrderedUnits
        INT OrderedWhen
        INT OrderedConverter
        INT BilledQuantity
        INT BilledUnits
        INT BilledWhen
        INT BilledConverter
        INT DeliveryQuantity
        INT DeliveryUnits
        INT DeliveryConverter
        INT BillingCode
        INT Modifier1
        INT Modifier2
        INT Modifier3
        INT Modifier4
        INT DXPointer
        INT BillingMonth
        INT BillItemOn
        INT AuthorizationNumber
        INT AuthorizationTypeID
        INT ReasonForPickup
        INT SendCMN_RX_w_invoice
        INT MedicallyUnnecessary
        INT Sale
        INT SpecialCode
        INT ReviewCode
        INT NextOrderID
        INT ReoccuringID
        INT CMNFormID
        INT HAOCode
        INT State
        INT BillIns1
        INT BillIns2
        INT BillIns3
        INT BillIns4
        INT EndDate
        INT MIR
        INT NextBillingDate
        INT WarehouseID
        INT AcceptAssignment
        INT DrugNoteField
        INT DrugControlNumber
        INT NopayIns1
        INT PointerICD10
        INT DXPointer10
        INT HaoDescription
        INT UserField1
        INT UserField2
        INT AuthorizationExpirationDate
        INT IsActive
        INT IsCanceled
        INT IsSold
        INT IsRented
        INT ActualSaleRentType
        INT ActualBillItemOn
        INT ActualOrderedWhen
        INT ActualBilledWhen
        INT ActualDosTo
        INT InvoiceDate
        INT IsOxygen
        INT); IsZeroAmount
        -- ----------------------------------------------------- view_pricecode
    }
    view_pricecode {
        (`ID` INT view_pricecode
        INT Name
        INT); IsRetail
        -- ----------------------------------------------------- view_reoccuringlist
    }
    view_reoccuringlist {
        (`OrderID` INT view_reoccuringlist
        INT BilledWhen
        INT); BillItemOn
        -- ----------------------------------------------------- view_sequence
    }
    view_sequence {
        (`num` INT); view_sequence
        -- ----------------------------------------------------- view_sequence_core
    }
    view_sequence_core {
        (`num` INT); view_sequence_core
        -- ----------------------------------------------------- view_taxrate
    }
    view_taxrate {
        (`ID` INT view_taxrate
        INT CityTax
        INT CountyTax
        INT Name
        INT OtherTax
        INT StateTax
        INT LastUpdateUserID
        INT LastUpdateDatetime
        INT); TotalTax
    }
    tbl_deposits ||--otbl_order : references
    tbl_orderdetails ||--otbl_order : references
    tbl_orderdetails ||--otbl_order : references
    tbl_depositdetails ||--otbl_deposits : references
    tbl_depositdetails ||--otbl_orderdetails : references
    tbl_invoice ||--otbl_order : references
    tbl_invoicedetails ||--otbl_invoice : references
    tbl_invoice_transaction ||--otbl_invoicedetails : references
    tbl_orderdeposits ||--otbl_order : references
    tbl_orderdeposits ||--otbl_orderdetails : references
```
