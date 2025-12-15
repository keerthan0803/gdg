# Automatic Lead Capture Setup Guide

Your AI Lead Qualification system now has **3 webhook endpoints** that automatically capture leads from different sources:

## 🔗 Available Webhooks

### 1️⃣ CRM Webhook (HubSpot, Salesforce, etc.)
**URL:** `https://your-domain.com/api/webhooks/crm`

### 2️⃣ Email Webhook (SendGrid, Mailgun, etc.)
**URL:** `https://your-domain.com/api/webhooks/email`

### 3️⃣ Website Form Webhook
**URL:** `https://your-domain.com/api/webhooks/form`

---

## 📧 Setup 1: Email Auto-Capture (SendGrid)

### What It Does:
- Automatically creates leads when someone emails you
- Example: leads@yourdomain.com → Auto-creates lead
- AI processes and qualifies immediately

### Setup Steps:

1. **Login to SendGrid**
   - Go to https://app.sendgrid.com

2. **Configure Inbound Parse**
   - Navigate to: **Settings** → **Inbound Parse**
   - Click **Add Host & URL**

3. **Configure Domain**
   - **Subdomain**: `leads` (or any name you want)
   - **Domain**: Your domain (e.g., `yourdomain.com`)
   - **Result**: `leads@yourdomain.com`

4. **Set Webhook URL**
   ```
   https://your-backend-url.com/api/webhooks/email
   ```
   For local testing:
   ```
   http://localhost:8000/api/webhooks/email
   ```

5. **Test It**
   Send an email to: `leads@yourdomain.com`
   
   The system will:
   - ✅ Extract email sender
   - ✅ Create lead automatically
   - ✅ Enrich with company data
   - ✅ Score the lead
   - ✅ AI agent takes action

---

## 🔄 Setup 2: CRM Webhook (HubSpot)

### What It Does:
- Captures leads from HubSpot forms
- Syncs new HubSpot contacts automatically
- Two-way sync capability

### Setup Steps:

1. **Login to HubSpot**
   - Go to https://app.hubspot.com

2. **Navigate to Webhooks**
   - **Settings** (⚙️) → **Integrations** → **Webhooks**
   - Click **Create webhook**

3. **Configure Webhook**
   - **Webhook URL**:
     ```
     https://your-backend-url.com/api/webhooks/crm
     ```
   
   - **Subscribe to events**:
     - ✅ `contact.creation`
     - ✅ `contact.propertyChange`
     - ✅ `deal.creation`

4. **Authentication** (optional)
   - Add custom headers if needed
   - Or use HubSpot's authentication

5. **Test It**
   - Create a test contact in HubSpot
   - Check your backend logs
   - Lead should appear in dashboard

### HubSpot API Token Setup:

1. **Create Private App**
   - Go to: **Settings** → **Integrations** → **Private Apps**
   - Click **Create a private app**
   - Name: "Lead Qualification System"

2. **Configure Scopes**
   Select these scopes:
   - ✅ `crm.objects.contacts.read`
   - ✅ `crm.objects.contacts.write`
   - ✅ `crm.objects.companies.read`
   - ✅ `crm.objects.companies.write`
   - ✅ `crm.objects.deals.read`
   - ✅ `crm.objects.deals.write`

3. **Copy Access Token**
   - Copy the token (starts with `pat-na...`)
   - Add to your `.env` file:
     ```env
     HUBSPOT_API_KEY=pat-na2-your-token-here
     ```

---

## 🌐 Setup 3: Website Form Integration

### What It Does:
- Captures leads from your website contact forms
- Works with any HTML form
- Real-time lead qualification

### Option A: Direct Form Submission

Add this JavaScript to your website:

```html
<form id="leadForm">
  <input type="email" name="email" placeholder="Email" required>
  <input type="text" name="first_name" placeholder="First Name">
  <input type="text" name="last_name" placeholder="Last Name">
  <input type="text" name="company_name" placeholder="Company">
  <input type="tel" name="phone" placeholder="Phone">
  <textarea name="message" placeholder="Message"></textarea>
  <button type="submit">Submit</button>
</form>

<script>
document.getElementById('leadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch('https://your-backend-url.com/api/webhooks/form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            alert('Thank you! We\\'ll be in touch soon.');
            console.log('Lead Score:', result.lead_score);
            console.log('Next Action:', result.recommended_action);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Something went wrong. Please try again.');
    }
});
</script>
```

### Option B: Use with Form Builders

**Typeform:**
1. Go to **Connect** → **Webhooks**
2. Add: `https://your-backend-url.com/api/webhooks/form`

**Webflow:**
1. Form Settings → **Custom Webhook**
2. Add: `https://your-backend-url.com/api/webhooks/form`

**WordPress (Contact Form 7):**
1. Install "Webhooks" plugin
2. Configure webhook URL

---

## 🧪 Testing Webhooks Locally

### Use ngrok to expose localhost:

```bash
# Install ngrok
choco install ngrok

# Expose port 8000
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`) and use it in webhook configurations:
```
https://abc123.ngrok.io/api/webhooks/crm
https://abc123.ngrok.io/api/webhooks/email
https://abc123.ngrok.io/api/webhooks/form
```

### Test with cURL:

```bash
# Test CRM Webhook
curl -X POST http://localhost:8000/api/webhooks/crm \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@acme.com",
    "first_name": "John",
    "last_name": "Doe",
    "company": "Acme Corp"
  }'

# Test Email Webhook
curl -X POST http://localhost:8000/api/webhooks/email \
  -H "Content-Type: application/json" \
  -d '{
    "from": "Jane Smith <jane@company.com>",
    "subject": "Demo Request",
    "text": "I would like to schedule a demo"
  }'

# Test Form Webhook
curl -X POST http://localhost:8000/api/webhooks/form \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mike@startup.io",
    "first_name": "Mike",
    "company_name": "Startup Inc",
    "message": "Interested in your product"
  }'
```

---

## 🤖 What Happens Automatically

When a lead comes in via webhook:

1. **Lead Creation** - Stored in database
2. **Enrichment** - Company data fetched
3. **Scoring** - AI evaluates ICP fit, intent, engagement
4. **Agent Decision** - AI decides next action
5. **Auto-Action** - Based on score:
   - **High (80+)**: Schedule demo, notify sales, sync to CRM
   - **Medium (50-79)**: Send qualifying questions
   - **Low (0-49)**: Add to nurture campaign

---

## 📊 Monitor Webhook Activity

### View in Dashboard:
- Go to: http://localhost:3000/leads
- Filter by source: `CRM Webhook`, `Email`, `Website Form`

### Check Logs:
```bash
# Backend logs show webhook activity
tail -f backend.log
```

### API Endpoint:
```bash
# Get all webhook-sourced leads
curl http://localhost:8000/api/leads?source=crm_webhook
curl http://localhost:8000/api/leads?source=email
curl http://localhost:8000/api/leads?source=website_form
```

---

## 🔐 Security Best Practices

1. **Use HTTPS** in production (never HTTP)
2. **Validate webhook signatures** from CRMs
3. **Rate limiting** - Add to prevent abuse
4. **API authentication** - Add API keys for production
5. **IP whitelisting** - Restrict to known IPs

Example: Add API key validation:
```python
from fastapi import Header

@app.post("/api/webhooks/crm")
async def crm_webhook(
    request: dict,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    if x_api_key != settings.WEBHOOK_API_KEY:
        raise HTTPException(401, "Invalid API key")
    # ... rest of code
```

---

## 🚀 Production Deployment

When deploying to Render, your webhook URLs will be:
```
https://your-app-name.onrender.com/api/webhooks/crm
https://your-app-name.onrender.com/api/webhooks/email
https://your-app-name.onrender.com/api/webhooks/form
```

Update all webhook configurations to use your production URL!

---

## 📞 Support

**Test your webhooks:** http://localhost:8000/docs

Look for these endpoints:
- POST `/api/webhooks/crm`
- POST `/api/webhooks/email`
- POST `/api/webhooks/form`

Each has interactive documentation showing required fields and response formats.

**Your system is ready for automatic lead capture! 🎉**
