"""
Quick test script for Google Calendar authentication
Run this to verify your OAuth setup works
"""
# In this case you need to have your credentials.json file in the project root
# So you can verify that the OAuth flow completes and token.json is created for the rest of your project 
from auth.google_auth import test_calendar_connection, revoke_token
import sys


def main():
    
    print(" GOOGLE CALENDAR AUTHENTICATION TEST")
    
    print()
    
    # Check if user wants to revoke token
    if len(sys.argv) > 1 and sys.argv[1] == '--revoke':
        print("🗑️  Revoking existing token...\n")
        revoke_token()
        print()
    
    # Test connection
    try:
        success = test_calendar_connection()
        
        if success:
            print("\n🎉 SUCCESS! Your Google Calendar is connected.")
            print("✓ token.json has been generated")
            print("✓ You can now build calendar tools")
        else:
            print("\n⚠️  Connection test completed with warnings")
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print("\n📝 Troubleshooting:")
        print("1. Ensure credentials.json is in the project root")
        print("2. Check that Google Calendar API is enabled in Cloud Console")
        print("3. Verify OAuth consent screen is configured")
        print("4. Make sure redirect URIs include http://localhost")
        return False
    
    return True


if __name__ == "__main__":
    main()