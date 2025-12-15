# AI-Powered Autonomous Lead Qualification Agent

A production-ready MVP system that autonomously qualifies, enriches, scores, and takes action on inbound sales leads using AI and external data sources.

## 🎯 Overview

This system reduces manual sales effort by automatically:
- **Ingesting** leads from multiple sources (website forms, CRM, email, chat)
- **Enriching** leads with company data and technographic signals
- **Scoring** leads using AI-powered analysis (ICP fit, intent, engagement)
- **Taking Action** autonomously (scheduling demos, asking questions, syncing to CRM)
- **Tracking** all actions in an audit trail

## 🏗️ Architecture

```
┌─────────────────┐
│   Lead Sources  │
│ (Forms/CRM/API) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Backend│
│  - Ingest       │
│  - Normalize    │
│  - Store        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Enrichment Svc  │
│ - Domain Extract│
│ - Company Data  │
│ - Technographics│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Scoring     │
│ - ICP Fit       │
│ - Intent        │
│ - Engagement    │
│ - GPT-4 Analysis│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Autonomous Agent│
│ - Decision Logic│
│ - Actions       │
│ - Follow-ups    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐┌────────┐┌────────┐┌────────┐
│Schedule││  CRM   ││ Email  ││Nurture │
│  Demo  ││  Sync  ││ Q&A    ││Campaign│
└────────┘└────────┘└────────┘└────────┘
```

## 📊 Lead Scoring Logic

### Overall Lead Score (0-100)
Weighted combination of three factors:

1. **ICP Fit Score (35% weight)**
   - Company size within target range: 30 pts
   - Target industry match: 30 pts
   - Decision-maker role: 25 pts
   - Business email domain: 15 pts

2. **Intent Score (40% weight)**
   - AI-powered analysis using GPT-4
   - Analyzes context, urgency, pain points
   - Identifies buying signals and concerns

3. **Engagement Score (25% weight)**
   - Complete information provided: 40 pts
   - Phone number provided: 20 pts
   - Quality source: up to 20 pts
   - Additional context/notes: 20 pts

### Decision Thresholds

- **≥75**: Qualified Lead → Schedule demo, sync CRM, notify sales
- **50-74**: Nurture Lead → Ask qualifying questions, add to nurture
- **<50**: Disqualified → Add to long-term nurture, no immediate action

## 🤖 Autonomous Agent Behavior

The AI agent makes decisions based on lead scores:

### High-Quality Lead (Score ≥ 75)
1. ✅ Sync to CRM with full enrichment data
2. 📅 Create personalized scheduling link
3. 📧 Send demo invitation email
4. 🔔 Notify sales team with lead details
5. 📊 Mark as "Qualified"

### Medium-Quality Lead (Score 50-74)
1. ❓ Generate personalized qualifying questions
2. 📧 Send questions via email
3. ⏳ Wait for responses
4. 🔄 Re-evaluate after response
5. 📊 Mark as "Nurture"

### Low-Quality Lead (Score < 50)
1. 📋 Add to nurture workflow
2. 🚫 No immediate follow-up
3. 📊 Mark as "Disqualified"

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- OpenAI API key

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env with your credentials
# Required: DATABASE_URL, OPENAI_API_KEY
# Optional: SENDGRID_API_KEY, TWILIO credentials, etc.

# Initialize database
python -c "from database import init_db; init_db()"

# Run the server
python main.py
```

Backend will start on `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file (optional)
echo VITE_API_URL=http://localhost:8000 > .env

# Run development server
npm run dev
```

Frontend will start on `http://localhost:3000`

## 📝 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lead_qualification

# OpenAI (Required)
OPENAI_API_KEY=sk-your-key-here

# Email Service (Optional)
SENDGRID_API_KEY=your-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Messaging (Optional)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_SMS_NUMBER=+1234567890

# Calendar (Optional)
CALENDLY_API_KEY=your-key
CALENDLY_EVENT_TYPE_UUID=your-uuid

# CRM (Optional)
HUBSPOT_API_KEY=your-key
HUBSPOT_PORTAL_ID=your-id
```

### ICP Configuration

Edit `backend/config.py` to customize your Ideal Customer Profile:

```python
ICP_MIN_COMPANY_SIZE = 10
ICP_MAX_COMPANY_SIZE = 5000
ICP_TARGET_INDUSTRIES = [
    "Technology",
    "SaaS",
    "Software",
    "IT Services",
    "Financial Services",
]
ICP_TARGET_ROLES = [
    "CEO",
    "CTO",
    "VP",
    "Director",
    "Head of",
]
```

## 🧪 Testing

### Test Lead Creation via API

```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@techcorp.com",
    "first_name": "John",
    "last_name": "Doe",
    "job_title": "CTO",
    "company_name": "TechCorp",
    "source": "website_form",
    "notes": "Interested in enterprise plan"
  }'
```

### Test via Dashboard

1. Open `http://localhost:3000`
2. Click "New Lead"
3. Fill in lead information
4. Submit and watch autonomous processing

## 📚 API Documentation

### Core Endpoints

#### Create Lead
```
POST /api/leads
```
Creates and automatically processes a new lead.

#### Get Leads
```
GET /api/leads?page=1&page_size=20&status=qualified&min_score=75
```
List leads with filtering and pagination.

#### Get Lead Details
```
GET /api/leads/{id}
```
Get complete lead information.

#### Process Lead
```
POST /api/leads/{id}/process
```
Manually trigger autonomous agent processing.

#### Get Agent Actions
```
GET /api/leads/{id}/actions
```
View all actions taken by the agent for a lead.

#### Dashboard Stats
```
GET /api/dashboard/stats
```
Get dashboard statistics and metrics.

See full API documentation at `http://localhost:8000/docs` (Swagger UI)

## 🔧 Customization

### Adding Custom Scoring Logic

Edit `backend/services/scoring.py`:

```python
def calculate_custom_score(self, lead_data: Dict[str, Any]) -> float:
    score = 0.0
    # Add your custom scoring logic
    return score
```

### Adding Custom Agent Actions

Edit `backend/services/agent.py`:

```python
async def _custom_action(self, lead: Lead, db: Session) -> Dict[str, Any]:
    # Implement your custom action
    pass
```

### Customizing Email Templates

Edit templates in `backend/services/communication.py`:

```python
async def send_custom_email(self, to_email: str, context: dict):
    # Customize email content
    pass
```

## 🐛 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify credentials and database exists

### OpenAI API Error
- Verify `OPENAI_API_KEY` is correct
- Check API usage limits
- Ensure model name is valid (default: `gpt-4-turbo-preview`)

### Frontend Can't Connect to Backend
- Ensure backend is running on port 8000
- Check CORS settings in `backend/config.py`
- Verify proxy settings in `frontend/vite.config.ts`

## 📈 Performance Optimization

### Database Indexing
The system includes indexes on:
- `leads.email` (unique)
- `leads.status`
- `leads.lead_score`
- `leads.company_domain`
- `agent_actions.lead_id`

### Caching Recommendations
- Cache enrichment data (TTL: 7 days)
- Cache scoring results (TTL: 24 hours)
- Use Redis for session storage

### Scaling Considerations
- Use Celery for background task processing
- Implement rate limiting for API endpoints
- Use connection pooling for database
- Consider horizontal scaling with load balancer

## 🔒 Security

### Best Practices Implemented
- ✅ Environment variables for secrets
- ✅ SQL injection protection (SQLAlchemy)
- ✅ CORS configuration
- ✅ Input validation (Pydantic)
- ✅ API rate limiting ready

### Additional Recommendations
- Add authentication/authorization
- Implement API key management
- Use HTTPS in production
- Regular security audits
- Encrypt sensitive data at rest

## 📊 Monitoring & Logging

All system events are logged to:
- Console (development)
- `system_logs` table (database)

Monitor:
- Lead processing success rate
- Agent action completion rate
- API response times
- OpenAI API usage
- Database query performance

## 🤝 Support

For questions or issues:
1. Check documentation
2. Review API logs
3. Check database logs
4. Test with minimal configuration

## 📄 License

MIT License - See LICENSE file for details

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/)
- [React Query Guide](https://tanstack.com/query/latest)
- [PostgreSQL Manual](https://www.postgresql.org/docs/)
