# Cal.com Integration Guide

Your system has been updated to use **Cal.com** instead of Calendly!

## How to Set Up Cal.com

### Step 1: Get Your Cal.com API Key

1. Go to [cal.com/settings/developer/api-keys](https://cal.com/settings/developer/api-keys)
2. Click "Create API Key"
3. Give it a name (e.g., "Lead Qualification System")
4. Copy the API key (starts with `cal_live_...`)

### Step 2: Find Your Username and Event Type

**Username:**
- Your Cal.com username is in your booking URL
- Example: `https://cal.com/john-doe/demo` → username is `john-doe`

**Event Type ID:**
- This is the event slug in your booking URL
- Example: `https://cal.com/john-doe/30min` → event type is `30min`
- Or create a custom event type for demos

### Step 3: Update Your .env File

Open `backend/.env` and update these values:

```env
# Cal.com Configuration
CAL_COM_API_KEY=cal_live_your_actual_api_key_here
CAL_COM_EVENT_TYPE_ID=demo
CAL_COM_USERNAME=your-username
```

**Example with real values:**
```env
CAL_COM_API_KEY=cal_live_1234567890abcdef
CAL_COM_EVENT_TYPE_ID=30min
CAL_COM_USERNAME=john-doe
```

### Step 4: Restart Your Backend

```powershell
# Stop the current backend (Ctrl+C)
# Then restart it
cd backend
.\venv\Scripts\Activate
uvicorn main:app --reload
```

## How It Works

### Automatic Scheduling Links

When a high-quality lead is detected, the AI agent will:

1. Generate a personalized Cal.com booking link
2. Pre-fill the lead's name and email
3. Send the link via email
4. Track when meetings are scheduled

### Example Link Generated

```
https://cal.com/your-username/demo?name=John%20Doe&email=john@acme.com
```

The lead will see:
- Your Cal.com booking page
- Their name and email already filled in
- Available time slots based on your calendar

## Cal.com API Features Used

### Current Implementation

✅ **Booking Link Generation** - Create personalized links with pre-filled data
✅ **Query Parameters** - Auto-fill attendee information

### Future Enhancements (Optional)

🔄 **Get Bookings API** - Fetch scheduled meetings
🔄 **Create Bookings** - Programmatically schedule meetings
🔄 **Webhook Integration** - Get notified when meetings are booked
🔄 **Rescheduling** - Handle meeting changes

## Testing Cal.com Integration

### Test 1: Generate a Booking Link

```powershell
# Create a test lead via API
$body = @{
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
    company_name = "Test Corp"
    source = "website"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/leads" -Method POST -Body $body -ContentType "application/json"
```

### Test 2: Trigger AI Agent

```powershell
# Process the lead (will generate Cal.com link if high score)
Invoke-RestMethod -Uri "http://localhost:8000/api/leads/1/process" -Method POST
```

### Test 3: Check the Generated Link

1. Go to your dashboard at http://localhost:3000
2. Click on the lead
3. Look for "Agent Actions" section
4. You'll see the Cal.com booking link

## Cal.com vs Calendly

| Feature | Cal.com | Calendly |
|---------|---------|----------|
| **Cost** | Free & Open Source | Paid plans |
| **Self-Hosting** | Yes | No |
| **API Access** | Free tier | Paid plans only |
| **Customization** | Full control | Limited |
| **Integration** | Works ✅ | Also works |

## Troubleshooting

**Link shows "your-username"?**
- Make sure you updated `CAL_COM_USERNAME` in `.env`
- Restart the backend server

**API errors?**
- Verify your API key is correct
- Check it starts with `cal_live_` (not `cal_test_`)
- Ensure API key has proper permissions

**Bookings not showing?**
- The free tier may have API limitations
- Check Cal.com API documentation
- Verify your event type ID is correct

## Cal.com Resources

- **Dashboard**: https://cal.com/dashboard
- **API Docs**: https://cal.com/docs/api-reference
- **Settings**: https://cal.com/settings
- **Event Types**: https://cal.com/event-types

---

**Your system is now configured for Cal.com! 🎉**

When leads are qualified, they'll automatically receive Cal.com booking links to schedule demos with your team.
