"""
Calendar Assistant Agent
Main agent logic with ReAct pattern and tool calling
"""

import sys
from pathlib import Path
from typing import List, Optional
from langchain.agents import AgentExecutor, initialize_agent, AgentType

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.llm import get_ollama_llm
from agent.tools import create_calendar_tools, get_tool_descriptions


from datetime import datetime, timedelta
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

def create_calendar_agent(verbose: bool = True) -> AgentExecutor:
    """
    Create and return a Calendar Assistant agent using ReAct pattern.
    Handles string max_results for upcoming_events_tool and strict ReAct output.
    """
    # Initialize LLM
    llm = get_ollama_llm(temperature=0.1)

    # Load tools
    tools = create_calendar_tools()
    tool_names = [t.name for t in tools]

    # System prompt enforcing strict ReAct
    system_prompt = """You are a Calendar Assistant that helps manage Google Calendar events.

CRITICAL RULES:
1. HISTORY OVER TOOLS: If the answer is already in the `chat_history` (e.g., a link or time you just provided), DO NOT call any tools. Go straight to Final Answer.
2. Always use proper datetime format: YYYY-MM-DDTHH:MM:SS (e.g., 2025-12-10T15:00:00)
3. NEVER invent or guess event IDs - get them from list_upcoming_events first
4. (Optional) check_availability is recommended but not mandatory if the request is specific.
5. GROUNDING RULE: Never invent, guess, or hallucinate events. Only report events that are EXPLICITLY returned by a tool observation.
6. EMPTY CALENDAR: If a tool returns no events for a day, you MUST say: "You are free for [today/tomorrow/date]. If you wish I can help you fulfill your schedule."
7. SPEED: Aim for the Final Answer in as few steps as possible.
8. LINKS: Always include the `htmlLink` in your Final Answer when creating or listing events.
9. NO RE-CREATION: If you just created an event or if history shows it was created, NEVER call `create_event` again for that same request.
10. STRICT ACTION CLAUSE: You must NEVER claim an action (Create, Update, Delete) is done unless you have a REAL tool `Observation` confirming it. If you haven't called the tool yet, your next step MUST be an `Action`.

AVAILABLE TOOLS:
{tools}

TOOL NAMES: {tool_names}

- list_upcoming_events: Input is any integer (e.g., 5)
- get_daily_report: Input is date string in YYYY-MM-DD format
- check_availability: Input is JSON: {{"start_datetime":"...", "end_datetime":"..."}}
- create_event: Input is JSON with summary, start_datetime, etc.
- delete_event: Input is ONLY the event ID (string).
- update_event: Input is JSON with event_id and modifications.

GROUNDING EXAMPLES:
User: "What's on my calendar for 2025-12-25?"
Thought: I should check the daily report for that date.
Action: get_daily_report
Action Input: 2025-12-25
Observation: 📅 Daily Report for 2025-12-25
No events scheduled for 2025-12-25
Thought: The observation confirms the calendar is empty.
Final Answer: You are free for December 25th, 2025. If you wish I can help you fulfill your schedule.

User: "Add 'Meeting' at 3pm today"
Thought: Slot is free, creating event.
Action: create_event
Action Input: {{"summary":"Meeting", "start_datetime":"2025-12-26T15:00:00", "end_datetime":"2025-12-26T16:00:00"}}
Observation: ✅ Event created! Link: https://calendar.google.com/event?eid=abc
Thought: I have the link. I'll include it.
Final Answer: Your "Meeting" has been added for today at 3pm. Link: https://calendar.google.com/event?eid=abc

User: "List my events"
Thought: I'll list upcoming events.
Action: list_upcoming_events
Action Input: 5
Observation: 📅 No upcoming events found.
Thought: The calendar is empty.
Final Answer: You are free! I couldn't find any upcoming events. If you wish I can help you fulfill your schedule.

User: "Move my 2pm meeting to 3pm"
Thought: I need the event ID first.
Action: list_upcoming_events
Action Input: 10
Observation: 📅 Upcoming Events (1 total): 1. Meeting (2025-12-27T14:00:00, ID: abc123)
Thought: I have the ID. Now I will update it.
Action: update_event
Action Input: {{"event_id": "abc123", "start_datetime": "2025-12-27T15:00:00", "end_datetime": "2025-12-27T17:00:00"}}
Observation: ✅ Event updated successfully! New time: 15:00-17:00.
Thought: The update is confirmed.
Final Answer: I've moved your meeting to 3 pm tomorrow.

RESPONSE FORMAT:
You must strictly follow this ReAct loop. DO NOT invent observations.

Thought: [Your reasoning about what to do next]
Action: [tool_name]
Action Input: [input string or JSON]

STOP HERE. The system will provide the Observation.

After the Observation, continue with:

Thought: [Your reasoning about the result]
Final Answer: [Your response to the user. This MUST include the 'Final Answer:' prefix and should include event links if available.]

RULES FOR USER INTERACTION:
- POLITENESS: If the user says "thank you", "thanks", "ok", or similar without a new request, DO NOT call any tools. Just respond politely with "Final Answer: You're welcome!" or "Glad I could help!".
- NO STUTTERING: If you just performed an action and the user is acknowledging it, do not repeat the full confirmation unless they ask for a summary.
- If you need more information (like an end time), DO NOT use a tool. Skip to Final Answer.
- Example for missing info:
  Thought: I need an end time for the routine.
  Final Answer: What time would you like the morning routine to end?
- NEVER write "Observation:".
- Your response MUST END exactly after the Action Input or Final Answer.
- DO NOT explain the format to the user.

CONTEXT:
Current Time (System): {current_time}
Today's Date: {today_date}
Tomorrow's Date: {tomorrow_date}
"""



    # Prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("assistant", "{agent_scratchpad}")
    ])

    # Create agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt.partial(
            tools=get_tool_descriptions(),
            tool_names=tool_names,
            current_time=lambda: datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            today_date=lambda: datetime.now().strftime("%Y-%m-%d"),
            tomorrow_date=lambda: (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        )
    )

    # Wrap in AgentExecutor with safe parsing
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=10,
        max_execution_time=90,
        early_stopping_method="force"

    )



class CalendarAssistantChat:
    """
    Stateful chat interface for the Calendar Assistant
    Maintains conversation history
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize Calendar Assistant chat interface
        
        Args:
            verbose (bool): Enable verbose agent output
        """
        print("\n🗓️  Initializing Calendar Assistant...")
        self.agent = create_calendar_agent(verbose=verbose)
        self.chat_history: List[tuple] = []
        self.verbose = verbose
        print("✅ Calendar Assistant ready!\n")
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return agent response
        """
        try:
            # Format history as objects
            langchain_history = []
            for h in self.chat_history[-5:]: # Keep last 5 turns to avoid context bloat
                langchain_history.append(HumanMessage(content=h[0]))
                langchain_history.append(AIMessage(content=h[1]))
            
            # Run agent
            response = self.agent.invoke({
                "input": user_input,
                "chat_history": langchain_history
            })
            
            # Extract final output
            output = response.get("output", "I apologize, but I couldn't process that request.")
            
            # Update chat history
            self.chat_history.append((user_input, output))
            
            return output
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            return error_msg
    
    def reset(self):
        """Clear conversation history"""
        self.chat_history = []
        if self.verbose:
            print("✓ Chat history cleared")
    
    def get_history(self) -> List[tuple]:
        """Get current chat history"""
        return self.chat_history.copy()


def run_simple_query(query: str, verbose: bool = True) -> str:
    """
    Run a single query without maintaining conversation state
    
    Args:
        query (str): User query
        verbose (bool): Enable verbose output
    
    Returns:
        str: Agent response
    """
    agent = create_calendar_agent(verbose=verbose)
    result = agent.invoke({"input": query})
    return result.get("output", "No response generated")


if __name__ == "__main__":
    # Quick test
    print("="*70)
    print(" CALENDAR ASSISTANT AGENT TEST")
    print("="*70)
    print()
    
    # Create chat interface
    chat = CalendarAssistantChat(verbose=True)
    
    # Test query
    query = "What events do I have coming up?"
    print(f"USER: {query}\n")
    
    response = chat.chat(query)
    
    print(f"\nASSISTANT: {response}\n")
    
    print("="*70)
    print("✅ Agent test completed!")
    print("="*70)