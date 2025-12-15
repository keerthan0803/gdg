# Backend Documentation

## Overview

The backend is built with FastAPI and provides a REST API for lead qualification, enrichment, scoring, and autonomous agent actions.

## Project Structure

```
backend/
├── config.py              # Application configuration
├── database.py            # Database setup and session management
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic schemas for validation
├── main.py                # FastAPI application and routes
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
└── services/             # Business logic services
    ├── __init__.py
    ├── enrichment.py     # Lead enrichment service
    ├── scoring.py        # AI scoring service
    ├── agent.py          # Autonomous agent
    ├── communication.py  # Email/SMS/WhatsApp
    ├── crm.py           # HubSpot CRM integration
    └── calendar.py      # Calendly integration
```

## Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

Required variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for GPT-4

Optional variables:
- Email service (SendGrid)
- Messaging (Twilio)
- Calendar (Calendly)
- CRM (HubSpot)

### 4. Initialize Database

```bash
python -c "from database import init_db; init_db()"
```

### 5. Run Server

```bash
# Development
python main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Lead Management

#### POST /api/leads
Create a new lead and trigger autonomous processing.

**Request:**
```json
{
  "email": "john@company.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "job_title": "CTO",
  "company_name": "TechCorp",
  "source": "website_form",
  "notes": "Interested in enterprise plan"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "john@company.com",
  "lead_score": 82.5,
  "status": "qualified",
  "recommended_action": "schedule_demo",
  ...
}
```

#### GET /api/leads
List leads with filtering and pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50, max: 100)
- `status`: Filter by status
- `min_score`: Minimum lead score
- `source`: Filter by source

#### GET /api/leads/{id}
Get detailed information about a specific lead.

#### PATCH /api/leads/{id}
Update lead information.

#### DELETE /api/leads/{id}
Delete a lead.

### Lead Processing

#### POST /api/leads/{id}/enrich
Manually trigger lead enrichment.

#### POST /api/leads/{id}/score
Manually trigger lead scoring.

#### POST /api/leads/{id}/process
Process lead through complete autonomous pipeline.

### Agent Actions

#### GET /api/leads/{id}/actions
Get all actions taken by the agent for a lead.

**Response:**
```json
[
  {
    "id": 1,
    "lead_id": 1,
    "action_type": "enrich",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:30:05Z"
  }
]
```

### Conversations

#### GET /api/leads/{id}/conversations
Get conversation history for a lead.

#### POST /api/conversations
Create a new conversation message.

### Dashboard

#### GET /api/dashboard/stats
Get dashboard statistics.

**Response:**
```json
{
  "total_leads": 150,
  "qualified_leads": 45,
  "nurture_leads": 60,
  "disqualified_leads": 45,
  "average_score": 62.5,
  "leads_by_status": {...},
  "leads_by_source": {...},
  "recent_conversions": 12
}
```

## Services

### Enrichment Service (`services/enrichment.py`)

Enriches leads with company data:

```python
from services.enrichment import enrichment_service

# Extract domain from email
domain = enrichment_service.extract_domain_from_email(email)

# Enrich lead
enrichment_data = await enrichment_service.enrich_lead(email, domain)
```

Features:
- Domain extraction from email
- Company data enrichment (Clearbit or free sources)
- Technology detection
- Firmographic data

### Scoring Service (`services/scoring.py`)

AI-powered lead scoring:

```python
from services.scoring import scoring_service

# Score a lead
results = await scoring_service.score_lead(lead_data)
# Returns: lead_score, icp_fit_score, intent_score, engagement_score
```

Scoring components:
- **ICP Fit**: Company size, industry, role matching
- **Intent**: AI analysis of buying signals
- **Engagement**: Completeness, source quality

### Agent Service (`services/agent.py`)

Autonomous decision-making and actions:

```python
from services.agent import ai_agent

# Process a lead
results = await ai_agent.process_lead(lead, db)
```

Agent capabilities:
- Enrichment orchestration
- Scoring orchestration
- Decision making
- Action execution (demo scheduling, CRM sync, notifications)
- Question generation

### Communication Service (`services/communication.py`)

Multi-channel communication:

```python
from services.communication import communication_service

# Send email
await communication_service.send_email(
    to_email="lead@company.com",
    subject="Demo Invitation",
    body="Let's schedule your demo..."
)

# Send SMS
await communication_service.send_sms(
    to_phone="+1234567890",
    message="Your demo is scheduled!"
)
```

### CRM Service (`services/crm.py`)

HubSpot integration:

```python
from services.crm import crm_service

# Sync to CRM
result = await crm_service.sync_lead_to_crm(lead_data)

# Create deal
deal_id = await crm_service.create_deal(
    contact_id=crm_id,
    deal_name="Enterprise Deal"
)
```

### Calendar Service (`services/calendar.py`)

Calendly integration:

```python
from services.calendar import calendar_service

# Create scheduling link
link = await calendar_service.create_scheduling_link(
    lead_email="lead@company.com",
    lead_name="John Doe"
)
```

## Database Models

### Lead Model
Primary model storing all lead information:
- Contact details
- Company information
- Enrichment data
- Scoring results
- AI analysis
- CRM sync status

### AgentAction Model
Audit trail of all agent actions:
- Action type
- Input/output
- Status
- Reasoning
- Timestamps

### Conversation Model
Communication history:
- Messages between agent and lead
- Channel (email, SMS, WhatsApp)
- Metadata

### SystemLog Model
System-wide logging:
- Level (INFO, WARNING, ERROR)
- Component
- Message
- Context

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `201`: Created
- `204`: No Content (delete)
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

Error response format:
```json
{
  "detail": "Error message here"
}
```

## Logging

Configure logging in `main.py`:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Logs include:
- API requests
- Lead processing steps
- Agent actions
- External API calls
- Errors and warnings

## Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Create lead
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","first_name":"Test","source":"api"}'

# Get leads
curl http://localhost:8000/api/leads
```

### Interactive API Docs

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

## Performance Tips

1. **Database Connection Pooling**: Configured in `database.py`
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=10,
       max_overflow=20
   )
   ```

2. **Async Operations**: Use `async/await` for I/O operations

3. **Batch Processing**: Process multiple leads concurrently

4. **Caching**: Implement Redis caching for enrichment data

## Security Considerations

1. **Environment Variables**: Never commit `.env` file
2. **API Keys**: Rotate regularly
3. **Database**: Use strong passwords
4. **CORS**: Configure allowed origins in production
5. **Rate Limiting**: Implement for production use

## Deployment

See main README for deployment instructions to Render or other platforms.

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running
- Verify DATABASE_URL format
- Ensure database exists

### OpenAI API Errors
- Verify API key is valid
- Check rate limits
- Ensure sufficient credits

### Import Errors
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change PORT in `.env`
- Kill process using port 8000: 
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  
  # macOS/Linux
  lsof -ti:8000 | xargs kill
  ```
