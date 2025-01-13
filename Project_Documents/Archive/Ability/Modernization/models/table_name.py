"""
Table Name Models Module

This module provides models and enums for database table names.
"""
from enum import Enum
from typing import Dict, Optional, ClassVar
from pydantic import BaseModel, Field
from datetime import datetime

class TableCategory(str, Enum):
    """Categories of database tables"""
    ABILITY = "ability"
    AUTHORIZATION = "authorization"
    BILLING = "billing"
    CMN_FORM = "cmn_form"
    COMPANY = "company"
    COMPLIANCE = "compliance"
    CUSTOMER = "customer"
    DOCTOR = "doctor"
    ELIGIBILITY = "eligibility"
    FACILITY = "facility"
    INSURANCE = "insurance"
    INVENTORY = "inventory"
    INVOICE = "invoice"
    KIT = "kit"
    LOCATION = "location"
    MEDICAL = "medical"
    ORDER = "order"
    PAYMENT = "payment"
    PERMISSION = "permission"
    PREDEFINED = "predefined"
    PRICE = "price"
    PROVIDER = "provider"
    PURCHASE = "purchase"
    REPORT = "report"
    SERIAL = "serial"
    SHIPPING = "shipping"
    USER = "user"
    VENDOR = "vendor"

class TableName(str, Enum):
    """Enumeration of all database table names"""
    # Ability tables
    ABILITY_ELIGIBILITY_PAYER = "tbl_ability_eligibility_payer"
    ABILITY_ELIGIBILITY_REQUEST = "tbl_ability_eligibility_request"
    
    # Authorization tables
    AUTHORIZATION_TYPE = "tbl_authorizationtype"
    
    # Billing tables
    BATCH = "tbl_batch"
    BILLING_TYPE = "tbl_billingtype"
    
    # CMN Form tables
    CMN_FORM = "tbl_cmnform"
    CMN_FORM_0102A = "tbl_cmnform_0102a"
    CMN_FORM_0102B = "tbl_cmnform_0102b"
    CMN_FORM_0203A = "tbl_cmnform_0203a"
    CMN_FORM_0203B = "tbl_cmnform_0203b"
    CMN_FORM_0302 = "tbl_cmnform_0302"
    CMN_FORM_0403B = "tbl_cmnform_0403b"
    CMN_FORM_0403C = "tbl_cmnform_0403c"
    CMN_FORM_0602B = "tbl_cmnform_0602b"
    CMN_FORM_0702A = "tbl_cmnform_0702a"
    CMN_FORM_0702B = "tbl_cmnform_0702b"
    CMN_FORM_0902 = "tbl_cmnform_0902"
    CMN_FORM_1002A = "tbl_cmnform_1002a"
    CMN_FORM_1002B = "tbl_cmnform_1002b"
    CMN_FORM_4842 = "tbl_cmnform_4842"
    CMN_FORM_DETAILS = "tbl_cmnform_details"
    CMN_FORM_DRORDER = "tbl_cmnform_drorder"
    CMN_FORM_URO = "tbl_cmnform_uro"
    
    # Company tables
    COMPANY = "tbl_company"
    
    # Compliance tables
    COMPLIANCE = "tbl_compliance"
    COMPLIANCE_ITEMS = "tbl_compliance_items"
    COMPLIANCE_NOTES = "tbl_compliance_notes"
    
    # Customer tables
    CUSTOMER = "tbl_customer"
    CUSTOMER_INSURANCE = "tbl_customer_insurance"
    CUSTOMER_NOTES = "tbl_customer_notes"
    CUSTOMER_CLASS = "tbl_customerclass"
    CUSTOMER_TYPE = "tbl_customertype"
    
    # Doctor tables
    DOCTOR = "tbl_doctor"
    DOCTOR_TYPE = "tbl_doctortype"
    
    # Eligibility tables
    ELIGIBILITY_REQUEST = "tbl_eligibilityrequest"
    
    # Facility tables
    FACILITY = "tbl_facility"
    HAO = "tbl_hao"
    
    # Medical tables
    ICD9 = "tbl_icd9"
    ICD10 = "tbl_icd10"
    MEDICAL_CONDITIONS = "tbl_medicalconditions"
    
    # Insurance tables
    INSURANCE_COMPANY = "tbl_insurancecompany"
    INSURANCE_COMPANY_GROUP = "tbl_insurancecompanygroup"
    INSURANCE_COMPANY_TYPE = "tbl_insurancecompanytype"
    INSURANCE_TYPE = "tbl_insurancetype"
    
    # Inventory tables
    INVENTORY = "tbl_inventory"
    INVENTORY_TRANSACTION = "tbl_inventory_transaction"
    INVENTORY_TRANSACTION_TYPE = "tbl_inventory_transaction_type"
    INVENTORY_ITEM = "tbl_inventoryitem"
    INVENTORY_CODE = "tbl_inventorycode"
    
    # Invoice tables
    INVOICE = "tbl_invoice"
    INVOICE_DETAILS = "tbl_invoicedetails"
    INVOICE_NOTES = "tbl_invoicenotes"
    INVOICE_FORM = "tbl_invoiceform"
    INVOICE_TRANSACTION = "tbl_invoice_transaction"
    INVOICE_TRANSACTION_TYPE = "tbl_invoice_transactiontype"
    
    # Kit tables
    KIT = "tbl_kit"
    KIT_DETAILS = "tbl_kitdetails"
    
    # Location tables
    LEGAL_REP = "tbl_legalrep"
    LOCATION = "tbl_location"
    
    # Manufacturer tables
    MANUFACTURER = "tbl_manufacturer"
    
    # Object tables
    OBJECT = "tbl_object"
    
    # Order tables
    ORDER = "tbl_order"
    ORDER_DETAILS = "tbl_orderdetails"
    
    # Payment tables
    PAYMENT = "tbl_payment"
    PAYMENT_PLAN = "tbl_paymentplan"
    
    # Permission tables
    PERMISSIONS = "tbl_permissions"
    POS_TYPE = "tbl_postype"
    
    # Predefined text tables
    PREDEFINED_TEXT = "tbl_predefinedtext"
    PREDEFINED_TEXT_COMPLIANCE_NOTES = "tbl_predefinedtext_compliancenotes"
    PREDEFINED_TEXT_CUSTOMER_NOTES = "tbl_predefinedtext_customernotes"
    PREDEFINED_TEXT_INVOICE_NOTES = "tbl_predefinedtext_invoicenotes"
    
    # Price tables
    PRICE_CODE = "tbl_pricecode"
    PRICE_CODE_ITEM = "tbl_pricecode_item"
    PRODUCT_TYPE = "tbl_producttype"
    
    # Provider tables
    PROVIDER = "tbl_provider"
    PROVIDER_NUMBER_TYPE = "tbl_providernumbertype"
    
    # Purchase tables
    PURCHASE_ORDER = "tbl_purchaseorder"
    PURCHASE_ORDER_DETAILS = "tbl_purchaseorderdetails"
    
    # Report tables
    CRYSTAL_REPORT = "tbl_crystalreport"
    
    # Serial tables
    SERIAL = "tbl_serial"
    SERIAL_MAINTENANCE = "tbl_serial_maintenance"
    SERIAL_TRANSACTION = "tbl_serial_transaction"
    SERIAL_TRANSACTION_TYPE = "tbl_serial_transaction_type"
    SESSIONS = "tbl_sessions"
    
    # Shipping tables
    SHIPPING_METHOD = "tbl_shippingmethod"
    SIGNATURE_TYPE = "tbl_signaturetype"
    UPS_SHIPPING_BILLING_OPTION = "tbl_upsshipping_billingoption"
    UPS_SHIPPING_FREIGHT_CLASS = "tbl_upsshipping_freightclass"
    UPS_SHIPPING_PACKAGING_TYPE = "tbl_upsshipping_packagingtype"
    
    # Tax tables
    TAX_RATE = "tbl_taxrate"
    
    # User tables
    USER = "tbl_user"
    USER_LOCATION = "tbl_user_location"
    
    # Variables tables
    VARIABLES = "tbl_variables"
    
    # Vendor tables
    VENDOR = "tbl_vendor"
    WAREHOUSE = "tbl_warehouse"
    ZIPCODE = "tbl_zipcode"

class TableMetadata(BaseModel):
    """Model for table metadata"""
    name: TableName
    category: TableCategory
    description: Optional[str] = None
    schema_version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True

class TableRegistry:
    """Registry for table metadata"""
    _registry: ClassVar[Dict[TableName, TableMetadata]] = {}
    
    @classmethod
    def register(cls, metadata: TableMetadata):
        """Register table metadata"""
        cls._registry[metadata.name] = metadata
    
    @classmethod
    def get(cls, table_name: TableName) -> Optional[TableMetadata]:
        """Get table metadata"""
        return cls._registry.get(table_name)
    
    @classmethod
    def normalize(cls, table_name: str) -> str:
        """
        Normalize table name.
        
        Args:
            table_name: Table name to normalize
            
        Returns:
            Normalized table name
            
        Raises:
            ValueError: If table name is None
        """
        if table_name is None:
            raise ValueError("Table name cannot be None")
        
        try:
            # Try to convert to enum and get value
            return TableName(table_name).value
        except ValueError:
            # If not a valid enum value, return as is
            return table_name

# Initialize table metadata
def initialize_table_metadata():
    """Initialize table metadata in registry"""
    # Ability tables
    TableRegistry.register(TableMetadata(
        name=TableName.ABILITY_ELIGIBILITY_PAYER,
        category=TableCategory.ABILITY,
        description="Stores ability eligibility payer information"
    ))
    TableRegistry.register(TableMetadata(
        name=TableName.ABILITY_ELIGIBILITY_REQUEST,
        category=TableCategory.ABILITY,
        description="Stores ability eligibility request information"
    ))
    
    # Authorization tables
    TableRegistry.register(TableMetadata(
        name=TableName.AUTHORIZATION_TYPE,
        category=TableCategory.AUTHORIZATION,
        description="Stores authorization type information"
    ))
    
    # Add more table metadata as needed...
