#!/usr/bin/env python3
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add the shared directory to path
sys.path.insert(0, os.path.abspath('.'))

from notifiers.email_notifier import EmailNotifier

async def test_email():
    """Test sending an email using the Communicator Agent"""
    print("=" * 60)
    print("Testing Communicator Agent Email Notifier")
    print("=" * 60)
    
    # Check environment variables
    zepto_token = os.getenv('ZEPTO_TOKEN', '')
    zepto_from = os.getenv('ZEPTO_FROM_EMAIL', '')
    
    print(f"\nZEPTO_TOKEN: {'✅ Set' if zepto_token else '❌ Not Set'}")
    print(f"ZEPTO_FROM_EMAIL: {zepto_from}")
    print(f"Mock Mode: {os.getenv('MOCK_EMAIL', 'false')}")
    
    # Initialize email notifier
    notifier = EmailNotifier()
    
    # Send test email
    print("\n📧 Sending test email to todak2000@gmail.com...")
    
    result = await notifier.send(
        recipient="todak2000@gmail.com",
        subject="✅ Test Email from Communicator Agent",
        body="""Hello!

This is a test email from the Communicator Agent to verify that email notifications are working correctly.

If you receive this email, it means:
✅ ZEPTO_TOKEN is configured correctly
✅ Email Notifier is working
✅ Communicator Agent is operational

This email was sent as part of testing the AI Agent workflow for the Cloud Run Hackathon project.

Best regards,
Communicator Agent
""",
        metadata={"test": True, "agent": "communicator"}
    )
    
    if result:
        print("\n✅ Email sent successfully!")
        print("📬 Check todak2000@gmail.com inbox")
    else:
        print("\n❌ Email failed to send")
        print("Check the logs above for error details")
    
    print("=" * 60)
    return result

if __name__ == "__main__":
    success = asyncio.run(test_email())
    sys.exit(0 if success else 1)
