"""
Google Calendar OAuth Authentication
Handles OAuth 2.0 flow and token management
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Scopes required for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

# File paths
PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / 'credentials.json'
TOKEN_FILE = PROJECT_ROOT / 'token.json'


def get_calendar_service():
    """
    Authenticate and return Google Calendar service
    
    This function:
    1. Checks if token.json exists (previously authenticated)
    2. If exists and valid, uses it
    3. If expired, refreshes it
    4. If missing, runs OAuth flow to generate new token
    
    Returns:
        googleapiclient.discovery.Resource: Calendar service object
    
    Raises:
        FileNotFoundError: If credentials.json is missing
        Exception: If authentication fails
    """
    creds = None
    
    # Check if credentials.json exists
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"credentials.json not found at {CREDENTIALS_FILE}\n"
            "Please download it from Google Cloud Console:\n"
            "1. Go to https://console.cloud.google.com/\n"
            "2. Select your project\n"
            "3. Go to APIs & Services > Credentials\n"
            "4. Download OAuth 2.0 Client ID credentials\n"
            "5. Save as 'credentials.json' in project root"
        )
    
    # Load existing token if available
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            print("✓ Loaded existing token.json")
        except Exception as e:
            print(f"⚠ Warning: Could not load token.json: {e}")
            creds = None
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Token expired, refresh it
            try:
                print("🔄 Refreshing expired token...")
                creds.refresh(Request())
                print("✓ Token refreshed successfully")
            except Exception as e:
                print(f"⚠ Could not refresh token: {e}")
                print("⚠ Starting new OAuth flow...")
                creds = None
        
        if not creds:
            # Run OAuth flow
            print("\n" + "="*60)
            print("🔐 GOOGLE OAUTH AUTHENTICATION REQUIRED")
            print("="*60)
            print("A browser window will open for you to:")
            print("1. Select your Google account")
            print("2. Grant calendar access permissions")
            print("3. Return to this application")
            print("="*60 + "\n")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), 
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
                print("\n✓ Authentication successful!")
            except Exception as e:
                raise Exception(f"OAuth flow failed: {e}")
        
        # Save credentials for next time
        try:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            print(f"✓ Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"⚠ Warning: Could not save token: {e}")
    
    # Build and return calendar service
    try:
        service = build('calendar', 'v3', credentials=creds)
        print("✓ Google Calendar service initialized")
        return service
    except HttpError as error:
        raise Exception(f"Failed to build calendar service: {error}")


def test_calendar_connection():
    """
    Test the calendar connection by fetching calendar list
    
    Returns:
        bool: True if connection successful
    """
    try:
        service = get_calendar_service()
        
        # Try to list calendars
        print("\n" + "="*60)
        print("📅 TESTING CALENDAR CONNECTION")
        print("="*60)
        
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if not calendars:
            print("⚠ No calendars found")
            return False
        
        print(f"\n✓ Successfully connected!")
        print(f"✓ Found {len(calendars)} calendar(s):\n")
        
        for calendar in calendars:
            print(f"  📅 {calendar['summary']}")
            print(f"     ID: {calendar['id']}")
            print(f"     Access: {calendar.get('accessRole', 'N/A')}")
            print()
        
        print("="*60)
        print("✅ Calendar connection test PASSED!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test FAILED: {e}\n")
        return False


def revoke_token():
    """
    Revoke the current token (for testing or re-authentication)
    Deletes token.json file
    """
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print(f"✓ Token deleted: {TOKEN_FILE}")
        print("ℹ Run authentication again to generate new token")
    else:
        print("ℹ No token.json found")


if __name__ == "__main__":
    # Quick test
    print("🚀 Google Calendar Authentication Test\n")
    
    try:
        test_calendar_connection()
    except FileNotFoundError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Error: {e}")