"""
Tests for the date service module
"""

from datetime import datetime
from app.services.billing.date_service import DateService, BillingFrequency

def test_get_new_dos_to_one_time():
    """Test DOS To calculation for one-time frequency"""
    service = DateService()
    
    from_date = datetime(2025, 1, 1)
    result = service.get_new_dos_to(
        from_date=from_date,
        frequency=BillingFrequency.ONE_TIME
    )
    assert result == from_date

def test_get_new_dos_to_daily():
    """Test DOS To calculation for daily frequency"""
    service = DateService()
    
    from_date = datetime(2025, 1, 1)
    result = service.get_new_dos_to(
        from_date=from_date,
        frequency=BillingFrequency.DAILY,
        periods=5
    )
    assert result == datetime(2025, 1, 6)

def test_get_new_dos_to_weekly():
    """Test DOS To calculation for weekly frequency"""
    service = DateService()
    
    from_date = datetime(2025, 1, 1)
    result = service.get_new_dos_to(
        from_date=from_date,
        frequency=BillingFrequency.WEEKLY,
        periods=2
    )
    assert result == datetime(2025, 1, 15)

def test_get_new_dos_to_monthly():
    """Test DOS To calculation for monthly frequency"""
    service = DateService()
    
    # Test regular month
    from_date = datetime(2025, 1, 15)
    result = service.get_new_dos_to(
        from_date=from_date,
        frequency=BillingFrequency.MONTHLY,
        periods=2
    )
    assert result == datetime(2025, 3, 14)
    
    # Test month end dates
    from_date = datetime(2025, 1, 31)
    result = service.get_new_dos_to(
        from_date=from_date,
        frequency=BillingFrequency.MONTHLY,
        periods=1
    )
    assert result == datetime(2025, 2, 28)

def test_get_new_dos_to_with_end_date():
    """Test DOS To calculation with end date constraint"""
    service = DateService()
    
    from_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 15)
    
    result = service.get_new_dos_to(
        from_date=from_date,
        frequency=BillingFrequency.MONTHLY,
        periods=2,
        end_date=end_date
    )
    assert result == end_date

def test_get_next_dos_from_one_time():
    """Test next DOS From calculation for one-time frequency"""
    service = DateService()
    
    current_to = datetime(2025, 1, 1)
    result = service.get_next_dos_from(
        current_to=current_to,
        frequency=BillingFrequency.ONE_TIME,
        gap_days=2
    )
    assert result == datetime(2025, 1, 3)

def test_get_next_dos_from_daily():
    """Test next DOS From calculation for daily frequency"""
    service = DateService()
    
    current_to = datetime(2025, 1, 1)
    result = service.get_next_dos_from(
        current_to=current_to,
        frequency=BillingFrequency.DAILY
    )
    assert result == datetime(2025, 1, 2)

def test_get_next_dos_from_weekly():
    """Test next DOS From calculation for weekly frequency"""
    service = DateService()
    
    # Test maintaining day of week
    current_to = datetime(2025, 1, 1)  # Wednesday
    result = service.get_next_dos_from(
        current_to=current_to,
        frequency=BillingFrequency.WEEKLY
    )
    assert result == datetime(2025, 1, 8)  # Next Wednesday

def test_get_next_dos_from_monthly():
    """Test next DOS From calculation for monthly frequency"""
    service = DateService()
    
    # Test regular month
    current_to = datetime(2025, 1, 15)
    result = service.get_next_dos_from(
        current_to=current_to,
        frequency=BillingFrequency.MONTHLY
    )
    assert result == datetime(2025, 2, 15)
    
    # Test month end dates
    current_to = datetime(2025, 1, 31)
    result = service.get_next_dos_from(
        current_to=current_to,
        frequency=BillingFrequency.MONTHLY
    )
    assert result == datetime(2025, 2, 28)

def test_get_next_dos_to_one_time():
    """Test next DOS To calculation for one-time frequency"""
    service = DateService()
    
    current_from = datetime(2025, 1, 1)
    current_to = datetime(2025, 1, 31)
    result = service.get_next_dos_to(
        current_from=current_from,
        current_to=current_to,
        frequency=BillingFrequency.ONE_TIME
    )
    assert result == current_to

def test_get_next_dos_to_daily():
    """Test next DOS To calculation for daily frequency"""
    service = DateService()
    
    # Test 5-day period
    current_from = datetime(2025, 1, 1)
    current_to = datetime(2025, 1, 5)
    result = service.get_next_dos_to(
        current_from=current_from,
        current_to=current_to,
        frequency=BillingFrequency.DAILY
    )
    assert result == datetime(2025, 1, 10)  # Next 5-day period

def test_get_next_dos_to_weekly():
    """Test next DOS To calculation for weekly frequency"""
    service = DateService()
    
    # Test 2-week period
    current_from = datetime(2025, 1, 1)
    current_to = datetime(2025, 1, 14)
    result = service.get_next_dos_to(
        current_from=current_from,
        current_to=current_to,
        frequency=BillingFrequency.WEEKLY
    )
    assert result == datetime(2025, 1, 28)  # Next 2-week period

def test_get_next_dos_to_monthly():
    """Test next DOS To calculation for monthly frequency"""
    service = DateService()
    
    # Test regular month
    current_from = datetime(2025, 1, 15)
    current_to = datetime(2025, 2, 14)
    result = service.get_next_dos_to(
        current_from=current_from,
        current_to=current_to,
        frequency=BillingFrequency.MONTHLY
    )
    assert result == datetime(2025, 3, 14)
    
    # Test month end dates
    current_from = datetime(2025, 1, 31)
    current_to = datetime(2025, 2, 28)
    result = service.get_next_dos_to(
        current_from=current_from,
        current_to=current_to,
        frequency=BillingFrequency.MONTHLY
    )
    assert result == datetime(2025, 3, 31)

def test_get_next_dos_to_with_end_date():
    """Test next DOS To calculation with end date constraint"""
    service = DateService()
    
    current_from = datetime(2025, 1, 1)
    current_to = datetime(2025, 1, 31)
    end_date = datetime(2025, 2, 15)
    
    result = service.get_next_dos_to(
        current_from=current_from,
        current_to=current_to,
        frequency=BillingFrequency.MONTHLY,
        end_date=end_date
    )
    assert result == end_date

def test_get_period_end_one_time():
    """Test period end calculation for one-time frequency"""
    service = DateService()
    
    start_date = datetime(2025, 1, 1, 10, 30)  # With time component
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.ONE_TIME
    )
    assert result == start_date

def test_get_period_end_daily():
    """Test period end calculation for daily frequency"""
    service = DateService()
    
    # Test without calendar alignment
    start_date = datetime(2025, 1, 1, 10, 30)
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.DAILY,
        periods=5
    )
    assert result == datetime(2025, 1, 5, 10, 30)
    
    # Test with calendar alignment
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.DAILY,
        periods=5,
        align_to_calendar=True
    )
    assert result == datetime(2025, 1, 5, 23, 59, 59, 999999)

def test_get_period_end_weekly():
    """Test period end calculation for weekly frequency"""
    service = DateService()
    
    # Test without calendar alignment
    start_date = datetime(2025, 1, 1)  # Wednesday
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.WEEKLY,
        periods=2
    )
    assert result == datetime(2025, 1, 8)  # Next Wednesday
    
    # Test with calendar alignment
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.WEEKLY,
        periods=2,
        align_to_calendar=True
    )
    assert result == datetime(2025, 1, 12, 23, 59, 59, 999999)  # Sunday

def test_get_period_end_monthly():
    """Test period end calculation for monthly frequency"""
    service = DateService()
    
    # Test without calendar alignment
    start_date = datetime(2025, 1, 15)
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=2
    )
    assert result == datetime(2025, 3, 14)
    
    # Test with calendar alignment
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=2,
        align_to_calendar=True
    )
    assert result == datetime(2025, 2, 28, 23, 59, 59, 999999)
    
    # Test month end dates
    start_date = datetime(2025, 1, 31)
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=1,
        align_to_calendar=True
    )
    assert result == datetime(2025, 1, 31, 23, 59, 59, 999999)

def test_get_period_end_with_end_date():
    """Test period end calculation with end date constraint"""
    service = DateService()
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 15, 12, 30)
    
    # Test without calendar alignment
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=2,
        end_date=end_date
    )
    assert result == end_date
    
    # Test with calendar alignment
    result = service.get_period_end(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=2,
        end_date=end_date,
        align_to_calendar=True
    )
    assert result == datetime(2025, 1, 15, 23, 59, 59, 999999)

def test_get_period_end2_min_days():
    """Test period end2 calculation with minimum days requirement"""
    service = DateService()
    
    # Test daily frequency
    start_date = datetime(2025, 1, 1)
    result = service.get_period_end2(
        start_date=start_date,
        frequency=BillingFrequency.DAILY,
        periods=2,
        min_days=5
    )
    assert result == datetime(2025, 1, 5)
    
    # Test weekly frequency
    result = service.get_period_end2(
        start_date=start_date,
        frequency=BillingFrequency.WEEKLY,
        periods=1,
        min_days=10
    )
    assert result == datetime(2025, 1, 14)  # 2 weeks
    
    # Test monthly frequency
    result = service.get_period_end2(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=1,
        min_days=45
    )
    assert result == datetime(2025, 2, 28)  # 2 months

def test_get_period_end2_extend_partial():
    """Test period end2 calculation with partial period extension"""
    service = DateService()
    
    # Test weekly extension
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 4)  # 4 days into week
    result = service.get_period_end2(
        start_date=start_date,
        frequency=BillingFrequency.WEEKLY,
        periods=2,
        end_date=end_date,
        extend_for_partial=True
    )
    assert result == datetime(2025, 1, 7)  # Extended to end of week
    
    # Test monthly extension
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 20)  # 20 days into month
    result = service.get_period_end2(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=2,
        end_date=end_date,
        extend_for_partial=True
    )
    assert result == datetime(2025, 1, 31)  # Extended to end of month

def test_get_period_end2_no_extension():
    """Test period end2 calculation without partial period extension"""
    service = DateService()
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 20)
    result = service.get_period_end2(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=2,
        end_date=end_date,
        extend_for_partial=False
    )
    assert result == end_date  # Not extended

def test_get_period_end2_calendar_alignment():
    """Test period end2 calculation with calendar alignment"""
    service = DateService()
    
    start_date = datetime(2025, 1, 1, 10, 30)
    end_date = datetime(2025, 1, 20, 15, 45)
    result = service.get_period_end2(
        start_date=start_date,
        frequency=BillingFrequency.MONTHLY,
        periods=1,
        end_date=end_date,
        align_to_calendar=True
    )
    assert result == datetime(2025, 1, 20, 23, 59, 59, 999999)
