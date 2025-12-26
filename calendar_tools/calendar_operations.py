"""
Google Calendar Operations
Core functions for creating, reading, updating, and deleting calendar events
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from xmlrpc.client import _datetime
import pytz
from googleapiclient.errors import HttpError

from auth.google_auth import get_calendar_service


# Default calendar ID (primary calendar)
DEFAULT_CALENDAR_ID = 'primary'
# Default timezone
DEFAULT_TIMEZONE = 'Asia/Beirut'


def create_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    calendar_id: str = DEFAULT_CALENDAR_ID
) -> Dict[str, Any]:
    """
    Create a new calendar event
    """
    try:
        service = get_calendar_service()
        
        # Build event body
        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_datetime,
                'timeZone': DEFAULT_TIMEZONE,
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': DEFAULT_TIMEZONE,
            },
        }
        
        # Add optional fields
        if description:
            event_body['description'] = description
        
        if location:
            event_body['location'] = location
        
        if attendees:
            event_body['attendees'] = [{'email': email} for email in attendees]
        
        # Create event
        event = service.events().insert(
            calendarId=calendar_id,
            body=event_body,
            sendUpdates='all' if attendees else 'none'
        ).execute()
        
        return {
            "success": True,
            "event_id": event.get('id'),
            "summary": event.get('summary'),
            "start": event['start'].get('dateTime', event['start'].get('date')),
            "end": event['end'].get('dateTime', event['end'].get('date')),
            "link": event.get('htmlLink'),
            "message": f"✓ Event '{summary}' created successfully"
        }
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"HTTP error: {error.resp.status} - {error.error_details}",
            "summary": summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": summary
        }


def update_event(
    event_id: str,
    summary: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = DEFAULT_CALENDAR_ID
) -> Dict[str, Any]:
    """
    Update an existing calendar event (patch)
    
    Args:
        event_id (str): Event ID to update
        summary (str, optional): New title
        start_datetime (str, optional): New start time
        end_datetime (str, optional): New end time
        description (str, optional): New description
        location (str, optional): New location
        calendar_id (str): Calendar ID
    """
    try:
        service = get_calendar_service()
        
        # Build patch body
        patch_body = {}
        if summary: patch_body['summary'] = summary
        if start_datetime: patch_body['start'] = {'dateTime': start_datetime, 'timeZone': DEFAULT_TIMEZONE}
        if end_datetime: patch_body['end'] = {'dateTime': end_datetime, 'timeZone': DEFAULT_TIMEZONE}
        if description: patch_body['description'] = description
        if location: patch_body['location'] = location
        
        # Update event
        updated_event = service.events().patch(
            calendarId=calendar_id,
            eventId=event_id,
            body=patch_body
        ).execute()
        
        return {
            "success": True,
            "event_id": updated_event.get('id'),
            "summary": updated_event.get('summary'),
            "start": updated_event['start'].get('dateTime', updated_event['start'].get('date')),
            "end": updated_event['end'].get('dateTime', updated_event['end'].get('date')),
            "message": f"✓ Event '{event_id}' updated successfully"
        }
    except HttpError as error:
        return {
            "success": False,
            "error": f"HTTP error: {error.resp.status} - {error.error_details}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def delete_event(
    event_id: str,
    calendar_id: str = DEFAULT_CALENDAR_ID
) -> Dict[str, Any]:
    """
    Delete a calendar event
    
    Args:
        event_id (str): Event ID to delete
        calendar_id (str): Calendar ID (default: 'primary')
    
    Returns:
        dict: {
            "success": bool,
            "event_id": str,
            "message": str,
            "error": str (if failed)
        }
    
    Example:
        >>> delete_event("abc123")
        {
            "success": True,
            "event_id": "abc123",
            "message": "✓ Event deleted successfully"
        }
    """
    try:
        service = get_calendar_service()
        
        # Delete the event
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        return {
            "success": True,
            "event_id": event_id,
            "message": f"✓ Event '{event_id}' deleted successfully"
        }
        
    except HttpError as error:
        if error.resp.status == 404:
            return {
                "success": False,
                "event_id": event_id,
                "error": f"Event '{event_id}' not found"
            }
        return {
            "success": False,
            "event_id": event_id,
            "error": f"HTTP error: {error.resp.status} - {error.error_details}"
        }
    except Exception as e:
        return {
            "success": False,
            "event_id": event_id,
            "error": str(e)
        }


def check_availability(
    start_datetime: str,
    end_datetime: str,
    calendar_id: str = DEFAULT_CALENDAR_ID
) -> Dict[str, Any]:
    """
    Check if a time slot is available (no conflicting events)
    
    Args:
        start_datetime (str): Start time in ISO format
        end_datetime (str): End time in ISO format
        calendar_id (str): Calendar ID (default: 'primary')
    
    Returns:
        dict: {
            "success": bool,
            "available": bool,
            "start": str,
            "end": str,
            "conflicting_events": list (if not available),
            "error": str (if failed)
        }
    """
    try:
        service = get_calendar_service()
        
        # Ensure datetime strings have timezone. If no timezone, assume DEFAULT_TIMEZONE.
        tz = pytz.timezone(DEFAULT_TIMEZONE)
        
        def localize_if_needed(dt_str):
            if 'Z' in dt_str or '+' in dt_str:
                return dt_str
            # Parse and localize
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            return dt.isoformat()

        start_datetime = localize_if_needed(start_datetime)
        end_datetime = localize_if_needed(end_datetime)
        
        # Get events in the time range
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_datetime,
            timeMax=end_datetime,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return {
                "success": True,
                "available": True,
                "start": start_datetime,
                "end": end_datetime,
                "message": "✓ Time slot is available"
            }
        
        # Format conflicting events
        conflicts = []
        for event in events: # type: ignore
            conflicts.append({
                "id": event.get('id'),
                "summary": event.get('summary', 'Untitled Event'),
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date'))
            })
        
        return {
            "success": True,
            "available": False,
            "start": start_datetime,
            "end": end_datetime,
            "conflicting_events": conflicts,
            "message": f"⚠ Time slot has {len(conflicts)} conflicting event(s)"
        }
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"HTTP error: {error.resp.status} - {error.error_details}",
            "start": start_datetime,
            "end": end_datetime
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "start": start_datetime,
            "end": end_datetime
        }

def get_daily_report(
    date: Optional[str] = None,
    calendar_id: str = DEFAULT_CALENDAR_ID
) -> Dict[str, Any]:
    """
    Get a daily report of all events for a specific date

    Args:
        date (str, optional): Date in ISO format (YYYY-MM-DD). Defaults to today.
        calendar_id (str): Calendar ID (default: 'primary')
    
    Returns:
        dict: {
            "success": bool,
            "date": str,
            "event_count": int,
            "events": list of dicts,
            "summary": str,
            "error": str (if failed)
        }
    
    Example:
        >>> get_daily_report("2024-12-05")
        {
            "success": True,
            "date": "2024-12-05",
            "event_count": 3,
            "events": [
                {
                    "id": "abc123",
                    "summary": "Team Meeting",
                    "start": "2024-12-05T10:00:00",
                    "end": "2024-12-05T11:00:00",
                    "location": "Conference Room A"
                },
                ...
            ],
            "summary": "You have 3 events scheduled for 2024-12-05"
        }
    """
    try:
        service = get_calendar_service()
        
        # Use today if no date provided
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Remove any quotes or extra whitespace
        date = date.strip().strip('"').strip("'")
        
        # Build timestamps with proper timezone
        # If we use Z, we are checking UTC day, which is wrong for the user
        tz = pytz.timezone(DEFAULT_TIMEZONE)
        start_dt = tz.localize(datetime.strptime(f"{date} 00:00:00", "%Y-%m-%d %H:%M:%S"))
        end_dt = tz.localize(datetime.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S"))
        
        start_of_day = start_dt.isoformat()
        end_of_day = end_dt.isoformat()
        
        print(f"DEBUG: Querying calendar from {start_of_day} to {end_of_day}")  # Debug line
        
        # Get events for the day
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events
        formatted_events = []
        for event in events:
            formatted_events.append({
                "id": event.get('id'),
                "summary": event.get('summary', 'Untitled Event'),
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "location": event.get('location'),
                "description": event.get('description'),
                "link": event.get('htmlLink'),
                "attendees": [a.get('email') for a in event.get('attendees', [])]
            })
        
        # Create summary message
        if not events:
            summary = f"No events scheduled for {date}"
        elif len(events) == 1:
            summary = f"You have 1 event scheduled for {date}"
        else:
            summary = f"You have {len(events)} events scheduled for {date}"
        
        return {
            "success": True,
            "date": date,
            "event_count": len(events),
            "events": formatted_events,
            "summary": summary
        }
        
    except HttpError as error:
        return {
            "success": False,
            "date": date,
            "error": f"HTTP error: {error.resp.status} - {error.error_details}"
        }
    except Exception as e:
        return {
            "success": False,
            "date": date,
            "error": str(e)
        }


def list_upcoming_events(
    max_results: int = 10,
    calendar_id: str = DEFAULT_CALENDAR_ID
) -> Dict[str, Any]:
    """
    List upcoming events from now
    
    Args:
        max_results (int): Maximum number of events to return (default: 10)
        calendar_id (str): Calendar ID (default: 'primary')
    
    Returns:
        dict: {
            "success": bool,
            "event_count": int,
            "events": list of dicts,
            "error": str (if failed)
        }
    
    Example:
        >>> list_upcoming_events(max_results=5)
        {
            "success": True,
            "event_count": 5,
            "events": [...]
        }
    """
    try:
        service = get_calendar_service()
        
        # Get current time
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Get upcoming events
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events
        formatted_events = []
        for event in events:
            formatted_events.append({
                "id": event.get('id'),
                "summary": event.get('summary', 'Untitled Event'),
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "location": event.get('location'),
                "link": event.get('htmlLink')
            })
        
        return {
            "success": True,
            "event_count": len(events),
            "events": formatted_events,
            "message": f"Found {len(events)} upcoming event(s)"
        }
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"HTTP error: {error.resp.status} - {error.error_details}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Utility functions

def parse_datetime(datetime_str: str) -> datetime:
    """
    Parse datetime string to datetime object
    
    Supports formats:
    - ISO 8601: "2024-12-05T10:00:00"
    - Date only: "2024-12-05"
    """
    try:
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except ValueError:
        # Try date-only format
        return datetime.strptime(datetime_str, '%Y-%m-%d')


def format_datetime_for_display(datetime_str: str) -> str:
    """
    Format datetime for human-readable display
    
    Args:
        datetime_str: ISO format datetime string
    
    Returns:
        str: Formatted datetime (e.g., "Dec 5, 2024 at 10:00 AM")
    """
    dt = parse_datetime(datetime_str)
    return dt.strftime('%b %d, %Y at %I:%M %p')