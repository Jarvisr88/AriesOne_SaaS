"""
Billing Calculation Service Module

This module handles core billing calculations for the DME/HME system, including
allowable amounts, multipliers, and billing period calculations.
"""

from decimal import Decimal
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum

class SaleRentType(str, Enum):
    """Enumeration of sale and rental types"""
    ONE_TIME_SALE = "One Time Sale"
    REOCCURRING_SALE = "Re-occurring Sale"
    ONE_TIME_RENTAL = "One Time Rental"
    MEDICARE_OXYGEN_RENTAL = "Medicare Oxygen Rental"
    MONTHLY_RENTAL = "Monthly Rental"
    RENT_TO_PURCHASE = "Rent to Purchase"
    CAPPED_RENTAL = "Capped Rental"
    PARENTAL_CAPPED_RENTAL = "Parental Capped Rental"

class BillingFrequency(str, Enum):
    """Enumeration of billing frequencies"""
    ONE_TIME = "One Time"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

class InvoiceModifierType(str, Enum):
    """Types of invoice modifiers that can be applied"""
    STANDARD = "standard"
    INSURANCE = "insurance"
    MEDICARE = "medicare"
    MEDICAID = "medicaid"
    WORKERS_COMP = "workers_comp"
    CASH = "cash"

class InvoiceModifier:
    """Represents an invoice modifier with its rules"""
    def __init__(
        self,
        modifier_type: InvoiceModifierType,
        multiplier: Decimal,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        rules: Optional[Dict] = None
    ):
        self.type = modifier_type
        self.multiplier = multiplier
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.start_date = start_date
        self.end_date = end_date
        self.rules = rules or {}

class QuantityRule:
    """Represents a quantity-based pricing rule"""
    def __init__(
        self,
        min_quantity: int,
        max_quantity: Optional[int],
        multiplier: Decimal,
        flat_rate: Optional[Decimal] = None
    ):
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.multiplier = multiplier
        self.flat_rate = flat_rate

    def applies_to(self, quantity: int) -> bool:
        """Check if this rule applies to the given quantity"""
        if quantity < self.min_quantity:
            return False
        if self.max_quantity is not None and quantity > self.max_quantity:
            return False
        return True

class BillingCalculator:
    """Handles core billing calculations for DME/HME items"""

    @staticmethod
    def get_allowable_amount(
        sale_rent_type: SaleRentType,
        billing_month: int,
        price: Decimal,
        quantity: int,
        sale_price: Optional[Decimal] = None,
        flat_rate: bool = False
    ) -> Decimal:
        """
        Calculate the allowable amount based on sale/rent type and billing parameters.
        
        Args:
            sale_rent_type: Type of sale or rental
            billing_month: Current billing month (1-based)
            price: Base price for the item
            quantity: Quantity being billed
            sale_price: Sale price for rent-to-purchase items
            flat_rate: If True, quantity is set to 1
            
        Returns:
            Decimal: Calculated allowable amount
        """
        # Input validation and normalization
        billing_month = max(1, billing_month)
        if flat_rate:
            quantity = 1

        # One-time charges
        if sale_rent_type in [
            SaleRentType.ONE_TIME_SALE,
            SaleRentType.REOCCURRING_SALE,
            SaleRentType.ONE_TIME_RENTAL
        ]:
            if billing_month == 1:
                return price * Decimal(quantity)
            return Decimal('0.00')

        # Regular rentals
        if sale_rent_type in [
            SaleRentType.MEDICARE_OXYGEN_RENTAL,
            SaleRentType.MONTHLY_RENTAL
        ]:
            return price * Decimal(quantity)

        # Rent to purchase
        if sale_rent_type == SaleRentType.RENT_TO_PURCHASE:
            if billing_month <= 9:
                return price * Decimal(quantity)
            elif billing_month == 10 and sale_price is not None:
                return (sale_price - (9 * price)) * Decimal(quantity)
            return Decimal('0.00')

        # Capped rental
        if sale_rent_type == SaleRentType.CAPPED_RENTAL:
            if billing_month <= 3:
                return price * Decimal(quantity)
            elif billing_month <= 15:
                return Decimal('0.75') * price * Decimal(quantity)
            elif billing_month >= 22 and (billing_month - 22) % 6 == 0:
                return price * Decimal(quantity)
            return Decimal('0.00')

        # Parental capped rental
        if sale_rent_type == SaleRentType.PARENTAL_CAPPED_RENTAL:
            if billing_month <= 15:
                return price * Decimal(quantity)
            elif billing_month >= 22 and (billing_month - 22) % 6 == 0:
                return price * Decimal(quantity)
            return Decimal('0.00')

        return Decimal('0.00')

    @staticmethod
    def get_amount_multiplier(
        dos_from: datetime,
        dos_to: datetime,
        end_date: Optional[datetime],
        sale_rent_type: SaleRentType,
        ordered_when: BillingFrequency,
        billed_when: BillingFrequency
    ) -> Decimal:
        """
        Calculate the billing amount multiplier based on dates and frequencies.
        
        Args:
            dos_from: Start date of service
            dos_to: End date of service
            end_date: Optional end date (for terminated services)
            sale_rent_type: Type of sale or rental
            ordered_when: Frequency of ordering
            billed_when: Frequency of billing
            
        Returns:
            Decimal: Calculated multiplier for the billing amount
        """
        # One-time items always have multiplier of 1
        if sale_rent_type in [
            SaleRentType.ONE_TIME_SALE,
            SaleRentType.REOCCURRING_SALE,
            SaleRentType.ONE_TIME_RENTAL
        ]:
            return Decimal('1')

        # Handle terminated services
        if end_date and end_date < dos_to:
            dos_to = end_date

        # Same frequency billing
        if ordered_when == billed_when:
            return Decimal('1')

        # Calculate days between dates
        days_diff = (dos_to - dos_from).days + 1
        
        # Convert to appropriate multiplier based on frequencies
        if billed_when == BillingFrequency.MONTHLY:
            if ordered_when == BillingFrequency.DAILY:
                return Decimal(str(days_diff))
            elif ordered_when == BillingFrequency.WEEKLY:
                return Decimal(str(days_diff / 7)).quantize(Decimal('0.0001'))
            
        elif billed_when == BillingFrequency.WEEKLY:
            if ordered_when == BillingFrequency.DAILY:
                return Decimal(str(days_diff))
                
        elif billed_when == BillingFrequency.DAILY:
            if ordered_when in [BillingFrequency.WEEKLY, BillingFrequency.MONTHLY]:
                return Decimal('1') / Decimal(str(days_diff))

        return Decimal('1')

    @staticmethod
    def get_billable_amount(
        sale_rent_type: SaleRentType,
        billing_month: int,
        price: Decimal,
        quantity: int,
        sale_price: Optional[Decimal] = None,
        flat_rate: bool = False,
        tax_rate: Optional[Decimal] = None,
        discount_percent: Optional[Decimal] = None
    ) -> Decimal:
        """
        Calculate the billable amount based on sale/rent type and billing parameters.
        
        Args:
            sale_rent_type: Type of sale or rental
            billing_month: Current billing month (1-based)
            price: Base price for the item
            quantity: Quantity being billed
            sale_price: Sale price for rent-to-purchase items
            flat_rate: If True, quantity is set to 1
            tax_rate: Optional tax rate as decimal (e.g., 0.08 for 8%)
            discount_percent: Optional discount percentage (e.g., 10 for 10%)
            
        Returns:
            Decimal: Calculated billable amount including tax and discounts
        """
        # Input validation and normalization
        billing_month = max(1, billing_month)
        if flat_rate:
            quantity = 1

        # Calculate base amount using similar logic to allowable amount
        base_amount = Decimal('0.00')
        
        # One-time charges
        if sale_rent_type in [
            SaleRentType.ONE_TIME_SALE,
            SaleRentType.REOCCURRING_SALE,
            SaleRentType.ONE_TIME_RENTAL
        ]:
            if billing_month == 1:
                base_amount = price * Decimal(quantity)

        # Regular rentals
        elif sale_rent_type in [
            SaleRentType.MEDICARE_OXYGEN_RENTAL,
            SaleRentType.MONTHLY_RENTAL
        ]:
            base_amount = price * Decimal(quantity)

        # Rent to purchase
        elif sale_rent_type == SaleRentType.RENT_TO_PURCHASE:
            if billing_month <= 9:
                base_amount = price * Decimal(quantity)
            elif billing_month == 10 and sale_price is not None:
                base_amount = (sale_price - (9 * price)) * Decimal(quantity)

        # Capped rental
        elif sale_rent_type == SaleRentType.CAPPED_RENTAL:
            if billing_month <= 3:
                base_amount = price * Decimal(quantity)
            elif billing_month <= 15:
                base_amount = Decimal('0.75') * price * Decimal(quantity)
            elif billing_month >= 22 and (billing_month - 22) % 6 == 0:
                base_amount = price * Decimal(quantity)

        # Parental capped rental
        elif sale_rent_type == SaleRentType.PARENTAL_CAPPED_RENTAL:
            if billing_month <= 15:
                base_amount = price * Decimal(quantity)
            elif billing_month >= 22 and (billing_month - 22) % 6 == 0:
                base_amount = price * Decimal(quantity)

        # Apply discount if provided
        if discount_percent is not None and discount_percent > 0:
            discount_multiplier = (100 - discount_percent) / Decimal('100')
            base_amount *= discount_multiplier

        # Apply tax if provided and amount is positive
        if tax_rate is not None and base_amount > 0:
            tax_multiplier = 1 + tax_rate
            base_amount *= tax_multiplier

        return base_amount.quantize(Decimal('0.01'))

    @staticmethod
    def get_invoice_modifier(
        base_amount: Decimal,
        modifier_type: InvoiceModifierType,
        service_date: datetime,
        modifiers: List[InvoiceModifier],
        customer_type: Optional[str] = None,
        insurance_type: Optional[str] = None,
        state: Optional[str] = None
    ) -> Decimal:
        """
        Calculate the invoice modifier amount based on various business rules.
        
        Args:
            base_amount: Original invoice amount
            modifier_type: Type of modifier to apply
            service_date: Date of service
            modifiers: List of available modifiers
            customer_type: Optional customer classification
            insurance_type: Optional insurance type
            state: Optional state code for state-specific rules
            
        Returns:
            Decimal: Modified amount after applying rules
        """
        applicable_modifiers = [
            mod for mod in modifiers
            if mod.type == modifier_type
            and (mod.start_date is None or mod.start_date <= service_date)
            and (mod.end_date is None or service_date <= mod.end_date)
        ]

        if not applicable_modifiers:
            return base_amount

        # Sort by most restrictive first (those with more rules)
        applicable_modifiers.sort(key=lambda x: len(x.rules or {}), reverse=True)
        
        for modifier in applicable_modifiers:
            # Check if all rules match
            rules_match = True
            
            if modifier.rules:
                if customer_type and modifier.rules.get('customer_type'):
                    if customer_type not in modifier.rules['customer_type']:
                        rules_match = False
                        
                if insurance_type and modifier.rules.get('insurance_type'):
                    if insurance_type not in modifier.rules['insurance_type']:
                        rules_match = False
                        
                if state and modifier.rules.get('state'):
                    if state not in modifier.rules['state']:
                        rules_match = False
            
            if rules_match:
                modified_amount = base_amount * modifier.multiplier
                
                # Apply min/max constraints if present
                if modifier.min_amount is not None:
                    modified_amount = max(modified_amount, modifier.min_amount)
                if modifier.max_amount is not None:
                    modified_amount = min(modified_amount, modifier.max_amount)
                
                return modified_amount.quantize(Decimal('0.01'))
        
        return base_amount

    @staticmethod
    def get_multiplier(
        frequency: BillingFrequency,
        from_date: datetime,
        to_date: datetime,
        end_date: Optional[datetime] = None,
        prorate: bool = True,
        round_method: str = 'floor'
    ) -> Decimal:
        """
        Calculate a general-purpose multiplier based on frequency and date ranges.
        
        Args:
            frequency: Billing frequency (daily, weekly, monthly)
            from_date: Start date of the period
            to_date: End date of the period
            end_date: Optional end date for early termination
            prorate: If True, calculate partial periods
            round_method: How to round partial periods ('floor', 'ceil', 'round')
            
        Returns:
            Decimal: Calculated multiplier for the period
        """
        # Handle early termination
        if end_date and end_date < to_date:
            to_date = end_date

        # Ensure dates are in correct order
        if from_date > to_date:
            return Decimal('0')

        # One-time items always have multiplier of 1
        if frequency == BillingFrequency.ONE_TIME:
            return Decimal('1')

        # Calculate the total days in the period
        days_diff = (to_date - from_date).days + 1

        if frequency == BillingFrequency.DAILY:
            return Decimal(str(days_diff))

        if frequency == BillingFrequency.WEEKLY:
            if not prorate:
                # Round to nearest week
                weeks = days_diff / 7
                if round_method == 'floor':
                    return Decimal(str(int(weeks)))
                elif round_method == 'ceil':
                    return Decimal(str(int(weeks + 0.99)))
                else:  # round
                    return Decimal(str(round(weeks)))
            else:
                # Calculate exact weeks including partial
                return Decimal(str(days_diff / 7)).quantize(Decimal('0.0001'))

        if frequency == BillingFrequency.MONTHLY:
            # Calculate months between dates
            months = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)
            
            if not prorate:
                # Add 1 if we're past the start day in the final month
                if to_date.day >= from_date.day:
                    months += 1
                if round_method == 'floor':
                    return Decimal(str(months))
                elif round_method == 'ceil':
                    return Decimal(str(months + 1))
                else:  # round
                    # Add 0.5 if we're halfway through the month
                    if to_date.day >= 15:
                        months += 1
                    return Decimal(str(months))
            else:
                # Calculate exact months including partial
                days_in_month = (to_date.replace(day=1) - from_date.replace(day=1)).days
                if days_in_month == 0:
                    return Decimal('1')
                    
                partial = Decimal(str(days_diff)) / Decimal(str(days_in_month))
                return partial.quantize(Decimal('0.0001'))

        return Decimal('0')

    @staticmethod
    def get_quantity_multiplier(
        quantity: int,
        rules: List[QuantityRule],
        base_amount: Optional[Decimal] = None,
        allow_flat_rate: bool = True
    ) -> Decimal:
        """
        Calculate a multiplier based on quantity rules.
        
        Args:
            quantity: Number of items
            rules: List of quantity pricing rules
            base_amount: Original amount (needed for flat rate calculations)
            allow_flat_rate: Whether to allow flat rate pricing
            
        Returns:
            Decimal: Calculated multiplier based on quantity
        """
        if quantity <= 0:
            return Decimal('0')

        # Sort rules by min_quantity descending to get most specific rule first
        sorted_rules = sorted(rules, key=lambda x: x.min_quantity, reverse=True)
        
        for rule in sorted_rules:
            if rule.applies_to(quantity):
                # Handle flat rate if allowed and present
                if allow_flat_rate and rule.flat_rate is not None and base_amount:
                    # Calculate equivalent multiplier for flat rate
                    if base_amount > Decimal('0'):
                        return (rule.flat_rate / base_amount).quantize(Decimal('0.0001'))
                    return Decimal('0')
                
                # Apply standard multiplier
                return rule.multiplier.quantize(Decimal('0.0001'))
        
        # If no rules match, use quantity as direct multiplier
        return Decimal(str(quantity)).quantize(Decimal('0.0001'))
