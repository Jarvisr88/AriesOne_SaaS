from datetime import datetime
from typing import List, Optional
import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from fastapi import HTTPException

from ..models.calendar_event import CalendarEvent, EventReminders, EventReminder

class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.creds = None
        self.service = None
        
    async def initialize(self):
        """Initialize Google Calendar service with credentials"""
        credentials_path = Path.home() / '.credentials' / 'calendar-credentials.json'
        token_path = Path.home() / '.credentials' / 'token.json'
        
        if token_path.exists():
            self.creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not credentials_path.exists():
                    raise HTTPException(
                        status_code=500,
                        detail="Google Calendar credentials not found"
                    )
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path),
                    self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(self.creds.to_json())
            
        self.service = build('calendar', 'v3', credentials=self.creds)
        
    async def list_calendars(self, show_hidden: bool = False) -> List[dict]:
        """List available calendars"""
        if not self.service:
            await self.initialize()
            
        results = []
        page_token = None
        
        while True:
            calendar_list = self.service.calendarList().list(
                showHidden=show_hidden,
                pageToken=page_token
            ).execute()
            
            for calendar in calendar_list['items']:
                results.append({
                    'id': calendar['id'],
                    'summary': calendar.get('summaryOverride', calendar['summary']),
                    'primary': calendar.get('primary', False)
                })
                
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
                
        return results
        
    async def create_event(self, event: CalendarEvent) -> dict:
        """Create a new calendar event"""
        if not self.service:
            await self.initialize()
            
        event_body = {
            'summary': event.summary,
            'description': event.description,
            'start': {
                'dateTime': event.start_time.isoformat(),
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': event.end_time.isoformat(),
                'timeZone': 'UTC'
            },
            'reminders': {
                'useDefault': event.reminders.use_default,
                'overrides': [
                    {
                        'method': r.method,
                        'minutes': r.minutes
                    } for r in event.reminders.overrides
                ] if event.reminders.overrides else None
            }
        }
        
        try:
            result = self.service.events().insert(
                calendarId=event.calendar_id,
                body=event_body
            ).execute()
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create calendar event: {str(e)}"
            )
