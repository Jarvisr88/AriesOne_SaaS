"""
Calendar Utilities Module
Provides helper functions for calendar operations.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pytz import timezone
from ..models.calendar_event_model import ReminderConfig

def validate_time_range(start: datetime, end: datetime) -> bool:
    """
    Validate time range for events.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not start or not end:
        return False
    if end <= start:
        return False
    if (end - start) > timedelta(days=365):
        return False
    return True

def format_reminder_for_google(
    reminders: List[ReminderConfig]
) -> Dict[str, Any]:
    """
    Format reminders for Google Calendar API.
    
    Args:
        reminders: List of reminder configurations
        
    Returns:
        dict: Formatted reminder data
    """
    return {
        'useDefault': False,
        'overrides': [
            {
                'method': reminder.method,
                'minutes': reminder.minutes
            }
            for reminder in reminders
        ]
    }

def convert_timezone(
    dt: datetime,
    from_tz: str,
    to_tz: str = 'UTC'
) -> datetime:
    """
    Convert datetime between timezones.
    
    Args:
        dt: Datetime to convert
        from_tz: Source timezone
        to_tz: Target timezone
        
    Returns:
        datetime: Converted datetime
    """
    source = timezone(from_tz)
    target = timezone(to_tz)
    
    if dt.tzinfo is None:
        dt = source.localize(dt)
    
    return dt.astimezone(target)

def create_default_reminders() -> List[ReminderConfig]:
    """
    Create default reminder configuration.
    
    Returns:
        List[ReminderConfig]: Default reminders
    """
    return [
        ReminderConfig(method='email', minutes=15),
        ReminderConfig(method='popup', minutes=15),
        ReminderConfig(method='sms', minutes=15)
    ]

def format_event_for_google(
    summary: str,
    description: str,
    start: datetime,
    end: datetime,
    timezone_str: str = 'UTC',
    reminders: List[ReminderConfig] = None
) -> Dict[str, Any]:
    """
    Format event data for Google Calendar API.
    
    Args:
        summary: Event summary
        description: Event description
        start: Start datetime
        end: End datetime
        timezone_str: Timezone string
        reminders: List of reminders
        
    Returns:
        dict: Formatted event data
    """
    if not reminders:
        reminders = create_default_reminders()
    
    return {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': timezone_str
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': timezone_str
        },
        'reminders': format_reminder_for_google(reminders)
    }

def parse_google_datetime(
    dt_str: str,
    tz_str: str = 'UTC'
) -> datetime:
    """
    Parse datetime from Google Calendar API.
    
    Args:
        dt_str: Datetime string
        tz_str: Timezone string
        
    Returns:
        datetime: Parsed datetime
    """
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    if tz_str != 'UTC':
        dt = convert_timezone(dt, 'UTC', tz_str)
    return dt
