# Gmail API Integration Setup

## Overview
The system now includes Gmail API integration to automatically read and process sales inquiry emails into leads.

## Setup Instructions

### 1. Enable Gmail API in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure consent screen if prompted:
   - User Type: External (for testing) or Internal (for organization)
   - Add required information
   - Add scope: `https://www.googleapis.com/auth/gmail.readonly`
4. Application type: **Desktop app**
5. Download the credentials JSON file
6. Rename it to `credentials.json`
7. Place it in the `backend/` directory

### 3. Configure Environment Variables

Add to your `.env` file:

```env
# Gmail API Settings
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_SEARCH_QUERY=is:unread subject:(inquiry OR quote OR sales OR demo OR contact)
```

### 4. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. First-Time Authentication

Run the authentication flow:

```bash
python -c "from services.gmail import gmail_service; gmail_service.authenticate()"
```

This will:
1. Open a browser window
2. Ask you to sign in to your Google account
3. Request permission to read emails
4. Save authentication token to `token.json`

### 6. Customize Email Search Query

Modify `GMAIL_SEARCH_QUERY` in `.env` to match your needs:

```env
# Search for unread emails with specific keywords in subject
GMAIL_SEARCH_QUERY=is:unread subject:(inquiry OR quote OR sales OR demo OR contact)

# Search for emails from specific domain
GMAIL_SEARCH_QUERY=is:unread from:@company.com

# Search for emails in specific label/folder
GMAIL_SEARCH_QUERY=is:unread label:sales-leads

# Combine multiple criteria
GMAIL_SEARCH_QUERY=is:unread (subject:inquiry OR subject:quote) from:@company.com
```

## Usage

### Manual Sync via API

Sync emails and create leads:

```bash
POST http://localhost:8000/api/gmail/sync?max_emails=10
```

Response:
```json
{
  "status": "success",
  "message": "Processed 5 emails",
  "emails_processed": 5,
  "leads_created": 3,
  "leads": [
    {
      "lead_id": 10,
      "email": "john@example.com",
      "name": "John Doe",
      "score": 75
    }
  ]
}
```

### Check Authentication Status

```bash
GET http://localhost:8000/api/gmail/status
```

Response:
```json
{
  "authenticated": true,
  "credentials_file_exists": true,
  "token_file_exists": true,
  "search_query": "is:unread subject:(inquiry OR quote OR sales OR demo OR contact)"
}
```

### From Frontend

Add a "Sync Emails" button to your dashboard:

```typescript
const syncEmails = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/gmail/sync?max_emails=10', {
      method: 'POST'
    });
    const data = await response.json();
    console.log('Synced:', data);
    // Refresh leads list
  } catch (error) {
    console.error('Sync failed:', error);
  }
};
```

## Automated Sync (Optional)

### Option 1: Scheduled Task (Windows)

Create a task to run every 15 minutes:

```powershell
# Create a PowerShell script: sync_gmail.ps1
Invoke-RestMethod -Uri "http://localhost:8000/api/gmail/sync" -Method POST
```

Schedule it in Task Scheduler to run periodically.

### Option 2: Celery Background Task

Add to `backend/tasks.py`:

```python
from celery import Celery
from services.gmail import gmail_service

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def sync_gmail_emails():
    """Background task to sync emails."""
    # Your sync logic here
    pass

# Schedule to run every 15 minutes
celery.conf.beat_schedule = {
    'sync-gmail-every-15-minutes': {
        'task': 'tasks.sync_gmail_emails',
        'schedule': 900.0,  # 15 minutes
    },
}
```

## What Information is Extracted

From each email, the system extracts:

- **Email address** (sender)
- **Name** (from sender info)
- **Company** (from email domain or email signature)
- **Phone** (if found in email body)
- **Subject line** (stored in notes)
- **Email body** (first 500 characters stored in notes)
- **Thread ID** (for reference)

## Security Notes

- `credentials.json` contains your OAuth client credentials - keep it secure
- `token.json` contains your access token - keep it secure  
- Add both files to `.gitignore` to prevent committing them
- The system only requests **read-only** access to Gmail
- Processed emails are marked as read automatically

## Troubleshooting

### Authentication fails
- Ensure `credentials.json` is in the `backend/` directory
- Check that Gmail API is enabled in Google Cloud Console
- Delete `token.json` and re-authenticate

### No emails found
- Check your `GMAIL_SEARCH_QUERY` matches your emails
- Verify you have unread emails matching the criteria
- Test with a simpler query: `is:unread`

### Permission denied
- Make sure the OAuth consent screen is configured
- Add your email as a test user (for External apps)
- Check that gmail.readonly scope is included

## Next Steps

After setup, the system will:
1. ✅ Read sales inquiry emails from Gmail
2. ✅ Extract lead information automatically
3. ✅ Create leads in the database
4. ✅ Trigger AI agent processing (enrichment, scoring, actions)
5. ✅ Mark processed emails as read

You can now focus on responding to qualified leads!
