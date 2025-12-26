"""
LangChain Tool Wrappers for Calendar Operations
Wraps calendar functions into LangChain-compatible tools
"""

from langchain.tools import Tool
from typing import List
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from calendar_tools.calendar_operations import (
    create_event,
    delete_event,
    check_availability,
    get_daily_report,
    list_upcoming_events,
    update_event
)


def format_create_event_result(result: dict) -> str:
    """Format create_event result for LLM consumption"""
    if not result.get("success"):
        return f"❌ Failed to create event: {result.get('error', 'Unknown error')}"
    
    return (
        f"✅ Event created successfully!\n"
        f"📅 {result['summary']}\n"
        f"🕐 Start: {result['start']}\n"
        f"🕑 End: {result['end']}\n"
        f"🔗 Link: {result['link']}\n"
        f"🆔 Event ID: {result['event_id']}\n\n"
        f"Event ID: {result['event_id']}\n"
        f"Link: {result['link']}"
    )


def format_delete_event_result(result: dict) -> str:
    """Format delete_event result for LLM consumption"""
    if not result.get("success"):
        return f"❌ Failed to delete event: {result.get('error', 'Unknown error')}"
    
    return f"✅ {result['message']}"


def format_availability_result(result: dict) -> str:
    """Format check_availability result for LLM consumption"""
    if not result.get("success"):
        return f"❌ Error checking availability: {result.get('error', 'Unknown error')}"
    
    if result.get("available"):
        return f"✅ Time slot is AVAILABLE ({result['start']} to {result['end']})"
    
    conflicts = result.get("conflicting_events", [])
    lines = [f"⚠️ Time slot is NOT AVAILABLE ({result['start']} to {result['end']})"]
    lines.append(f"Found {len(conflicts)} conflicting event(s):")
    
    for event in conflicts:
        lines.append(f"  • {event['summary']} ({event['start']} - {event['end']})")
    
    return "\n".join(lines)


def format_daily_report_result(result: dict) -> str:
    """Format get_daily_report result for LLM consumption"""
    if not result.get("success"):
        return f"❌ Error generating report: {result.get('error', 'Unknown error')}"
    
    lines = [f"📅 Daily Report for {result['date']}"]
    lines.append(f"{result['summary']}")
    
    events = result.get("events", [])
    if events:
        lines.append("\nEvents:")
        for i, event in enumerate(events, 1):
            lines.append(f"\n{i}. {event['summary']}")
            lines.append(f"   Time: {event['start']} - {event['end']}")
            if event.get('location'):
                lines.append(f"   Location: {event['location']}")
            if event.get('description'):
                lines.append(f"   Description: {event['description'][:100]}...")
            if event.get('link'):
                lines.append(f"   Link: {event['link']}")
    
    return "\n".join(lines)


def format_upcoming_events_result(result: dict) -> str:
    """Format list_upcoming_events result for LLM consumption"""
    if not result.get("success"):
        return f"❌ Error listing events: {result.get('error', 'Unknown error')}"
    
    events = result.get("events", [])
    if not events:
        return "📅 No upcoming events found."
    
    lines = [f"📅 Upcoming Events ({result['event_count']} total):"]
    
    for i, event in enumerate(events, 1):
        lines.append(f"\n{i}. {event['summary']}")
        lines.append(f"   Time: {event['start']} - {event['end']}")
        if event.get('location'):
            lines.append(f"   Location: {event['location']}")
        if event.get('link'):
            lines.append(f"   Link: {event['link']}")
        lines.append(f"   ID: {event['id']}")
    
    return "\n".join(lines)


# Tool wrapper functions that parse input strings and call calendar functions

def create_event_tool(tool_input: str) -> str:
    """
    Tool wrapper for creating calendar events
    Expects JSON string with: summary, start_datetime, end_datetime, description, location
    """
    import json
    try:
        params = json.loads(tool_input)
        result = create_event(**params)
        return format_create_event_result(result)
    except json.JSONDecodeError:
        return "❌ Invalid input format. Please provide valid JSON with event details."
    except Exception as e:
        return f"❌ Error: {str(e)}"


def delete_event_tool(tool_input: str) -> str:
    """
    Tool wrapper for deleting calendar events.
    Handles both raw ID strings and JSON with 'event_id'.
    """
    import json
    event_id = tool_input.strip()
    
    # Try to parse as JSON in case agent got confused
    if event_id.startswith('{'):
        try:
            params = json.loads(event_id)
            if 'event_id' in params:
                event_id = params['event_id']
            elif 'id' in params:
                event_id = params['id']
        except json.JSONDecodeError:
            pass # Use raw input if JSON is invalid
            
    result = delete_event(event_id)
    return format_delete_event_result(result)


def check_availability_tool(tool_input: str) -> str:
    """
    Tool wrapper for checking availability
    Expects JSON string with: start_datetime, end_datetime
    """
    import json
    try:
        params = json.loads(tool_input)
        result = check_availability(**params)
        return format_availability_result(result)
    except json.JSONDecodeError:
        return "❌ Invalid input format. Please provide valid JSON with start_datetime and end_datetime."
    except Exception as e:
        return f"❌ Error: {str(e)}"


def daily_report_tool(date: str) -> str:
    """Tool wrapper for getting daily reports"""
    clean_date = date.strip().strip('"').strip("'") if date else None
    result = get_daily_report(clean_date)
    return format_daily_report_result(result)


def upcoming_events_tool(max_results: str = "10") -> str:
    """Tool wrapper for listing upcoming events"""
    try:
        # Strip quotes and whitespace if LLM provided them
        clean_input = max_results.strip().strip('"').strip("'")
        max_count = int(clean_input) if clean_input else 10
        result = list_upcoming_events(max_results=max_count)
        return format_upcoming_events_result(result)
    except (ValueError, TypeError):
        return "❌ max_results must be a number (integer)"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def update_event_tool(tool_input: str) -> str:
    """
    Tool wrapper for updating calendar events
    Expects JSON string with: event_id (required), and optional summary, start_datetime, end_datetime, description, location
    """
    import json
    try:
        params = json.loads(tool_input)
        if 'event_id' not in params:
            return "❌ Missing required field: 'event_id'"
        result = update_event(**params)
        if not result.get("success"):
            return f"❌ Failed to update event: {result.get('error', 'Unknown error')}"
        return f"✅ Event updated successfully!\n📅 {result['summary']}\n🕐 Start: {result['start']}\n🕑 End: {result['end']}"
    except json.JSONDecodeError:
        return "❌ Invalid input format. Please provide valid JSON."
    except Exception as e:
        return f"❌ Error: {str(e)}"


def create_calendar_tools() -> List[Tool]:
    """
    Create LangChain Tool objects for all calendar operations
    
    Returns:
        List[Tool]: LangChain tools ready for agent use
    """
    tools = [
        Tool(
            name="create_event",
            func=create_event_tool,
            description=(
                "Create a new calendar event. "
                "Input must be JSON with these fields: "
                '{"summary": "Event Title", "start_datetime": "2025-12-05T10:00:00", '
                '"end_datetime": "2025-12-05T11:00:00", '
                '"description": "Optional description", "location": "Optional location"}. '
                "IMPORTANT: Use ISO format for datetimes (YYYY-MM-DDTHH:MM:SS). "
                "Returns event ID and details if successful."
            )
        ),
        Tool(
            name="delete_event",
            func=delete_event_tool,
            description=(
                "Delete a calendar event by its ID. "
                "Input should be the event ID (string). "
                "CRITICAL: You MUST get the event ID from list_upcoming_events or daily_report first. "
                "NEVER make up or guess event IDs. "
                "Returns success/failure message."
            )
        ),
        Tool(
              name="check_availability",
              func=check_availability_tool,
              description=(
        "Check if a time slot is available (no conflicting events). "
        "Input MUST be valid JSON string with escaped quotes: "
        '{\\"start_datetime\\":\\"2025-12-05T10:00:00\\",\\"end_datetime\\":\\"2025-12-05T11:00:00\\"}. '
        "OR use single quotes for JSON: "
        "{'start_datetime':'2025-12-05T10:00:00','end_datetime':'2025-12-05T11:00:00'}. "
        "Returns whether slot is available and lists conflicts."
           )
        ),
        Tool(
            name="get_daily_report",
            func=daily_report_tool,
            description=(
                "Get a report of all events for a specific date. "
                "Input should be date in YYYY-MM-DD format (e.g., '2025-12-05'). "
                "If no date provided, returns today's events. "
                "Returns list of all events with details."
            )
        ),
        Tool(
            name="list_upcoming_events",
            func=upcoming_events_tool,
            description=(
                "List upcoming calendar events from now. "
                "Input should be max number of events to return (default: 10). "
                "Returns list of upcoming events with IDs, times, and locations. "
                "Use this to get event IDs before deleting or updating."
            )
        ),
        Tool(
            name="update_event",
            func=update_event_tool,
            description=(
                "Update an existing calendar event. "
                "Input must be JSON with 'event_id' and any fields to change: summary, start_datetime, end_datetime, description, location. "
                "Example: {'event_id': 'abc', 'summary': 'New Title'}. "
                "CRITICAL: Get event_id from list_upcoming_events first."
            )
        )
    ]
    
    return tools


def get_tool_descriptions() -> str:
    """Get a formatted string describing all available tools"""
    descriptions = [
        "Available Calendar Tools:",
        "",
        "1. create_event - Create new calendar events with title, time, location",
        "2. delete_event - Delete events by ID (get ID from list_upcoming_events first)",
        "3. check_availability - Check if a time slot is free",
        "4. get_daily_report - Get all events for a specific date",
        "5. list_upcoming_events - List next N upcoming events with IDs",
        "6. update_event - Update an existing event by its ID",
        "",
        "CRITICAL RULES:",
        "- Always use ISO format for dates: YYYY-MM-DDTHH:MM:SS",
        "- NEVER guess or make up event IDs - always get them from tools first",
        "- Use check_availability before creating or moving events to avoid conflicts",
    ]
    return "\n".join(descriptions)


if __name__ == "__main__":
    # Test tool creation
    tools = create_calendar_tools()
    print(f"✓ Created {len(tools)} LangChain tools")
    print("\nTools:")
    for tool in tools:
        print(f"  • {tool.name}: {tool.description[:80]}...")
    
    print("\n" + get_tool_descriptions())