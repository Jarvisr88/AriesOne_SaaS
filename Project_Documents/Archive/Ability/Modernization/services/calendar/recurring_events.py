"""
Recurring Events Service Module

This module handles recurring event patterns and calculations.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class RecurrenceFrequency(str, Enum):
    """Recurrence frequency types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class WeekDay(str, Enum):
    """Days of the week"""
    MONDAY = "MO"
    TUESDAY = "TU"
    WEDNESDAY = "WE"
    THURSDAY = "TH"
    FRIDAY = "FR"
    SATURDAY = "SA"
    SUNDAY = "SU"

class MonthlyRecurrenceType(str, Enum):
    """Monthly recurrence types"""
    DAY_OF_MONTH = "day_of_month"
    DAY_OF_WEEK = "day_of_week"

class RecurrencePattern(BaseModel):
    """Recurrence pattern definition"""
    pattern_id: UUID = Field(default_factory=uuid4)
    frequency: RecurrenceFrequency
    interval: int = 1
    week_days: Optional[List[WeekDay]] = None
    monthly_type: Optional[MonthlyRecurrenceType] = None
    day_of_month: Optional[int] = None
    week_of_month: Optional[int] = None
    month_of_year: Optional[int] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    count: Optional[int] = None
    exceptions: List[datetime] = Field(default_factory=list)

class RecurringEventService:
    """Service for managing recurring events"""

    def calculate_occurrences(
        self,
        pattern: RecurrencePattern,
        start: datetime,
        end: datetime
    ) -> List[datetime]:
        """Calculate event occurrences based on pattern"""
        occurrences = []
        current = pattern.start_date

        while (
            current <= end and
            (pattern.end_date is None or current <= pattern.end_date) and
            (pattern.count is None or len(occurrences) < pattern.count)
        ):
            if current >= start and current not in pattern.exceptions:
                if self._matches_pattern(current, pattern):
                    occurrences.append(current)

            current = self._next_potential_occurrence(current, pattern)

        return occurrences

    def _matches_pattern(
        self,
        dt: datetime,
        pattern: RecurrencePattern
    ) -> bool:
        """Check if date matches recurrence pattern"""
        if pattern.frequency == RecurrenceFrequency.DAILY:
            return True

        elif pattern.frequency == RecurrenceFrequency.WEEKLY:
            if not pattern.week_days:
                return True
            return WeekDay(dt.strftime("%A")[:2].upper()) in pattern.week_days

        elif pattern.frequency == RecurrenceFrequency.MONTHLY:
            if pattern.monthly_type == MonthlyRecurrenceType.DAY_OF_MONTH:
                return dt.day == pattern.day_of_month
            else:  # DAY_OF_WEEK
                week_of_month = (dt.day - 1) // 7 + 1
                return (
                    WeekDay(dt.strftime("%A")[:2].upper()) in pattern.week_days and
                    week_of_month == pattern.week_of_month
                )

        elif pattern.frequency == RecurrenceFrequency.YEARLY:
            return (
                dt.month == pattern.month_of_year and
                dt.day == pattern.day_of_month
            )

        return False

    def _next_potential_occurrence(
        self,
        dt: datetime,
        pattern: RecurrencePattern
    ) -> datetime:
        """Calculate next potential occurrence"""
        if pattern.frequency == RecurrenceFrequency.DAILY:
            return dt + timedelta(days=pattern.interval)

        elif pattern.frequency == RecurrenceFrequency.WEEKLY:
            return dt + timedelta(days=7 * pattern.interval)

        elif pattern.frequency == RecurrenceFrequency.MONTHLY:
            year = dt.year + ((dt.month + pattern.interval - 1) // 12)
            month = (dt.month + pattern.interval - 1) % 12 + 1
            return dt.replace(year=year, month=month)

        elif pattern.frequency == RecurrenceFrequency.YEARLY:
            return dt.replace(year=dt.year + pattern.interval)

        return dt

    def add_exception(
        self,
        pattern: RecurrencePattern,
        date: datetime
    ) -> RecurrencePattern:
        """Add exception date to pattern"""
        if date not in pattern.exceptions:
            pattern.exceptions.append(date)
        return pattern

    def remove_exception(
        self,
        pattern: RecurrencePattern,
        date: datetime
    ) -> RecurrencePattern:
        """Remove exception date from pattern"""
        if date in pattern.exceptions:
            pattern.exceptions.remove(date)
        return pattern
