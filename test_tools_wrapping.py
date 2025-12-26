"""
Test LangChain tool wrappers
Verify tools can be called correctly
"""
# Testing the tool wrappers is crucial to ensure they function as expected within a LangChain agent.
# So you can proceed with your work without worrying about tool integration issues later on.
from agent.tools import create_calendar_tools, get_tool_descriptions
import json


def main():
    print(" 🔧 TESTING LANGCHAIN TOOL WRAPPERS")
    
    # Create tools
    tools = create_calendar_tools()
    print(f"✓ Created {len(tools)} tools\n")
    
    # Print tool descriptions
    print(get_tool_descriptions())
    print()
    
    # Test 1: List upcoming events
    
    print("TEST 1: List Upcoming Events")
    
    
    list_tool = next(t for t in tools if t.name == "list_upcoming_events")
    result = list_tool.func("5") # type: ignore
    print(result)
    
    # Test 2: Get daily report
    
    print("TEST 2: Daily Report")
    
    
    report_tool = next(t for t in tools if t.name == "get_daily_report")
    result = report_tool.func("2025-12-05") # type: ignore
    print(result)
    
    # Test 3: Check availability
    print("TEST 3: Check Availability")
    
    
    avail_tool = next(t for t in tools if t.name == "check_availability")
    test_input = json.dumps({
        "start_datetime": "2025-12-06T10:00:00",
        "end_datetime": "2025-12-06T11:00:00"
    })
    result = avail_tool.func(test_input) # type: ignore
    print(result)
    
    print("✅ ALL TOOL WRAPPER TESTS COMPLETED!")


if __name__ == "__main__":
    main()