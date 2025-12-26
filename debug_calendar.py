"""
Debug script to check what's happening with calendar events
"""

from calendar_tools.calendar_operations import list_upcoming_events, create_event
from datetime import datetime
# here you findout what's going wrong with your calendar operations
print("DEBUGGING CALENDAR ISSUE")

# Test 1: List current events
print("\n1. Listing all upcoming events...")
result = list_upcoming_events(max_results=20)
print(f"Found {result['event_count']} events")

if result['success'] and result['events']:
    print("\nYour events:")
    for event in result['events'][:5]:  # Show first 5
        print(f"  • {event['summary']}")
        print(f"    Time: {event['start']}")
        print(f"    ID: {event['id']}")
        print()

# Test 2: Try creating a test event
print("\n2. Creating a test event...")
test_result = create_event(
    summary="test for nour",
start_datetime="2025-12-16T10:00:00",
end_datetime="2025-12-16T11:00:00",
description="test test"
)

print(f"Success: {test_result['success']}")
if test_result['success']:
    print(f"Event ID: {test_result['event_id']}")
    print(f"Link: {test_result['link']}")
    print("\n✅ Check your calendar now - do you see 'TEST - Calendar Debug' on Dec 15?")
else:
    print(f"Error: {test_result.get('error')}")

print("\n" + "="*70)