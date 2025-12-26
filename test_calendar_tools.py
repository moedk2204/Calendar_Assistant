"""
Test script for Calendar Tools
Run this to test all calendar operations
"""
# testing before gradio integration is very important 
from datetime import datetime, timedelta
from calendar_tools.calendar_operations import (
    create_event,
    delete_event,
    check_availability,
    get_daily_report,
    list_upcoming_events
)
import json


def print_result(title: str, result: dict):
    """Pretty print test results"""
    print(f"📋 {title}")
    print(json.dumps(result, indent=2))
    print()


def main():
    print(" 🧪 CALENDAR TOOLS TEST SUITE")
    
    # Test 1: List Upcoming Events
    print("\n1️⃣ Testing: List Upcoming Events")
    result = list_upcoming_events(max_results=5)
    print_result("Upcoming Events", result)
    
    # Test 2: Get Daily Report (Today)
    print("\n2️⃣ Testing: Daily Report (Today)")
    today = datetime.now().strftime('%Y-%m-%d')
    result = get_daily_report(date=today)
    print_result(f"Daily Report for {today}", result)
    
    # Test 3: Check Availability (Tomorrow 10-11 AM)
    print("\n3️⃣ Testing: Check Availability")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_time = f"{tomorrow}T10:00:00"
    end_time = f"{tomorrow}T11:00:00"
    result = check_availability(start_time, end_time)
    print_result(f"Availability Check: {start_time} to {end_time}", result)
    
    # Test 4: Create Event
    print("\n4️⃣ Testing: Create Event")
    result = create_event(
        summary="Test Event - Calendar Assistant",
        start_datetime=start_time,
        end_datetime=end_time,
        description="This is a test event created by Calendar Assistant",
        location="Virtual Meeting"
    )
    print_result("Event Creation", result)
    
    if result["success"]:
        event_id = result["event_id"]
        
        # Test 5: Check Availability Again (should show conflict)
        print("\n5️⃣ Testing: Check Availability After Creating Event")
        result = check_availability(start_time, end_time)
        print_result("Availability Check (Should Show Conflict)", result)
        
        
        
        # Test 7: Check Availability One More Time
        print("\n7️⃣ Testing: Final Availability Check")
        result = check_availability(start_time, end_time)
        print_result("Final Availability Check (Should Be Available)", result)
    
    print("✅ ALL TESTS COMPLETED!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during tests: {e}")