"""
Timezone Service Module

This module handles timezone conversions and management.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo, available_timezones
from pydantic import BaseModel

class TimezoneInfo(BaseModel):
    """Timezone information"""
    name: str
    offset: str
    current_time: datetime
    dst_active: bool

class TimezoneService:
    """Service for timezone management"""

    @staticmethod
    def get_available_timezones() -> List[str]:
        """Get list of available timezones"""
        return sorted(available_timezones())

    @staticmethod
    def get_timezone_info(timezone_name: str) -> TimezoneInfo:
        """Get timezone information"""
        tz = ZoneInfo(timezone_name)
        now = datetime.now(tz)
        
        return TimezoneInfo(
            name=timezone_name,
            offset=now.strftime('%z'),
            current_time=now,
            dst_active=bool(now.dst())
        )

    @staticmethod
    def convert_timezone(
        dt: datetime,
        from_tz: str,
        to_tz: str
    ) -> datetime:
        """Convert datetime between timezones"""
        from_zone = ZoneInfo(from_tz)
        to_zone = ZoneInfo(to_tz)
        
        # Ensure datetime is timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=from_zone)
        
        return dt.astimezone(to_zone)

    @staticmethod
    def is_dst(dt: datetime, timezone_name: str) -> bool:
        """Check if date is in DST for timezone"""
        tz = ZoneInfo(timezone_name)
        return bool(dt.replace(tzinfo=tz).dst())
