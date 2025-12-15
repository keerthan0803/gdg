# Quick Start Guide

Get the AI Lead Qualification Agent running in under 10 minutes.

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

## 1. Clone Repository

```bash
git clone <your-repo-url>
cd gdg
```

## 2. Backend Setup (5 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Mac/Linux

# Edit .env and add your credentials:
# Minimum required:
# - DATABASE_URL=postgresql://user:password@localhost:5432/lead_qualification
# - OPENAI_API_KEY=sk-your-key-here

# Initialize database
python -c "from database import init_db; init_db()"

# Start backend
python main.py
```

Backend now running at `http://localhost:8000`

Visit `http://localhost:8000/docs` to see API documentation.

## 3. Frontend Setup (3 minutes)

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend now running at `http://localhost:3000`

## 4. Test the System (2 minutes)

1. Open `http://localhost:3000` in your browser
2. Click "New Lead"
3. Fill in test lead:
   ```
   Email: john.doe@techcorp.com
   First Name: John
   Last Name: Doe
   Job Title: CTO
   Company: TechCorp
   Source: Manual
   Notes: Looking for enterprise solution
   ```
4. Click "Create Lead"
5. Watch the autonomous agent process the lead!

You should see:
- Lead enrichment happening
- AI scoring in progress
- Agent actions being logged
- Final qualification status

## 5. Next Steps

### Customize ICP Criteria

Edit `backend/config.py`:

```python
ICP_TARGET_INDUSTRIES = [
    "Your",
    "Target",
    "Industries"
]

ICP_TARGET_ROLES = [
    "CEO",
    "CTO",
    "VP"
]
```

### Add Integrations

**Email (SendGrid)**:
1. Sign up at sendgrid.com
2. Get API key
3. Add to `.env`:
   ```
   SENDGRID_API_KEY=your-key
   SENDGRID_FROM_EMAIL=noreply@yourdomain.com
   ```

**CRM (HubSpot)**:
1. Get HubSpot API key
2. Add to `.env`:
   ```
   HUBSPOT_API_KEY=your-key
   HUBSPOT_PORTAL_ID=your-id
   ```

**Calendar (Calendly)**:
1. Get Calendly API key
2. Add to `.env`:
   ```
   CALENDLY_API_KEY=your-key
   CALENDLY_EVENT_TYPE_UUID=your-uuid
   ```

## Common Issues

### Database Connection Error
```bash
# Make sure PostgreSQL is running
# Windows:
net start postgresql

# Mac:
brew services start postgresql

# Create database if needed:
createdb lead_qualification
```

### Port Already in Use
```bash
# Backend (port 8000):
# Kill process or change PORT in .env

# Frontend (port 3000):
# Change port in vite.config.ts
```

### OpenAI API Error
- Check API key is correct
- Verify you have credits
- Check rate limits

## Development Workflow

### Add a New Lead via API

```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "source": "api"
  }'
```

### View Logs

Backend logs show:
- Lead processing steps
- AI decisions
- Agent actions
- Errors

Watch them in your terminal running `python main.py`

### Check Database

```bash
# Connect to PostgreSQL
psql lead_qualification

# View leads
SELECT id, email, lead_score, status FROM leads;

# View agent actions
SELECT lead_id, action_type, status FROM agent_actions;
```

## Architecture Overview

```
User Input
    ↓
Frontend (React)
    ↓
API (FastAPI)
    ↓
Enrichment → Scoring → Agent → Actions
    ↓           ↓        ↓       ↓
Database ← PostgreSQL ← Audit Trail
```

## What Happens When You Create a Lead?

1. **Ingest**: Lead data validated and stored
2. **Enrich**: Company data fetched from external sources
3. **Score**: AI analyzes and scores the lead
   - ICP Fit: How well do they match your ideal customer?
   - Intent: How likely are they to buy?
   - Engagement: How engaged are they?
4. **Decide**: Agent determines next best action
5. **Act**: Agent executes actions automatically
   - High score → Schedule demo, notify sales
   - Medium score → Ask qualifying questions
   - Low score → Add to nurture campaign

## Tips for Success

1. **Start with test data**: Don't use real leads initially
2. **Monitor the dashboard**: Watch how leads are scored
3. **Adjust thresholds**: Tune scoring in `config.py`
4. **Check agent actions**: Review what the agent is doing
5. **Iterate on ICP**: Refine your target customer profile

## Getting Help

- 📖 Read the full [README.md](README.md)
- 🔧 Check [Backend Documentation](backend/README.md)
- 🎨 See [Frontend Documentation](frontend/README.md)
- 🚀 Review [Deployment Guide](DEPLOYMENT.md)

## Production Deployment

When ready to deploy:

1. Push code to GitHub
2. Follow [DEPLOYMENT.md](DEPLOYMENT.md)
3. Deploy to Render (free tier available)
4. Add production API keys
5. Test with real leads

## Success Metrics

Track these KPIs:
- Lead processing time
- Scoring accuracy
- Qualification rate
- Sales team feedback
- Conversion rates

## Ready to Scale?

Once validated, consider:
- Adding more data sources
- Enhancing AI prompts
- Implementing advanced workflows
- Building custom integrations
- Adding team collaboration features

---

**You're all set!** 🚀 Start qualifying leads autonomously.
