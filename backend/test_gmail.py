"""Test Gmail service initialization."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing Gmail service import...")
    from services.gmail import gmail_service
    print("✓ Gmail service imported successfully")
    
    print("\nTesting authorization URL generation...")
    auth_url = gmail_service.get_authorization_url()
    
    if auth_url:
        print(f"✓ Authorization URL generated successfully:")
        print(f"\n{auth_url}\n")
        print("You can visit this URL to authorize Gmail access")
    else:
        print("✗ Failed to generate authorization URL")
        print("Check if credentials.json exists and is valid")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
