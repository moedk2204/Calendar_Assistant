"""
Complete agent test with real calendar operations
"""

# testing the full agent is the final step to ensure everything is working together as expected :)

from agent.agent import CalendarAssistantChat


def main():
    print(" CALENDAR ASSISTANT - FULL AGENT TEST")
    print()
    
    # Create chat instance
    chat = CalendarAssistantChat(verbose=True)
    
    # Test queries
    queries = [
        "What events do I have coming up?",
        "What's on my calendar for December 6th, 2025?",
        "Is December 10th at 3pm available?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"TEST {i}: {query}")
        
        response = chat.chat(query)
        
        print(f"\n✓ Response:\n{response}\n")
        
        if i < len(queries):
            input("Press Enter for next test...")
    
    print("✅ ALL AGENT TESTS COMPLETED!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")