"""
Tests for the billing calculation service
"""

from decimal import Decimal
from datetime import datetime, timedelta
import pytest
from app.services.billing.calculation_service import (
    BillingCalculator,
    SaleRentType,
    BillingFrequency,
    InvoiceModifier,
    InvoiceModifierType,
    QuantityRule
)

def test_one_time_sale():
    """Test one time sale calculations"""
    calc = BillingCalculator()
    
    # First month should charge full amount
    assert calc.get_allowable_amount(
        SaleRentType.ONE_TIME_SALE,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=2
    ) == Decimal('200.00')
    
    # Subsequent months should be zero
    assert calc.get_allowable_amount(
        SaleRentType.ONE_TIME_SALE,
        billing_month=2,
        price=Decimal('100.00'),
        quantity=2
    ) == Decimal('0.00')

def test_monthly_rental():
    """Test monthly rental calculations"""
    calc = BillingCalculator()
    
    # Should charge full amount each month
    assert calc.get_allowable_amount(
        SaleRentType.MONTHLY_RENTAL,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=2
    ) == Decimal('200.00')
    
    assert calc.get_allowable_amount(
        SaleRentType.MONTHLY_RENTAL,
        billing_month=2,
        price=Decimal('100.00'),
        quantity=2
    ) == Decimal('200.00')

def test_rent_to_purchase():
    """Test rent to purchase calculations"""
    calc = BillingCalculator()
    
    # First 9 months should be rental price
    assert calc.get_allowable_amount(
        SaleRentType.RENT_TO_PURCHASE,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=1,
        sale_price=Decimal('1500.00')
    ) == Decimal('100.00')
    
    # 10th month should be remainder
    assert calc.get_allowable_amount(
        SaleRentType.RENT_TO_PURCHASE,
        billing_month=10,
        price=Decimal('100.00'),
        quantity=1,
        sale_price=Decimal('1500.00')
    ) == Decimal('600.00')  # 1500 - (9 * 100)
    
    # After 10th month should be zero
    assert calc.get_allowable_amount(
        SaleRentType.RENT_TO_PURCHASE,
        billing_month=11,
        price=Decimal('100.00'),
        quantity=1,
        sale_price=Decimal('1500.00')
    ) == Decimal('0.00')

def test_capped_rental():
    """Test capped rental calculations"""
    calc = BillingCalculator()
    
    # First 3 months full price
    assert calc.get_allowable_amount(
        SaleRentType.CAPPED_RENTAL,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')
    
    # Months 4-15 at 75%
    assert calc.get_allowable_amount(
        SaleRentType.CAPPED_RENTAL,
        billing_month=4,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('75.00')
    
    # Every 6 months after month 22
    assert calc.get_allowable_amount(
        SaleRentType.CAPPED_RENTAL,
        billing_month=22,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')
    
    assert calc.get_allowable_amount(
        SaleRentType.CAPPED_RENTAL,
        billing_month=28,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')
    
    # Other months zero
    assert calc.get_allowable_amount(
        SaleRentType.CAPPED_RENTAL,
        billing_month=25,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('0.00')

def test_parental_capped_rental():
    """Test parental capped rental calculations"""
    calc = BillingCalculator()
    
    # First 15 months full price
    assert calc.get_allowable_amount(
        SaleRentType.PARENTAL_CAPPED_RENTAL,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')
    
    assert calc.get_allowable_amount(
        SaleRentType.PARENTAL_CAPPED_RENTAL,
        billing_month=15,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')
    
    # Every 6 months after month 22
    assert calc.get_allowable_amount(
        SaleRentType.PARENTAL_CAPPED_RENTAL,
        billing_month=22,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')
    
    assert calc.get_allowable_amount(
        SaleRentType.PARENTAL_CAPPED_RENTAL,
        billing_month=28,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')
    
    # Other months zero
    assert calc.get_allowable_amount(
        SaleRentType.PARENTAL_CAPPED_RENTAL,
        billing_month=25,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('0.00')

def test_flat_rate():
    """Test flat rate calculations"""
    calc = BillingCalculator()
    
    # Flat rate should ignore quantity
    assert calc.get_allowable_amount(
        SaleRentType.MONTHLY_RENTAL,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=5,
        flat_rate=True
    ) == Decimal('100.00')

def test_amount_multiplier_one_time():
    """Test amount multiplier for one-time items"""
    calc = BillingCalculator()
    
    dos_from = datetime(2025, 1, 1)
    dos_to = datetime(2025, 1, 31)
    
    # One-time items should always have multiplier of 1
    assert calc.get_amount_multiplier(
        dos_from=dos_from,
        dos_to=dos_to,
        end_date=None,
        sale_rent_type=SaleRentType.ONE_TIME_SALE,
        ordered_when=BillingFrequency.DAILY,
        billed_when=BillingFrequency.MONTHLY
    ) == Decimal('1')

def test_amount_multiplier_same_frequency():
    """Test amount multiplier when order and bill frequency match"""
    calc = BillingCalculator()
    
    dos_from = datetime(2025, 1, 1)
    dos_to = datetime(2025, 1, 31)
    
    # Same frequencies should have multiplier of 1
    assert calc.get_amount_multiplier(
        dos_from=dos_from,
        dos_to=dos_to,
        end_date=None,
        sale_rent_type=SaleRentType.MONTHLY_RENTAL,
        ordered_when=BillingFrequency.MONTHLY,
        billed_when=BillingFrequency.MONTHLY
    ) == Decimal('1')

def test_amount_multiplier_daily_to_monthly():
    """Test amount multiplier when converting daily to monthly"""
    calc = BillingCalculator()
    
    dos_from = datetime(2025, 1, 1)
    dos_to = datetime(2025, 1, 31)
    
    # Daily to monthly should multiply by number of days
    assert calc.get_amount_multiplier(
        dos_from=dos_from,
        dos_to=dos_to,
        end_date=None,
        sale_rent_type=SaleRentType.MONTHLY_RENTAL,
        ordered_when=BillingFrequency.DAILY,
        billed_when=BillingFrequency.MONTHLY
    ) == Decimal('31')

def test_amount_multiplier_weekly_to_monthly():
    """Test amount multiplier when converting weekly to monthly"""
    calc = BillingCalculator()
    
    dos_from = datetime(2025, 1, 1)
    dos_to = datetime(2025, 1, 28)
    
    # Weekly to monthly should divide days by 7
    assert calc.get_amount_multiplier(
        dos_from=dos_from,
        dos_to=dos_to,
        end_date=None,
        sale_rent_type=SaleRentType.MONTHLY_RENTAL,
        ordered_when=BillingFrequency.WEEKLY,
        billed_when=BillingFrequency.MONTHLY
    ) == Decimal('4.0000')

def test_amount_multiplier_with_end_date():
    """Test amount multiplier with early termination"""
    calc = BillingCalculator()
    
    dos_from = datetime(2025, 1, 1)
    dos_to = datetime(2025, 1, 31)
    end_date = datetime(2025, 1, 15)
    
    # Should only count days until end_date
    assert calc.get_amount_multiplier(
        dos_from=dos_from,
        dos_to=dos_to,
        end_date=end_date,
        sale_rent_type=SaleRentType.MONTHLY_RENTAL,
        ordered_when=BillingFrequency.DAILY,
        billed_when=BillingFrequency.MONTHLY
    ) == Decimal('15')

def test_billable_amount_one_time():
    """Test billable amount for one-time items"""
    calc = BillingCalculator()
    
    # First month should charge full amount
    assert calc.get_billable_amount(
        SaleRentType.ONE_TIME_SALE,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=2
    ) == Decimal('200.00')
    
    # Subsequent months should be zero
    assert calc.get_billable_amount(
        SaleRentType.ONE_TIME_SALE,
        billing_month=2,
        price=Decimal('100.00'),
        quantity=2
    ) == Decimal('0.00')

def test_billable_amount_with_tax():
    """Test billable amount with tax applied"""
    calc = BillingCalculator()
    
    assert calc.get_billable_amount(
        SaleRentType.ONE_TIME_SALE,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=1,
        tax_rate=Decimal('0.08')
    ) == Decimal('108.00')

def test_billable_amount_with_discount():
    """Test billable amount with discount applied"""
    calc = BillingCalculator()
    
    assert calc.get_billable_amount(
        SaleRentType.ONE_TIME_SALE,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=1,
        discount_percent=Decimal('10')
    ) == Decimal('90.00')

def test_billable_amount_with_tax_and_discount():
    """Test billable amount with both tax and discount"""
    calc = BillingCalculator()
    
    # $100 - 10% discount = $90, then + 8% tax = $97.20
    assert calc.get_billable_amount(
        SaleRentType.ONE_TIME_SALE,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=1,
        tax_rate=Decimal('0.08'),
        discount_percent=Decimal('10')
    ) == Decimal('97.20')

def test_billable_amount_rent_to_purchase():
    """Test billable amount for rent-to-purchase items"""
    calc = BillingCalculator()
    
    # First 9 months should be rental price
    assert calc.get_billable_amount(
        SaleRentType.RENT_TO_PURCHASE,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=1,
        sale_price=Decimal('1500.00')
    ) == Decimal('100.00')
    
    # 10th month should be remainder
    assert calc.get_billable_amount(
        SaleRentType.RENT_TO_PURCHASE,
        billing_month=10,
        price=Decimal('100.00'),
        quantity=1,
        sale_price=Decimal('1500.00')
    ) == Decimal('600.00')  # 1500 - (9 * 100)

def test_billable_amount_capped_rental():
    """Test billable amount for capped rental items"""
    calc = BillingCalculator()
    
    # First 3 months full price
    assert calc.get_billable_amount(
        SaleRentType.CAPPED_RENTAL,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')
    
    # Months 4-15 at 75%
    assert calc.get_billable_amount(
        SaleRentType.CAPPED_RENTAL,
        billing_month=4,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('75.00')
    
    # Every 6 months after month 22
    assert calc.get_billable_amount(
        SaleRentType.CAPPED_RENTAL,
        billing_month=22,
        price=Decimal('100.00'),
        quantity=1
    ) == Decimal('100.00')

def test_billable_amount_flat_rate():
    """Test billable amount with flat rate"""
    calc = BillingCalculator()
    
    # Flat rate should ignore quantity
    assert calc.get_billable_amount(
        SaleRentType.MONTHLY_RENTAL,
        billing_month=1,
        price=Decimal('100.00'),
        quantity=5,
        flat_rate=True
    ) == Decimal('100.00')

def test_invoice_modifier_basic():
    """Test basic invoice modifier without rules"""
    calc = BillingCalculator()
    
    modifier = InvoiceModifier(
        modifier_type=InvoiceModifierType.STANDARD,
        multiplier=Decimal('0.9')  # 10% discount
    )
    
    result = calc.get_invoice_modifier(
        base_amount=Decimal('100.00'),
        modifier_type=InvoiceModifierType.STANDARD,
        service_date=datetime(2025, 1, 1),
        modifiers=[modifier]
    )
    
    assert result == Decimal('90.00')

def test_invoice_modifier_with_dates():
    """Test invoice modifier with date restrictions"""
    calc = BillingCalculator()
    
    modifier = InvoiceModifier(
        modifier_type=InvoiceModifierType.STANDARD,
        multiplier=Decimal('0.9'),
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 12, 31)
    )
    
    # Within date range
    result = calc.get_invoice_modifier(
        base_amount=Decimal('100.00'),
        modifier_type=InvoiceModifierType.STANDARD,
        service_date=datetime(2025, 6, 1),
        modifiers=[modifier]
    )
    assert result == Decimal('90.00')
    
    # Outside date range
    result = calc.get_invoice_modifier(
        base_amount=Decimal('100.00'),
        modifier_type=InvoiceModifierType.STANDARD,
        service_date=datetime(2024, 12, 31),
        modifiers=[modifier]
    )
    assert result == Decimal('100.00')

def test_invoice_modifier_with_rules():
    """Test invoice modifier with business rules"""
    calc = BillingCalculator()
    
    modifier = InvoiceModifier(
        modifier_type=InvoiceModifierType.INSURANCE,
        multiplier=Decimal('0.85'),
        rules={
            'insurance_type': ['PPO', 'HMO'],
            'state': ['TX', 'CA']
        }
    )
    
    # Matching rules
    result = calc.get_invoice_modifier(
        base_amount=Decimal('100.00'),
        modifier_type=InvoiceModifierType.INSURANCE,
        service_date=datetime(2025, 1, 1),
        modifiers=[modifier],
        insurance_type='PPO',
        state='TX'
    )
    assert result == Decimal('85.00')
    
    # Non-matching rules
    result = calc.get_invoice_modifier(
        base_amount=Decimal('100.00'),
        modifier_type=InvoiceModifierType.INSURANCE,
        service_date=datetime(2025, 1, 1),
        modifiers=[modifier],
        insurance_type='EPO',
        state='TX'
    )
    assert result == Decimal('100.00')

def test_invoice_modifier_with_min_max():
    """Test invoice modifier with minimum and maximum amounts"""
    calc = BillingCalculator()
    
    modifier = InvoiceModifier(
        modifier_type=InvoiceModifierType.STANDARD,
        multiplier=Decimal('0.5'),
        min_amount=Decimal('75.00'),
        max_amount=Decimal('200.00')
    )
    
    # Test minimum amount
    result = calc.get_invoice_modifier(
        base_amount=Decimal('100.00'),
        modifier_type=InvoiceModifierType.STANDARD,
        service_date=datetime(2025, 1, 1),
        modifiers=[modifier]
    )
    assert result == Decimal('75.00')  # Would be 50.00 but min is 75.00
    
    # Test maximum amount
    result = calc.get_invoice_modifier(
        base_amount=Decimal('500.00'),
        modifier_type=InvoiceModifierType.STANDARD,
        service_date=datetime(2025, 1, 1),
        modifiers=[modifier]
    )
    assert result == Decimal('200.00')  # Would be 250.00 but max is 200.00

def test_invoice_modifier_multiple():
    """Test multiple invoice modifiers with different rules"""
    calc = BillingCalculator()
    
    modifiers = [
        InvoiceModifier(
            modifier_type=InvoiceModifierType.INSURANCE,
            multiplier=Decimal('0.8'),
            rules={'insurance_type': ['PPO']}
        ),
        InvoiceModifier(
            modifier_type=InvoiceModifierType.INSURANCE,
            multiplier=Decimal('0.9'),
            rules={'insurance_type': ['PPO', 'HMO', 'EPO']}
        )
    ]
    
    # Should use more specific modifier (0.8 for PPO)
    result = calc.get_invoice_modifier(
        base_amount=Decimal('100.00'),
        modifier_type=InvoiceModifierType.INSURANCE,
        service_date=datetime(2025, 1, 1),
        modifiers=modifiers,
        insurance_type='PPO'
    )
    assert result == Decimal('80.00')

def test_multiplier_one_time():
    """Test multiplier for one-time frequency"""
    calc = BillingCalculator()
    
    result = calc.get_multiplier(
        frequency=BillingFrequency.ONE_TIME,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 31)
    )
    assert result == Decimal('1')

def test_multiplier_daily():
    """Test multiplier for daily frequency"""
    calc = BillingCalculator()
    
    result = calc.get_multiplier(
        frequency=BillingFrequency.DAILY,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 31)
    )
    assert result == Decimal('31')

def test_multiplier_weekly_no_prorate():
    """Test multiplier for weekly frequency without proration"""
    calc = BillingCalculator()
    
    # Test floor rounding (3 weeks + 2 days = 3 weeks)
    result = calc.get_multiplier(
        frequency=BillingFrequency.WEEKLY,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 23),
        prorate=False,
        round_method='floor'
    )
    assert result == Decimal('3')
    
    # Test ceiling rounding (3 weeks + 2 days = 4 weeks)
    result = calc.get_multiplier(
        frequency=BillingFrequency.WEEKLY,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 23),
        prorate=False,
        round_method='ceil'
    )
    assert result == Decimal('4')

def test_multiplier_weekly_with_prorate():
    """Test multiplier for weekly frequency with proration"""
    calc = BillingCalculator()
    
    # 3 weeks + 2 days = 3.2857 weeks
    result = calc.get_multiplier(
        frequency=BillingFrequency.WEEKLY,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 23),
        prorate=True
    )
    assert result == Decimal('3.2857')

def test_multiplier_monthly_no_prorate():
    """Test multiplier for monthly frequency without proration"""
    calc = BillingCalculator()
    
    # Test floor rounding (2 months + 15 days = 2 months)
    result = calc.get_multiplier(
        frequency=BillingFrequency.MONTHLY,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 3, 15),
        prorate=False,
        round_method='floor'
    )
    assert result == Decimal('2')
    
    # Test ceiling rounding (2 months + 15 days = 3 months)
    result = calc.get_multiplier(
        frequency=BillingFrequency.MONTHLY,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 3, 15),
        prorate=False,
        round_method='ceil'
    )
    assert result == Decimal('3')

def test_multiplier_monthly_with_prorate():
    """Test multiplier for monthly frequency with proration"""
    calc = BillingCalculator()
    
    # 2 months + 15 days = 2.5 months
    result = calc.get_multiplier(
        frequency=BillingFrequency.MONTHLY,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 3, 15),
        prorate=True
    )
    assert result == Decimal('2.5000')

def test_multiplier_with_end_date():
    """Test multiplier with early termination"""
    calc = BillingCalculator()
    
    result = calc.get_multiplier(
        frequency=BillingFrequency.DAILY,
        from_date=datetime(2025, 1, 1),
        to_date=datetime(2025, 1, 31),
        end_date=datetime(2025, 1, 15)
    )
    assert result == Decimal('15')

def test_multiplier_invalid_dates():
    """Test multiplier with invalid date ranges"""
    calc = BillingCalculator()
    
    result = calc.get_multiplier(
        frequency=BillingFrequency.DAILY,
        from_date=datetime(2025, 1, 31),
        to_date=datetime(2025, 1, 1)  # End before start
    )
    assert result == Decimal('0')

def test_quantity_multiplier_basic():
    """Test basic quantity multiplier without rules"""
    calc = BillingCalculator()
    
    result = calc.get_quantity_multiplier(
        quantity=5,
        rules=[]
    )
    assert result == Decimal('5.0000')

def test_quantity_multiplier_single_rule():
    """Test quantity multiplier with a single rule"""
    calc = BillingCalculator()
    
    rule = QuantityRule(
        min_quantity=3,
        max_quantity=None,
        multiplier=Decimal('0.8')  # 20% discount for 3+ items
    )
    
    result = calc.get_quantity_multiplier(
        quantity=5,
        rules=[rule]
    )
    assert result == Decimal('0.8000')

def test_quantity_multiplier_multiple_rules():
    """Test quantity multiplier with multiple overlapping rules"""
    calc = BillingCalculator()
    
    rules = [
        QuantityRule(
            min_quantity=10,
            max_quantity=None,
            multiplier=Decimal('0.7')  # 30% discount for 10+ items
        ),
        QuantityRule(
            min_quantity=5,
            max_quantity=9,
            multiplier=Decimal('0.8')  # 20% discount for 5-9 items
        ),
        QuantityRule(
            min_quantity=3,
            max_quantity=4,
            multiplier=Decimal('0.9')  # 10% discount for 3-4 items
        )
    ]
    
    # Test each tier
    result = calc.get_quantity_multiplier(quantity=12, rules=rules)
    assert result == Decimal('0.7000')
    
    result = calc.get_quantity_multiplier(quantity=7, rules=rules)
    assert result == Decimal('0.8000')
    
    result = calc.get_quantity_multiplier(quantity=3, rules=rules)
    assert result == Decimal('0.9000')
    
    # Test quantity below any rule
    result = calc.get_quantity_multiplier(quantity=2, rules=rules)
    assert result == Decimal('2.0000')

def test_quantity_multiplier_flat_rate():
    """Test quantity multiplier with flat rate pricing"""
    calc = BillingCalculator()
    
    rule = QuantityRule(
        min_quantity=5,
        max_quantity=None,
        multiplier=Decimal('1.0'),
        flat_rate=Decimal('100.00')
    )
    
    # Test flat rate calculation
    result = calc.get_quantity_multiplier(
        quantity=5,
        rules=[rule],
        base_amount=Decimal('200.00'),
        allow_flat_rate=True
    )
    assert result == Decimal('0.5000')  # 100/200 = 0.5
    
    # Test with flat rate disabled
    result = calc.get_quantity_multiplier(
        quantity=5,
        rules=[rule],
        base_amount=Decimal('200.00'),
        allow_flat_rate=False
    )
    assert result == Decimal('1.0000')

def test_quantity_multiplier_invalid():
    """Test quantity multiplier with invalid inputs"""
    calc = BillingCalculator()
    
    # Test zero quantity
    result = calc.get_quantity_multiplier(
        quantity=0,
        rules=[]
    )
    assert result == Decimal('0')
    
    # Test negative quantity
    result = calc.get_quantity_multiplier(
        quantity=-1,
        rules=[]
    )
    assert result == Decimal('0')
    
    # Test flat rate with zero base amount
    rule = QuantityRule(
        min_quantity=1,
        max_quantity=None,
        multiplier=Decimal('1.0'),
        flat_rate=Decimal('100.00')
    )
    result = calc.get_quantity_multiplier(
        quantity=1,
        rules=[rule],
        base_amount=Decimal('0'),
        allow_flat_rate=True
    )
    assert result == Decimal('0')
