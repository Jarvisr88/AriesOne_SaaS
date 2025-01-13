"""
Medical views module for handling various medical-related data views
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class AbilityEligibilityPayer:
    """Ability eligibility payer data"""
    id: int
    code: str
    name: str
    comments: Optional[str]
    search_options: Optional[str]
    allows_submission: bool

@dataclass
class Doctor:
    """Doctor information"""
    id: int
    first_name: str
    middle_name: Optional[str]
    last_name: str
    title: Optional[str]
    suffix: Optional[str]
    courtesy: Optional[str]
    type_id: int
    license_number: Optional[str]
    license_expired: Optional[datetime]
    medicaid_number: Optional[str]
    upin_number: Optional[str]
    fed_tax_id: Optional[str]
    dea_number: Optional[str]
    npi: Optional[str]
    pecos_enrolled: bool
    mir: Optional[str]
    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    phone: Optional[str]
    phone2: Optional[str]
    fax: Optional[str]
    contact: Optional[str]
    last_update_user_id: int
    last_update_datetime: datetime

@dataclass
class DoctorType:
    """Doctor type information"""
    id: int
    name: str
    last_update_user_id: int
    last_update_datetime: datetime

@dataclass
class ICD10:
    """ICD-10 code information"""
    code: str
    description: str
    header: bool
    active_date: datetime
    inactive_date: Optional[datetime]
    last_update_user_id: int
    last_update_datetime: datetime

@dataclass
class ICD9:
    """ICD-9 code information"""
    code: str
    description: str
    active_date: datetime
    inactive_date: Optional[datetime]
    last_update_user_id: int
    last_update_datetime: datetime

@dataclass
class InsuranceCompany:
    """Insurance company information"""
    id: int
    name: str
    type: str
    group_id: Optional[int]
    basis: Optional[str]
    expected_percent: Optional[Decimal]
    price_code_id: Optional[int]
    print_hao_on_invoice: bool
    print_inv_on_invoice: bool
    invoice_form_id: Optional[int]
    medicare_number: Optional[str]
    medicaid_number: Optional[str]
    office_ally_number: Optional[str]
    zirmed_number: Optional[str]
    availity_number: Optional[str]
    ability_number: Optional[str]
    ability_eligibility_payer_id: Optional[int]
    mir: Optional[str]
    address1: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    phone: Optional[str]
    phone2: Optional[str]
    fax: Optional[str]
    contact: Optional[str]
    title: Optional[str]
    last_update_user_id: int
    last_update_datetime: datetime

@dataclass
class InsuranceCompanyGroup:
    """Insurance company group information"""
    id: int
    name: str
    last_update_user_id: int
    last_update_datetime: datetime

@dataclass
class InsuranceCompanyType:
    """Insurance company type information"""
    id: int
    name: str

@dataclass
class ZipCode:
    """Zip code information"""
    zip: str
    state: str
    city: str
