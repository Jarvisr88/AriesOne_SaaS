"""
Validation Service for PriceUtilities Module.
Handles all validation logic for price-related operations.
"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
import re
from datetime import datetime

from ..models.price_list import PriceList
from ..models.parameters import Parameter
from ..models.icd_codes import ICDCode
from ..repositories.price_list import PriceListRepository
from ..repositories.parameters import ParameterRepository
from ..repositories.icd_codes import ICDCodeRepository

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class ValidationService:
    """Service for handling all validation operations"""
    
    def __init__(
        self,
        price_list_repo: PriceListRepository,
        parameter_repo: ParameterRepository,
        icd_code_repo: ICDCodeRepository
    ):
        self.price_list_repo = price_list_repo
        self.parameter_repo = parameter_repo
        self.icd_code_repo = icd_code_repo
        
    async def validate_price_update(
        self,
        update_data: Dict[str, Any]
    ) -> None:
        """
        Validate a price update operation
        
        Args:
            update_data: Dictionary containing update information
            
        Raises:
            ValidationError: If validation fails
        """
        required_fields = ['item_id', 'base_price']
        self._validate_required_fields(update_data, required_fields)
        
        # Validate price format and range
        self._validate_price(update_data.get('base_price'))
        
        # Validate quantity breaks if present
        if 'quantity_breaks' in update_data:
            self._validate_quantity_breaks(update_data['quantity_breaks'])
            
        # Validate currency if present
        if 'currency' in update_data:
            self._validate_currency(update_data['currency'])
            
        # Validate effective dates if present
        if 'effective_date' in update_data:
            self._validate_effective_date(update_data['effective_date'])
            
        # Validate ICD codes if present
        if 'icd_codes' in update_data:
            await self._validate_icd_codes(update_data['icd_codes'])
            
    def _validate_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> None:
        """Validate presence of required fields"""
        missing_fields = [
            field for field in required_fields
            if field not in data or data[field] is None
        ]
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
            
    def _validate_price(self, price: Any) -> None:
        """Validate price format and range"""
        try:
            price_decimal = Decimal(str(price))
        except (TypeError, ValueError, decimal.InvalidOperation):
            raise ValidationError("Invalid price format")
            
        if price_decimal < 0:
            raise ValidationError("Price cannot be negative")
            
        if price_decimal > Decimal('999999999.99'):
            raise ValidationError("Price exceeds maximum allowed value")
            
    def _validate_quantity_breaks(
        self,
        quantity_breaks: Dict[int, Decimal]
    ) -> None:
        """Validate quantity break structure and values"""
        if not isinstance(quantity_breaks, dict):
            raise ValidationError("Quantity breaks must be a dictionary")
            
        for quantity, discount in quantity_breaks.items():
            try:
                quantity_int = int(quantity)
                discount_decimal = Decimal(str(discount))
            except (TypeError, ValueError, decimal.InvalidOperation):
                raise ValidationError(
                    "Invalid quantity break format"
                )
                
            if quantity_int < 1:
                raise ValidationError(
                    "Quantity break threshold must be positive"
                )
                
            if not 0 <= discount_decimal <= 1:
                raise ValidationError(
                    "Discount must be between 0 and 1"
                )
                
    def _validate_currency(self, currency: str) -> None:
        """Validate currency code"""
        currency_pattern = re.compile(r'^[A-Z]{3}$')
        if not currency_pattern.match(currency):
            raise ValidationError(
                "Invalid currency code format"
            )
            
    def _validate_effective_date(
        self,
        effective_date: str
    ) -> None:
        """Validate effective date format and range"""
        try:
            date = datetime.fromisoformat(effective_date)
        except ValueError:
            raise ValidationError(
                "Invalid date format. Use ISO format"
            )
            
        if date < datetime.now():
            raise ValidationError(
                "Effective date cannot be in the past"
            )
            
    async def _validate_icd_codes(
        self,
        icd_codes: List[str]
    ) -> None:
        """Validate ICD codes existence and format"""
        if not isinstance(icd_codes, list):
            raise ValidationError("ICD codes must be a list")
            
        for code in icd_codes:
            if not await self.icd_code_repo.get_by_code(code):
                raise ValidationError(
                    f"Invalid ICD code: {code}"
                )
                
    async def validate_parameter(
        self,
        parameter: Dict[str, Any]
    ) -> None:
        """Validate parameter data"""
        required_fields = ['name', 'value', 'parameter_type']
        self._validate_required_fields(parameter, required_fields)
        
        valid_types = ['MULTIPLIER', 'FIXED_ADDITION', 'PERCENTAGE']
        if parameter['parameter_type'] not in valid_types:
            raise ValidationError(
                f"Invalid parameter type. Must be one of: {', '.join(valid_types)}"
            )
            
        try:
            value = Decimal(str(parameter['value']))
        except (TypeError, ValueError, decimal.InvalidOperation):
            raise ValidationError("Invalid parameter value format")
