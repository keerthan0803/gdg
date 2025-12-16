"""Test SendGrid API key validity."""
import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings

def test_sendgrid():
    print("Testing SendGrid configuration...")
    print(f"API Key: {settings.SENDGRID_API_KEY[:20]}..." if settings.SENDGRID_API_KEY else "Not set")
    print(f"From Email: {settings.SENDGRID_FROM_EMAIL}")
    
    if not settings.SENDGRID_API_KEY:
        print("\n❌ SendGrid API key not configured")
        return
    
    try:
        # Initialize client
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        
        # Try to send a test email to yourself
        message = Mail(
            from_email=settings.SENDGRID_FROM_EMAIL,
            to_emails=settings.SENDGRID_FROM_EMAIL,  # Send to yourself
            subject='SendGrid Test - AI Lead Agent',
            plain_text_content='This is a test email from your AI Lead Qualification Agent.',
            html_content='<strong>This is a test email from your AI Lead Qualification Agent.</strong>'
        )
        
        response = sg.send(message)
        
        print(f"\n✅ SendGrid test successful!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        
    except Exception as e:
        print(f"\n❌ SendGrid test failed!")
        print(f"Error: {e}")
        print("\nPossible issues:")
        print("1. API key is invalid or expired - regenerate at https://app.sendgrid.com/settings/api_keys")
        print("2. Sender email not verified - verify at https://app.sendgrid.com/settings/sender_auth")
        print("3. API key doesn't have 'Mail Send' permission")

if __name__ == "__main__":
    test_sendgrid()
