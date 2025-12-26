"""
Ollama Cloud LLM Configuration
Configures ChatOllama with gpt-oss:120b for Calendar Assistant
"""

import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama

# Load environment variables
load_dotenv()


def get_ollama_llm(
    model: str = "gpt-oss:120b",
    base_url: str = "https://ollama.com",
    temperature: float = 0.1,
    **kwargs
):
    """
    Initialize and return ChatOllama instance configured for Ollama Cloud
    
    Args:
        model (str): Model name (default: "gpt-oss:20b")
        base_url (str): Ollama Cloud API endpoint
        temperature (float): Sampling temperature (0.0 to 1.0)
        **kwargs: Additional ChatOllama parameters
    
    Returns:
        ChatOllama: Configured LLM instance
    
    Environment Variables:
        OLLAMA_API_KEY: Required API key for Ollama Cloud
        OLLAMA_MODEL: Optional override for model name
        OLLAMA_BASE_URL: Optional override for base URL
    
    Raises:
        ValueError: If OLLAMA_API_KEY not found in environment
    """
    # Get API key from environment
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        raise ValueError(
            "OLLAMA_API_KEY not found in environment variables.\n"
            "Please set it in your .env file:\n"
            "OLLAMA_API_KEY=your_api_key_here"
        )
    
    # Allow environment variable overrides
    model = os.getenv("OLLAMA_MODEL", model)
    base_url = os.getenv("OLLAMA_BASE_URL", base_url)
    
    # Create headers for Ollama Cloud authentication
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Initialize ChatOllama
    llm = ChatOllama(
        model=model,
        base_url=base_url,
        temperature=temperature,
        headers=headers,
        **kwargs
    )
    
    print(f"✓ Ollama LLM initialized: {model} @ {base_url}")
    
    return llm


def test_llm_connection():
    """
    Test the Ollama Cloud connection with a simple query
    
    Returns:
        bool: True if successful, raises exception otherwise
    """
    try:
        print("\n" + "="*70)
        print("🤖 TESTING OLLAMA CLOUD CONNECTION")
        print("="*70)
        
        llm = get_ollama_llm()
        
        # Test with simple query
        response = llm.invoke("Say 'Hello from Calendar Assistant!' if you can hear me.")
        
        print(f"\n✓ LLM Connection Test Passed")
        print(f"✓ Model Response: {response.content[:100]}...")
        print("\n" + "="*70)
        print("✅ OLLAMA CLOUD CONNECTED SUCCESSFULLY!")
        print("="*70 + "\n")
        
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ LLM Connection Test Failed: {e}\n")
        raise


if __name__ == "__main__":
    # Quick test when run directly
    print("🚀 Ollama Cloud LLM Test\n")
    
    try:
        test_llm_connection()
    except Exception as e:
        print(f"❌ Test failed: {e}")