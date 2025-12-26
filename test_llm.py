"""
Test script for Ollama Cloud LLM connection
Run this to verify your API key and model work
"""
# this test is the first one you should try directly after setting up your llm.py file

from agent.llm import test_llm_connection, get_ollama_llm


def main():
    print(" OLLAMA CLOUD LLM CONNECTION TEST")
    print()
    
    # Test 1: Basic connection
    try:
        test_llm_connection()
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print("\n📝 Troubleshooting:")
        print("1. Check that OLLAMA_API_KEY is set in .env file")
        print("2. Verify your API key is valid at https://ollama.com/settings/keys")
        print("3. Ensure model 'gpt-oss:20b' is available on your account")
        return False
    
    # Test 2: Calendar-specific query
    print("🗓️  TESTING CALENDAR-RELATED QUERY")
    
    try:
        llm = get_ollama_llm()
        
        query = "What information do you need to create a calendar event?"
        print(f"\n📤 Query: {query}")
        
        response = llm.invoke(query)
        
        print(f"\n📥 Response:\n{response.content}\n")
        
        print("✅ CALENDAR QUERY TEST PASSED!")
            
    except Exception as e:
        print(f"\n❌ Calendar query failed: {e}")
        return False
    
    print("\n🎉 SUCCESS! Your LLM is ready for the Calendar Assistant.")
    print("✓ API key is valid")
    print("✓ Model is responding correctly")
    print("✓ Ready to build the agent\n")
    
    return True


if __name__ == "__main__":
    main()