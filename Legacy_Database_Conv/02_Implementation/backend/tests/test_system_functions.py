"""
Unit tests for system functions implementation.
"""
import pytest
from datetime import datetime, date
from decimal import Decimal
from app.services.system_functions import (
    PriceCalculator, RentalCalculator, InventoryCalculator,
    SaleRentType
)

class TestPriceCalculator:
    """Test price calculation functionality."""

    def test_get_allowable_amount_sale(self):
        """Test allowable amount calculation for sales."""
        amount = PriceCalculator.get_allowable_amount(
            sale_rent_type=SaleRentType.SALE,
            billing_month=1,
            allowable_price=Decimal('100.00'),
            billed_quantity=2
        )
        assert amount == Decimal('200.00')

    def test_get_allowable_amount_rental(self):
        """Test allowable amount calculation for rentals."""
        # First 3 months
        amount = PriceCalculator.get_allowable_amount(
            sale_rent_type=SaleRentType.RENTAL,
            billing_month=2,
            allowable_price=Decimal('100.00'),
            billed_quantity=1
        )
        assert amount == Decimal('100.00')

        # After 3 months (25% reduction)
        amount = PriceCalculator.get_allowable_amount(
            sale_rent_type=SaleRentType.RENTAL,
            billing_month=4,
            allowable_price=Decimal('100.00'),
            billed_quantity=1
        )
        assert amount == Decimal('75.00')

    def test_get_allowable_amount_rental_purchase(self):
        """Test allowable amount calculation for rental purchase."""
        # First 10 months (10% premium)
        amount = PriceCalculator.get_allowable_amount(
            sale_rent_type=SaleRentType.RENTAL_PURCHASE,
            billing_month=5,
            allowable_price=Decimal('100.00'),
            billed_quantity=1
        )
        assert amount == Decimal('82.50')  # (100 * 0.75) * 1.1

        # After 10 months (no charge)
        amount = PriceCalculator.get_allowable_amount(
            sale_rent_type=SaleRentType.RENTAL_PURCHASE,
            billing_month=11,
            allowable_price=Decimal('100.00'),
            billed_quantity=1
        )
        assert amount == Decimal('0')

    def test_get_allowable_amount_flat_rate(self):
        """Test allowable amount calculation with flat rate."""
        amount = PriceCalculator.get_allowable_amount(
            sale_rent_type=SaleRentType.SALE,
            billing_month=1,
            allowable_price=Decimal('100.00'),
            billed_quantity=2,
            flat_rate=Decimal('50.00')
        )
        assert amount == Decimal('100.00')

    def test_get_billing_amount(self):
        """Test billing amount calculation."""
        result = PriceCalculator.get_billing_amount(
            allowable_amount=Decimal('100.00'),
            tax_rate=Decimal('8.25'),
            discount_percent=Decimal('10'),
            insurance_adjustment=Decimal('5.00')
        )
        
        assert result["subtotal"] == Decimal('90.00')  # After 10% discount
        assert result["tax_amount"] == Decimal('7.425')  # 8.25% of subtotal
        assert result["discount_amount"] == Decimal('10.00')
        assert result["insurance_adjustment"] == Decimal('5.00')
        assert result["total_amount"] == Decimal('92.425')

class TestRentalCalculator:
    """Test rental calculation functionality."""

    def test_calculate_rental_period_monthly(self):
        """Test rental period calculation for monthly rentals."""
        result = RentalCalculator.calculate_rental_period(
            start_date=date(2025, 1, 15),
            end_date=date(2025, 4, 20),
            frequency="Monthly"
        )
        
        assert result["period_count"] == 3
        assert result["prorated_days"] == 5
        assert len(result["billing_dates"]) == 4

    def test_calculate_rental_period_weekly(self):
        """Test rental period calculation for weekly rentals."""
        result = RentalCalculator.calculate_rental_period(
            start_date=date(2025, 1, 15),
            end_date=date(2025, 2, 5),
            frequency="Weekly"
        )
        
        assert result["period_count"] == 3
        assert result["prorated_days"] == 0
        assert len(result["billing_dates"]) == 4

    def test_calculate_rental_rate(self):
        """Test rental rate calculation."""
        result = RentalCalculator.calculate_rental_rate(
            base_rate=Decimal('100.00'),
            frequency="Monthly",
            duration=4,
            is_purchase_option=True
        )
        
        assert result["base_rate"] == Decimal('100.00')
        assert result["adjusted_rate"] == Decimal('75.00')  # 25% reduction after 3 months
        assert result["purchase_option_amount"] == Decimal('1000.00')
        assert result["total_cost"] == Decimal('325.00')  # 100*3 + 75*1

class TestInventoryCalculator:
    """Test inventory calculation functionality."""

    def test_get_inventory_value_fifo(self):
        """Test inventory value calculation using FIFO."""
        result = InventoryCalculator.get_inventory_value(
            quantity=100,
            unit_cost=Decimal('10.00'),
            valuation_method="FIFO"
        )
        
        assert result["total_value"] == Decimal('1000.00')
        assert result["average_unit_cost"] == Decimal('10.00')

    def test_get_inventory_value_average(self):
        """Test inventory value calculation using average cost."""
        result = InventoryCalculator.get_inventory_value(
            quantity=50,
            unit_cost=Decimal('12.00'),
            valuation_method="Average",
            previous_value=Decimal('1000.00'),
            previous_quantity=100
        )
        
        assert result["total_value"] == Decimal('11.33')  # (1000 + 600) / 150
        assert result["average_unit_cost"] == Decimal('11.33')

    def test_calculate_reorder_point(self):
        """Test reorder point calculation."""
        result = InventoryCalculator.calculate_reorder_point(
            avg_daily_usage=Decimal('10'),
            lead_time_days=5,
            safety_stock_days=3
        )
        
        assert result["reorder_point"] == Decimal('80')  # (10 * 5) + (10 * 3)
        assert result["safety_stock_quantity"] == Decimal('30')  # 10 * 3
