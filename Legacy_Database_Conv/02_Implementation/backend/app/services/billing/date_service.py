"""
Date Service Module

This module handles date-related calculations for billing periods and service dates.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from enum import Enum

class BillingFrequency(str, Enum):
    """Billing frequency options"""
    ONE_TIME = "OneTime"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

class DateService:
    """Handles date calculations for billing and service periods"""
    
    @staticmethod
    def get_new_dos_to(
        from_date: datetime,
        frequency: BillingFrequency,
        periods: int = 1,
        end_date: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate the end date (DOS To) based on frequency and periods.
        
        Args:
            from_date: Start date of service
            frequency: Billing frequency
            periods: Number of periods to calculate
            end_date: Optional maximum end date
            
        Returns:
            datetime: Calculated end date
        """
        if frequency == BillingFrequency.ONE_TIME:
            return from_date
            
        if frequency == BillingFrequency.DAILY:
            dos_to = from_date + timedelta(days=periods)
        elif frequency == BillingFrequency.WEEKLY:
            dos_to = from_date + timedelta(weeks=periods)
        else:  # MONTHLY
            # Add months while handling month end dates correctly
            dos_to = from_date
            for _ in range(periods):
                # Move to first of next month
                if dos_to.month == 12:
                    dos_to = dos_to.replace(year=dos_to.year + 1, month=1)
                else:
                    dos_to = dos_to.replace(month=dos_to.month + 1)
                
                # Handle month end dates
                while dos_to.month == from_date.month:
                    dos_to += timedelta(days=1)
            
            # Subtract one day to get end of previous month
            dos_to -= timedelta(days=1)
        
        # Apply end date constraint if provided
        if end_date and dos_to > end_date:
            return end_date
            
        return dos_to
    
    @staticmethod
    def get_next_dos_from(
        current_to: datetime,
        frequency: BillingFrequency,
        gap_days: int = 1
    ) -> datetime:
        """
        Calculate the next start date (DOS From) based on current end date.
        
        Args:
            current_to: Current end date of service
            frequency: Billing frequency
            gap_days: Number of days between periods
            
        Returns:
            datetime: Next start date
        """
        if frequency == BillingFrequency.ONE_TIME:
            return current_to + timedelta(days=gap_days)
            
        # For recurring frequencies, start next day by default
        next_from = current_to + timedelta(days=gap_days)
        
        if frequency == BillingFrequency.WEEKLY:
            # Ensure we start on the same day of week
            days_diff = (next_from.weekday() - current_to.weekday()) % 7
            if days_diff > 0:
                next_from += timedelta(days=7 - days_diff)
                
        elif frequency == BillingFrequency.MONTHLY:
            # Try to maintain same day of month
            target_day = min(current_to.day, 28)  # Handle month end dates
            while next_from.day != target_day:
                if next_from.day > target_day:
                    next_from -= timedelta(days=1)
                else:
                    next_from += timedelta(days=1)
        
        return next_from

    @staticmethod
    def get_next_dos_to(
        current_from: datetime,
        current_to: datetime,
        frequency: BillingFrequency,
        end_date: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate the next end date (DOS To) based on current period.
        
        Args:
            current_from: Current start date of service
            current_to: Current end date of service
            frequency: Billing frequency
            end_date: Optional maximum end date
            
        Returns:
            datetime: Next end date
        """
        if frequency == BillingFrequency.ONE_TIME:
            return current_to
            
        # Calculate period length from current dates
        if frequency == BillingFrequency.DAILY:
            days = (current_to - current_from).days + 1
            next_to = current_to + timedelta(days=days)
            
        elif frequency == BillingFrequency.WEEKLY:
            # Maintain exact number of weeks
            weeks = ((current_to - current_from).days + 1) // 7
            next_to = current_to + timedelta(weeks=weeks)
            
        else:  # MONTHLY
            # Calculate months between current dates
            months = (current_to.year - current_from.year) * 12 + (current_to.month - current_from.month)
            if current_to.day >= current_from.day:
                months += 1
                
            # Add same number of months to current_to
            next_to = current_to
            for _ in range(months):
                if next_to.month == 12:
                    next_to = next_to.replace(year=next_to.year + 1, month=1)
                else:
                    next_to = next_to.replace(month=next_to.month + 1)
                    
                # Adjust to match original period length
                while (next_to - current_to).days > (current_to - current_from).days:
                    next_to -= timedelta(days=1)
        
        # Apply end date constraint if provided
        if end_date and next_to > end_date:
            return end_date
            
        return next_to

    @staticmethod
    def get_period_end(
        start_date: datetime,
        frequency: BillingFrequency,
        periods: int = 1,
        end_date: Optional[datetime] = None,
        align_to_calendar: bool = False
    ) -> datetime:
        """
        Calculate the end of a billing period with optional calendar alignment.
        
        Args:
            start_date: Start date of the period
            frequency: Billing frequency
            periods: Number of periods to calculate
            end_date: Optional maximum end date
            align_to_calendar: If True, align to calendar boundaries
            
        Returns:
            datetime: Calculated period end date
        """
        if frequency == BillingFrequency.ONE_TIME:
            return start_date
            
        if frequency == BillingFrequency.DAILY:
            if align_to_calendar:
                # Align to end of day
                period_end = start_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            else:
                period_end = start_date
                
            # Add specified number of days
            period_end += timedelta(days=periods - 1)
            
        elif frequency == BillingFrequency.WEEKLY:
            if align_to_calendar:
                # Align to end of week (Sunday)
                days_to_sunday = (6 - start_date.weekday()) % 7
                period_end = start_date + timedelta(days=days_to_sunday)
                period_end = period_end.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            else:
                period_end = start_date
                
            # Add specified number of weeks
            period_end += timedelta(weeks=periods - 1)
            
        else:  # MONTHLY
            if align_to_calendar:
                # Align to end of month
                if start_date.month == 12:
                    period_end = start_date.replace(
                        year=start_date.year + 1,
                        month=1,
                        day=1
                    )
                else:
                    period_end = start_date.replace(
                        month=start_date.month + 1,
                        day=1
                    )
                period_end -= timedelta(days=1)
                period_end = period_end.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            else:
                period_end = start_date
                
            # Add specified number of months
            for _ in range(periods - 1):
                if period_end.month == 12:
                    period_end = period_end.replace(
                        year=period_end.year + 1,
                        month=1
                    )
                else:
                    period_end = period_end.replace(
                        month=period_end.month + 1
                    )
                    
                # Handle month end dates
                while period_end.month == start_date.month:
                    period_end += timedelta(days=1)
                period_end -= timedelta(days=1)
        
        # Apply end date constraint if provided
        if end_date and period_end > end_date:
            if align_to_calendar:
                # Align end_date to end of its period
                return end_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            return end_date
            
        return period_end

    @staticmethod
    def get_period_end2(
        start_date: datetime,
        frequency: BillingFrequency,
        periods: int = 1,
        end_date: Optional[datetime] = None,
        align_to_calendar: bool = False,
        extend_for_partial: bool = False,
        min_days: Optional[int] = None
    ) -> datetime:
        """
        Extended version of get_period_end with additional features.
        
        Args:
            start_date: Start date of the period
            frequency: Billing frequency
            periods: Number of periods to calculate
            end_date: Optional maximum end date
            align_to_calendar: If True, align to calendar boundaries
            extend_for_partial: If True, extend period for partial periods
            min_days: Minimum number of days required for a period
            
        Returns:
            datetime: Calculated period end date
        """
        # Get initial period end
        period_end = DateService.get_period_end(
            start_date=start_date,
            frequency=frequency,
            periods=periods,
            end_date=None,  # Handle end_date separately
            align_to_calendar=align_to_calendar
        )
        
        if frequency == BillingFrequency.ONE_TIME:
            return min(period_end, end_date) if end_date else period_end
            
        # Handle minimum days requirement
        if min_days is not None:
            days_in_period = (period_end - start_date).days + 1
            if days_in_period < min_days:
                if frequency == BillingFrequency.DAILY:
                    period_end = start_date + timedelta(days=min_days - 1)
                elif frequency == BillingFrequency.WEEKLY:
                    weeks_needed = (min_days + 6) // 7  # Round up
                    period_end = start_date + timedelta(weeks=weeks_needed - 1)
                else:  # MONTHLY
                    months = 1
                    while days_in_period < min_days:
                        months += 1
                        next_end = DateService.get_period_end(
                            start_date=start_date,
                            frequency=frequency,
                            periods=months,
                            align_to_calendar=align_to_calendar
                        )
                        days_in_period = (next_end - start_date).days + 1
                    period_end = next_end
        
        # Handle end date constraint
        if end_date and period_end > end_date:
            days_to_end = (end_date - start_date).days + 1
            
            if extend_for_partial:
                # Check if we should extend to next period
                if frequency == BillingFrequency.WEEKLY:
                    days_in_week = 7
                    if days_to_end % days_in_week >= days_in_week / 2:
                        # Extend to end of week
                        days_to_add = days_in_week - (days_to_end % days_in_week)
                        extended_end = end_date + timedelta(days=days_to_add)
                        if extended_end <= period_end:
                            return extended_end
                            
                elif frequency == BillingFrequency.MONTHLY:
                    # Calculate days in current month
                    if end_date.month == 12:
                        next_month = end_date.replace(year=end_date.year + 1, month=1, day=1)
                    else:
                        next_month = end_date.replace(month=end_date.month + 1, day=1)
                    days_in_month = (next_month - end_date.replace(day=1)).days
                    
                    days_used = end_date.day
                    if days_used >= days_in_month / 2:
                        # Extend to end of month
                        extended_end = next_month - timedelta(days=1)
                        if extended_end <= period_end:
                            if align_to_calendar:
                                extended_end = extended_end.replace(
                                    hour=23, minute=59, second=59, microsecond=999999
                                )
                            return extended_end
            
            # If not extending or extension not possible, return end_date
            if align_to_calendar:
                return end_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            return end_date
            
        return period_end
