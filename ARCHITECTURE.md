# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Web Browser │  │  Mobile App  │  │   API Client │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                    APPLICATION LAYER                              │
│                             │                                     │
│  ┌──────────────────────────▼───────────────────────────┐       │
│  │            React Frontend (TypeScript)                │       │
│  │  - Dashboard UI                                       │       │
│  │  - Lead Management                                    │       │
│  │  - Real-time Updates                                  │       │
│  └──────────────────────────┬───────────────────────────┘       │
│                             │                                     │
│                    ┌────────▼────────┐                           │
│                    │   API Gateway   │                           │
│                    └────────┬────────┘                           │
│                             │                                     │
│  ┌──────────────────────────▼───────────────────────────┐       │
│  │          FastAPI Backend (Python)                     │       │
│  │  ┌─────────────────────────────────────────────┐     │       │
│  │  │           API Routes Layer                   │     │       │
│  │  │  - Lead CRUD Operations                      │     │       │
│  │  │  - Dashboard Endpoints                       │     │       │
│  │  │  - Webhook Handlers                          │     │       │
│  │  └─────────────────┬───────────────────────────┘     │       │
│  │                    │                                  │       │
│  │  ┌─────────────────▼───────────────────────────┐     │       │
│  │  │         Business Logic Layer                 │     │       │
│  │  │                                              │     │       │
│  │  │  ┌──────────────────────────────────────┐   │     │       │
│  │  │  │    Enrichment Service                │   │     │       │
│  │  │  │  - Domain Extraction                 │   │     │       │
│  │  │  │  - Company Data Fetching             │   │     │       │
│  │  │  │  - Technographic Detection           │   │     │       │
│  │  │  └──────────────────────────────────────┘   │     │       │
│  │  │                                              │     │       │
│  │  │  ┌──────────────────────────────────────┐   │     │       │
│  │  │  │    AI Scoring Service                │   │     │       │
│  │  │  │  - ICP Fit Calculation               │   │     │       │
│  │  │  │  - Intent Analysis (GPT-4)           │   │     │       │
│  │  │  │  - Engagement Scoring                │   │     │       │
│  │  │  │  - Sales Stage Classification        │   │     │       │
│  │  │  └──────────────────────────────────────┘   │     │       │
│  │  │                                              │     │       │
│  │  │  ┌──────────────────────────────────────┐   │     │       │
│  │  │  │    Autonomous Agent                  │   │     │       │
│  │  │  │  - Decision Engine                   │   │     │       │
│  │  │  │  - Action Orchestration              │   │     │       │
│  │  │  │  - Question Generation               │   │     │       │
│  │  │  │  - Workflow Automation               │   │     │       │
│  │  │  └──────────────────────────────────────┘   │     │       │
│  │  │                                              │     │       │
│  │  │  ┌──────────────────────────────────────┐   │     │       │
│  │  │  │    Integration Services              │   │     │       │
│  │  │  │  - Communication (Email/SMS)         │   │     │       │
│  │  │  │  - CRM Sync (HubSpot)                │   │     │       │
│  │  │  │  - Calendar (Calendly)               │   │     │       │
│  │  │  └──────────────────────────────────────┘   │     │       │
│  │  └──────────────────────────────────────────────┘     │       │
│  └────────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                      DATA LAYER                                   │
│                             │                                     │
│  ┌──────────────────────────▼───────────────────────────┐       │
│  │          PostgreSQL Database                          │       │
│  │  ┌─────────────────────────────────────────────┐     │       │
│  │  │  Core Tables                                 │     │       │
│  │  │  - leads (contact & enrichment data)        │     │       │
│  │  │  - agent_actions (audit trail)              │     │       │
│  │  │  - conversations (communication history)    │     │       │
│  │  │  - system_logs (system events)              │     │       │
│  │  └─────────────────────────────────────────────┘     │       │
│  └────────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                   EXTERNAL SERVICES                               │
│                             │                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐            │
│  │   OpenAI    │  │  SendGrid   │  │   Twilio     │            │
│  │   GPT-4     │  │   Email     │  │  SMS/WhatsApp│            │
│  └─────────────┘  └─────────────┘  └──────────────┘            │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐            │
│  │  HubSpot    │  │  Calendly   │  │  Clearbit    │            │
│  │    CRM      │  │  Scheduling │  │  Enrichment  │            │
│  └─────────────┘  └─────────────┘  └──────────────┘            │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Lead Ingestion & Processing Pipeline

```
┌──────────────┐
│  Lead Source │
│ (Form/API)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 1. INGESTION PHASE                           │
│  ┌────────────────────────────────────────┐  │
│  │  - Validate email format               │  │
│  │  - Check for duplicates                │  │
│  │  - Store raw lead data                 │  │
│  │  - Create audit log entry              │  │
│  └────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ 2. ENRICHMENT PHASE                          │
│  ┌────────────────────────────────────────┐  │
│  │  Step 1: Extract domain from email    │  │
│  │         ↓                              │  │
│  │  Step 2: Filter free email providers  │  │
│  │         ↓                              │  │
│  │  Step 3: Fetch company data            │  │
│  │         ├─→ Clearbit API (if available)│  │
│  │         └─→ Free sources (fallback)    │  │
│  │         ↓                              │  │
│  │  Step 4: Detect technologies           │  │
│  │         ↓                              │  │
│  │  Step 5: Update lead record            │  │
│  └────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ 3. SCORING PHASE                             │
│  ┌────────────────────────────────────────┐  │
│  │  Component 1: ICP Fit Score (35%)      │  │
│  │   - Company size match                 │  │
│  │   - Industry alignment                 │  │
│  │   - Decision-maker role                │  │
│  │   - Business email domain              │  │
│  │         ↓                              │  │
│  │  Component 2: Intent Score (40%)       │  │
│  │   - AI analysis via GPT-4              │  │
│  │   - Context understanding              │  │
│  │   - Buying signal detection            │  │
│  │   - Urgency assessment                 │  │
│  │         ↓                              │  │
│  │  Component 3: Engagement Score (25%)   │  │
│  │   - Information completeness           │  │
│  │   - Source quality                     │  │
│  │   - Additional context                 │  │
│  │         ↓                              │  │
│  │  Calculate: Overall Lead Score         │  │
│  │  = (ICP×0.35 + Intent×0.40 + Eng×0.25)│  │
│  └────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ 4. DECISION PHASE                            │
│  ┌────────────────────────────────────────┐  │
│  │  IF Score ≥ 75 (HIGH QUALITY)          │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │ → Schedule demo                  │  │  │
│  │  │ → Sync to CRM                    │  │  │
│  │  │ → Notify sales team              │  │  │
│  │  │ → Mark as "Qualified"            │  │  │
│  │  └──────────────────────────────────┘  │  │
│  │                                        │  │
│  │  ELSE IF Score 50-74 (MEDIUM)         │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │ → Generate questions             │  │  │
│  │  │ → Send via email                 │  │  │
│  │  │ → Mark as "Nurture"              │  │  │
│  │  │ → Wait for response              │  │  │
│  │  └──────────────────────────────────┘  │  │
│  │                                        │  │
│  │  ELSE (LOW QUALITY)                   │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │ → Add to nurture workflow        │  │  │
│  │  │ → Mark as "Disqualified"         │  │  │
│  │  │ → No immediate action            │  │  │
│  │  └──────────────────────────────────┘  │  │
│  └────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ 5. ACTION EXECUTION PHASE                    │
│  ┌────────────────────────────────────────┐  │
│  │  Execute decided actions:               │  │
│  │  - Create agent_action records         │  │
│  │  - Call external APIs                  │  │
│  │  - Send communications                 │  │
│  │  - Update CRM                          │  │
│  │  - Log all outcomes                    │  │
│  └────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
            ┌──────────┐
            │ Complete │
            └──────────┘
```

## Component Interactions

### Scoring System Detail

```
┌─────────────────────────────────────────────────────────────┐
│                    SCORING ENGINE                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ICP Fit Calculator                       │  │
│  │                                                       │  │
│  │  Input: Company data + ICP criteria                  │  │
│  │    ├─→ Company size: [10-5000] employees             │  │
│  │    ├─→ Industry: Technology, SaaS, etc.              │  │
│  │    ├─→ Role: CEO, CTO, VP, Director                  │  │
│  │    └─→ Email domain: Business vs free                │  │
│  │                ↓                                      │  │
│  │  Calculation Logic:                                   │  │
│  │    Company size match:    30 points                  │  │
│  │    Industry match:        30 points                  │  │
│  │    Decision-maker role:   25 points                  │  │
│  │    Business email:        15 points                  │  │
│  │                ↓                                      │  │
│  │  Output: ICP Fit Score (0-100)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ├─────────────────┐              │
│                            │                 │              │
│  ┌────────────────────────▼──────────┐   ┌─▼────────────┐  │
│  │   Intent Analyzer (GPT-4)         │   │  Engagement  │  │
│  │                                   │   │  Calculator  │  │
│  │  Prompt Engineering:              │   │              │  │
│  │  - Analyze lead context           │   │  Factors:    │  │
│  │  - Identify pain points           │   │  - Complete  │  │
│  │  - Detect urgency signals         │   │    info      │  │
│  │  - Assess buying intent           │   │  - Phone     │  │
│  │                                   │   │    provided  │  │
│  │  AI Response:                     │   │  - Source    │  │
│  │  {                                │   │    quality   │  │
│  │    "intent_score": 0-100,         │   │  - Notes     │  │
│  │    "intent_level": "high",        │   │              │  │
│  │    "buying_signals": [...],       │   │  Output:     │  │
│  │    "concerns": [...],             │   │  0-100       │  │
│  │    "reasoning": "..."             │   │              │  │
│  │  }                                │   │              │  │
│  └───────────────────────────────────┘   └──────────────┘  │
│                            │                 │              │
│                            └────────┬────────┘              │
│                                     │                       │
│                    ┌────────────────▼─────────────────┐    │
│                    │    Score Aggregator              │    │
│                    │                                  │    │
│                    │  Overall = (ICP×0.35 +           │    │
│                    │            Intent×0.40 +         │    │
│                    │            Engagement×0.25)      │    │
│                    │                                  │    │
│                    │  Threshold Classification:       │    │
│                    │  ≥75: Qualified                  │    │
│                    │  50-74: Nurture                  │    │
│                    │  <50: Disqualified               │    │
│                    └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Agent Decision Tree

```
                    ┌──────────────┐
                    │  Lead Scored │
                    └──────┬───────┘
                           │
                ┌──────────▼──────────┐
                │  Evaluate Score     │
                └──────────┬──────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
    │ Score ≥ 75  │ │ Score 50-74│ │ Score < 50 │
    │   (High)    │ │  (Medium)  │ │   (Low)    │
    └──────┬──────┘ └─────┬──────┘ └─────┬──────┘
           │               │               │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
    │ Actions:    │ │ Actions:   │ │ Actions:   │
    │ 1. CRM Sync │ │ 1. Generate│ │ 1. Add to  │
    │ 2. Schedule │ │    Questions│ │    Nurture │
    │    Demo     │ │ 2. Send    │ │ 2. Log     │
    │ 3. Notify   │ │    Email   │ │    Decision│
    │    Sales    │ │ 3. Wait    │ │            │
    └─────────────┘ └────────────┘ └────────────┘
```

## Database Schema

```sql
┌─────────────────────────────────────────────────────────────┐
│                         LEADS TABLE                          │
├──────────────────┬──────────────────────────────────────────┤
│ id               │ PRIMARY KEY                              │
│ email            │ UNIQUE, NOT NULL (indexed)               │
│ first_name       │ VARCHAR                                  │
│ last_name        │ VARCHAR                                  │
│ phone            │ VARCHAR                                  │
│ job_title        │ VARCHAR                                  │
│ company_name     │ VARCHAR                                  │
│ company_domain   │ VARCHAR (indexed)                        │
│ company_size     │ INTEGER                                  │
│ company_industry │ VARCHAR                                  │
│ company_location │ VARCHAR                                  │
│ source           │ ENUM (indexed)                           │
│ status           │ ENUM (indexed)                           │
│ enrichment_data  │ JSONB                                    │
│ lead_score       │ FLOAT (indexed)                          │
│ icp_fit_score    │ FLOAT                                    │
│ intent_score     │ FLOAT                                    │
│ engagement_score │ FLOAT                                    │
│ buying_intent    │ VARCHAR                                  │
│ sales_stage      │ VARCHAR                                  │
│ recommended_action│ VARCHAR                                 │
│ ai_reasoning     │ TEXT                                     │
│ crm_id           │ VARCHAR (indexed)                        │
│ created_at       │ TIMESTAMP                                │
│ updated_at       │ TIMESTAMP                                │
└──────────────────┴──────────────────────────────────────────┘
                           │
                           │ 1:N
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    AGENT_ACTIONS TABLE                       │
├──────────────────┬──────────────────────────────────────────┤
│ id               │ PRIMARY KEY                              │
│ lead_id          │ FOREIGN KEY → leads.id (indexed)         │
│ action_type      │ ENUM                                     │
│ action_description│ TEXT                                    │
│ action_input     │ JSONB                                    │
│ action_output    │ JSONB                                    │
│ reasoning        │ TEXT                                     │
│ confidence       │ FLOAT                                    │
│ status           │ VARCHAR                                  │
│ error_message    │ TEXT                                     │
│ created_at       │ TIMESTAMP                                │
│ completed_at     │ TIMESTAMP                                │
└──────────────────┴──────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   CONVERSATIONS TABLE                        │
├──────────────────┬──────────────────────────────────────────┤
│ id               │ PRIMARY KEY                              │
│ lead_id          │ FOREIGN KEY → leads.id (indexed)         │
│ sender           │ VARCHAR ('agent' or 'lead')              │
│ message          │ TEXT                                     │
│ channel          │ VARCHAR (email, sms, whatsapp)           │
│ metadata         │ JSONB                                    │
│ created_at       │ TIMESTAMP                                │
└──────────────────┴──────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                         │
│                                                              │
│  Layer 1: Network Security                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │ - HTTPS/TLS encryption                             │     │
│  │ - CORS policy enforcement                          │     │
│  │ - Rate limiting                                    │     │
│  │ - DDoS protection                                  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Layer 2: Application Security                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ - Input validation (Pydantic)                      │     │
│  │ - SQL injection prevention (SQLAlchemy ORM)        │     │
│  │ - XSS protection                                   │     │
│  │ - Environment variable management                  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Layer 3: Data Security                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │ - Database encryption at rest                      │     │
│  │ - Secure API key storage                           │     │
│  │ - Audit logging                                    │     │
│  │ - Regular backups                                  │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- Load balancer distributes traffic
- Multiple backend instances
- Database read replicas
- Caching layer (Redis)

### Vertical Scaling
- Increase server resources
- Database optimization
- Query performance tuning
- Connection pooling

### Async Processing
- Background job queue (Celery)
- Event-driven architecture
- Webhook processing
- Batch operations

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                          │
│                                                              │
│  Application Metrics                                        │
│  - Request rate, response time                              │
│  - Error rate, success rate                                 │
│  - Lead processing time                                     │
│  - AI API latency                                           │
│                                                              │
│  Infrastructure Metrics                                     │
│  - CPU, Memory, Disk usage                                  │
│  - Database connections                                     │
│  - Network I/O                                              │
│                                                              │
│  Business Metrics                                           │
│  - Leads processed per hour                                 │
│  - Qualification rate                                       │
│  - Average lead score                                       │
│  - Conversion funnel                                        │
└─────────────────────────────────────────────────────────────┘
```

This architecture supports the core requirements of the AI-powered lead qualification system while maintaining scalability, security, and maintainability.
