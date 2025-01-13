"""
System functions service layer for AriesOne SaaS application.
Implements core business logic functions for pricing, billing, and inventory calculations.
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

class SaleRentType(str, Enum):
    """Sale or rental type."""
    SALE = "Sale"
    RENTAL = "Rental"
    RENTAL_PURCHASE = "RentalPurchase"

class PriceCalculator:
    """Service for calculating prices and allowable amounts."""

    @staticmethod
    def get_allowable_amount(
        sale_rent_type: SaleRentType,
        billing_month: int,
        allowable_price: Decimal,
        billed_quantity: int,
        sale_allowable_price: Optional[Decimal] = None,
        flat_rate: Optional[Decimal] = None
    ) -> Decimal:
        """
        Calculate the allowable amount based on sale/rent type and billing parameters.
        
        Args:
            sale_rent_type: Type of transaction (Sale/Rental)
            billing_month: Month number for rental billing
            allowable_price: Base allowable price
            billed_quantity: Quantity being billed
            sale_allowable_price: Optional override price for sales
            flat_rate: Optional flat rate override
            
        Returns:
            Calculated allowable amount
        """
        if flat_rate is not None and flat_rate > 0:
            return flat_rate * billed_quantity

        if sale_rent_type == SaleRentType.SALE:
            base_price = sale_allowable_price if sale_allowable_price is not None else allowable_price
            return base_price * billed_quantity

        # Rental calculations
        rental_price = allowable_price
        if billing_month > 3:
            rental_price = rental_price * Decimal('0.75')  # 25% reduction after 3 months
        
        if sale_rent_type == SaleRentType.RENTAL_PURCHASE:
            # Apply rental purchase logic
            if billing_month > 10:
                return Decimal('0')  # No charge after 10 months
            rental_price = rental_price * Decimal('1.1')  # 10% premium for rental purchase

        return rental_price * billed_quantity

    @staticmethod
    def get_billing_amount(
        allowable_amount: Decimal,
        tax_rate: Optional[Decimal] = None,
        discount_percent: Optional[Decimal] = None,
        insurance_adjustment: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate final billing amount including taxes and adjustments.
        
        Args:
            allowable_amount: Base allowable amount
            tax_rate: Optional tax rate percentage
            discount_percent: Optional discount percentage
            insurance_adjustment: Optional insurance adjustment amount
            
        Returns:
            Dictionary containing subtotal, tax_amount, discount_amount,
            insurance_adjustment, and total_amount
        """
        subtotal = allowable_amount
        
        # Apply discount if any
        discount_amount = Decimal('0')
        if discount_percent:
            discount_amount = subtotal * (discount_percent / Decimal('100'))
            subtotal -= discount_amount

        # Calculate tax
        tax_amount = Decimal('0')
        if tax_rate:
            tax_amount = subtotal * (tax_rate / Decimal('100'))

        # Apply insurance adjustment
        adj_amount = Decimal('0')
        if insurance_adjustment:
            adj_amount = insurance_adjustment

        total_amount = subtotal + tax_amount - adj_amount

        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "discount_amount": discount_amount,
            "insurance_adjustment": adj_amount,
            "total_amount": total_amount
        }

class RentalCalculator:
    """Service for rental-specific calculations."""

    @staticmethod
    def calculate_rental_period(
        start_date: date,
        end_date: date,
        frequency: str
    ) -> Dict[str, Any]:
        """
        Calculate rental period details based on start and end dates.
        
        Args:
            start_date: Rental start date
            end_date: Rental end date
            frequency: Billing frequency (Monthly/Weekly/Daily)
            
        Returns:
            Dictionary containing period_count, billing_dates, and prorated_days
        """
        delta = end_date - start_date
        
        if frequency == "Monthly":
            # Calculate full months and prorated days
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            prorated_days = end_date.day - start_date.day
            
            if prorated_days < 0:
                months -= 1
                prorated_days += 30  # Assuming 30-day month for proration
            
            return {
                "period_count": months,
                "prorated_days": prorated_days,
                "billing_dates": [
                    start_date.replace(day=1) + relativedelta(months=i)
                    for i in range(months + 1)
                ]
            }
            
        elif frequency == "Weekly":
            weeks = delta.days // 7
            prorated_days = delta.days % 7
            
            return {
                "period_count": weeks,
                "prorated_days": prorated_days,
                "billing_dates": [
                    start_date + timedelta(weeks=i)
                    for i in range(weeks + 1)
                ]
            }
            
        else:  # Daily
            return {
                "period_count": delta.days,
                "prorated_days": 0,
                "billing_dates": [
                    start_date + timedelta(days=i)
                    for i in range(delta.days + 1)
                ]
            }

    @staticmethod
    def calculate_rental_rate(
        base_rate: Decimal,
        frequency: str,
        duration: int,
        is_purchase_option: bool = False
    ) -> Dict[str, Decimal]:
        """
        Calculate rental rates based on frequency and duration.
        
        Args:
            base_rate: Base rental rate
            frequency: Billing frequency (Monthly/Weekly/Daily)
            duration: Number of periods
            is_purchase_option: Whether this is a rental-purchase
            
        Returns:
            Dictionary containing calculated rates and purchase option details
        """
        rates = {
            "base_rate": base_rate,
            "adjusted_rate": base_rate,
            "purchase_option_amount": Decimal('0'),
            "total_cost": base_rate * duration
        }

        # Apply long-term rental discounts
        if frequency == "Monthly":
            if duration > 3:
                rates["adjusted_rate"] = base_rate * Decimal('0.75')
            if duration > 6:
                rates["adjusted_rate"] = base_rate * Decimal('0.60')

        # Calculate purchase option if applicable
        if is_purchase_option:
            rates["purchase_option_amount"] = base_rate * Decimal('10')  # Example: 10x monthly rate
            rates["total_cost"] = min(
                rates["total_cost"],
                rates["purchase_option_amount"]
            )

        return rates

class InventoryCalculator:
    """Service for inventory-related calculations."""

    @staticmethod
    def get_inventory_value(
        quantity: int,
        unit_cost: Decimal,
        valuation_method: str = "FIFO",
        previous_value: Optional[Decimal] = None,
        previous_quantity: Optional[int] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate inventory value based on valuation method.
        
        Args:
            quantity: Current quantity
            unit_cost: Unit cost
            valuation_method: Inventory valuation method (FIFO/LIFO/Average)
            previous_value: Previous total value
            previous_quantity: Previous quantity
            
        Returns:
            Dictionary containing total_value and average_unit_cost
        """
        if valuation_method == "Average" and previous_value is not None and previous_quantity is not None:
            total_value = (previous_value * previous_quantity + unit_cost * quantity) / (previous_quantity + quantity)
            return {
                "total_value": total_value,
                "average_unit_cost": total_value / (previous_quantity + quantity)
            }
        
        # FIFO/LIFO
        total_value = quantity * unit_cost
        return {
            "total_value": total_value,
            "average_unit_cost": unit_cost
        }

    @staticmethod
    def calculate_reorder_point(
        avg_daily_usage: Decimal,
        lead_time_days: int,
        safety_stock_days: int
    ) -> Dict[str, Decimal]:
        """
        Calculate reorder point and safety stock levels.
        
        Args:
            avg_daily_usage: Average daily usage quantity
            lead_time_days: Lead time for new orders in days
            safety_stock_days: Number of days of safety stock to maintain
            
        Returns:
            Dictionary containing reorder_point and safety_stock_quantity
        """
        lead_time_demand = avg_daily_usage * lead_time_days
        safety_stock = avg_daily_usage * safety_stock_days
        
        return {
            "reorder_point": lead_time_demand + safety_stock,
            "safety_stock_quantity": safety_stock
        }
