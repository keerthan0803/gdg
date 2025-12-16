"""
Test script to sync Gmail and create leads.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def check_gmail_status():
    """Check if Gmail is authenticated."""
    response = requests.get(f"{BASE_URL}/api/gmail/status")
    print("Gmail Status:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def authorize_gmail():
    """Get authorization URL."""
    response = requests.get(f"{BASE_URL}/api/gmail/authorize")
    data = response.json()
    print("\nAuthorization URL:")
    print(data.get("authorization_url"))
    print("\nVisit this URL in your browser to authorize Gmail access.")

def sync_gmail():
    """Sync Gmail and create leads."""
    response = requests.get(f"{BASE_URL}/api/gmail/sync")
    print("\nGmail Sync Results:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("=== Gmail Lead Sync Test ===\n")
    
    # Step 1: Check status
    status = check_gmail_status()
    
    # Step 2: If not authenticated, get auth URL
    if not status.get("authenticated"):
        print("\n❌ Gmail not authenticated")
        authorize_gmail()
        print("\nAfter authorizing, run this script again to sync emails.")
    else:
        print("\n✅ Gmail authenticated")
        
        # Step 3: Sync emails
        print("\nSyncing emails...")
        sync_gmail()
