"""
Price Calculation Service for PriceUtilities Module.
Handles all price-related calculations and validations.
"""
from typing import Dict, List, Optional, Union
from decimal import Decimal
from datetime import datetime

from ..models.price_list import PriceList
from ..models.parameters import Parameter
from ..models.icd_codes import ICDCode
from ..repositories.price_list import PriceListRepository
from ..repositories.parameters import ParameterRepository
from ..repositories.icd_codes import ICDCodeRepository

class PriceCalculationService:
    """Service for handling all price calculations and related operations"""
    
    def __init__(
        self,
        price_list_repo: PriceListRepository,
        parameter_repo: ParameterRepository,
        icd_code_repo: ICDCodeRepository
    ):
        self.price_list_repo = price_list_repo
        self.parameter_repo = parameter_repo
        self.icd_code_repo = icd_code_repo
        
    def calculate_price(
        self,
        item_id: str,
        quantity: int,
        icd_codes: List[str],
        date: Optional[datetime] = None
    ) -> Dict[str, Union[Decimal, str]]:
        """
        Calculate final price for an item based on various factors
        
        Args:
            item_id: Unique identifier for the item
            quantity: Number of items
            icd_codes: List of ICD codes applicable
            date: Optional date for historical pricing
            
        Returns:
            Dictionary containing calculated price and breakdown
        """
        # Get base price
        price_list_item = self.price_list_repo.get_by_id(item_id)
        if not price_list_item:
            raise ValueError(f"Item {item_id} not found")
            
        # Apply quantity discounts
        base_price = self._apply_quantity_discount(
            price_list_item.base_price,
            quantity,
            price_list_item.quantity_breaks
        )
        
        # Apply ICD code modifiers
        icd_adjusted_price = self._apply_icd_modifiers(
            base_price,
            icd_codes
        )
        
        # Apply date-specific parameters
        final_price = self._apply_date_parameters(
            icd_adjusted_price,
            date or datetime.now()
        )
        
        return {
            'base_price': base_price,
            'icd_adjusted_price': icd_adjusted_price,
            'final_price': final_price,
            'currency': price_list_item.currency,
            'calculation_date': date.isoformat() if date else datetime.now().isoformat()
        }
        
    def _apply_quantity_discount(
        self,
        base_price: Decimal,
        quantity: int,
        quantity_breaks: Dict[int, Decimal]
    ) -> Decimal:
        """Apply quantity-based discounts to base price"""
        if not quantity_breaks:
            return base_price * quantity
            
        applicable_discount = Decimal('0')
        for break_point, discount in sorted(quantity_breaks.items(), reverse=True):
            if quantity >= break_point:
                applicable_discount = discount
                break
                
        return (base_price * quantity) * (1 - applicable_discount)
        
    def _apply_icd_modifiers(
        self,
        price: Decimal,
        icd_codes: List[str]
    ) -> Decimal:
        """Apply ICD code-specific price modifiers"""
        modifier = Decimal('1.0')
        for code in icd_codes:
            icd_item = self.icd_code_repo.get_by_code(code)
            if icd_item and icd_item.price_modifier:
                modifier *= icd_item.price_modifier
        
        return price * modifier
        
    def _apply_date_parameters(
        self,
        price: Decimal,
        date: datetime
    ) -> Decimal:
        """Apply date-specific parameters to price"""
        parameters = self.parameter_repo.get_active_parameters(date)
        
        for param in parameters:
            if param.parameter_type == 'MULTIPLIER':
                price *= Decimal(str(param.value))
            elif param.parameter_type == 'FIXED_ADDITION':
                price += Decimal(str(param.value))
                
        return price.quantize(Decimal('0.01'))
