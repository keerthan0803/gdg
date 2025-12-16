"""
Main FastAPI application with all routes.
"""
import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from config import settings
from database import get_db, init_db
from models import Lead, AgentAction, Conversation, SystemLog, LeadStatus, LeadSource
from schemas import (
    LeadCreate, LeadUpdate, LeadResponse, LeadListResponse,
    AgentActionResponse, ConversationResponse, ConversationCreate,
    AgentDecisionRequest, AgentDecisionResponse, DashboardStats
)
from services.agent import ai_agent
from services.enrichment import enrichment_service
from services.scoring import scoring_service

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Autonomous Lead Qualification Agent"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "AI Lead Qualification Agent API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== LEAD ENDPOINTS ====================

@app.post("/api/leads", response_model=LeadResponse, status_code=201)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new lead and trigger autonomous processing.
    
    This endpoint:
    1. Creates the lead in the database
    2. Automatically triggers enrichment
    3. Automatically scores the lead
    4. Automatically takes appropriate actions
    """
    # Check if lead already exists
    existing_lead = db.query(Lead).filter(Lead.email == lead_data.email).first()
    if existing_lead:
        raise HTTPException(status_code=400, detail="Lead with this email already exists")
    
    # Create new lead (convert empty strings to None)
    lead = Lead(
        email=lead_data.email,
        first_name=lead_data.first_name or None,
        last_name=lead_data.last_name or None,
        phone=lead_data.phone or None,
        job_title=lead_data.job_title or None,
        company_name=lead_data.company_name or None,
        company_domain=lead_data.company_domain or None,
        source=lead_data.source,
        notes=lead_data.notes or None,
        status=LeadStatus.NEW
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    logger.info(f"Created new lead: {lead.id} - {lead.email}")
    
    # Trigger autonomous agent processing (async in background)
    try:
        await ai_agent.process_lead(lead, db)
        db.refresh(lead)
    except Exception as e:
        logger.error(f"Error processing lead {lead.id}: {e}")
    
    return lead


@app.get("/api/leads", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all leads with pagination and filtering.
    """
    query = db.query(Lead)
    
    # Apply filters
    if status:
        query = query.filter(Lead.status == status)
    if min_score is not None:
        query = query.filter(Lead.lead_score >= min_score)
    if source:
        query = query.filter(Lead.source == source)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    leads = query.order_by(desc(Lead.created_at)).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "leads": leads
    }


@app.get("/api/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific lead by ID."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.patch("/api/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db)
):
    """Update a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Update fields
    for field, value in lead_update.dict(exclude_unset=True).items():
        setattr(lead, field, value)
    
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    
    logger.info(f"Updated lead: {lead_id}")
    return lead


@app.delete("/api/leads/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Delete a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    
    logger.info(f"Deleted lead: {lead_id}")
    return None


# ==================== ENRICHMENT ENDPOINTS ====================

@app.post("/api/leads/{lead_id}/enrich")
async def enrich_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Manually trigger lead enrichment."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    try:
        # Extract domain
        domain = enrichment_service.extract_domain_from_email(lead.email)
        if domain:
            lead.company_domain = domain
        
        # Enrich
        enrichment_data = await enrichment_service.enrich_lead(lead.email, domain)
        
        # Update lead
        if enrichment_data:
            lead.enrichment_data = enrichment_data
            if enrichment_data.get("company_name"):
                lead.company_name = enrichment_data["company_name"]
            if enrichment_data.get("company_size"):
                lead.company_size = enrichment_data["company_size"]
            if enrichment_data.get("company_industry"):
                lead.company_industry = enrichment_data["company_industry"]
        
        db.commit()
        db.refresh(lead)
        
        return {
            "success": True,
            "lead_id": lead_id,
            "enrichment_data": enrichment_data
        }
        
    except Exception as e:
        logger.error(f"Error enriching lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SCORING ENDPOINTS ====================

@app.post("/api/leads/{lead_id}/score")
async def score_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Manually trigger lead scoring."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    try:
        # Prepare lead data
        lead_data = {
            "email": lead.email,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "phone": lead.phone,
            "job_title": lead.job_title,
            "company_name": lead.company_name,
            "company_domain": lead.company_domain,
            "company_size": lead.company_size,
            "company_industry": lead.company_industry,
            "company_location": lead.company_location,
            "source": lead.source.value if lead.source else None,
            "notes": lead.notes
        }
        
        # Score the lead
        scoring_results = await scoring_service.score_lead(lead_data)
        
        # Update lead
        lead.lead_score = scoring_results["lead_score"]
        lead.icp_fit_score = scoring_results["icp_fit_score"]
        lead.intent_score = scoring_results["intent_score"]
        lead.engagement_score = scoring_results["engagement_score"]
        lead.buying_intent = scoring_results["buying_intent"]
        lead.sales_stage = scoring_results["sales_stage"]
        lead.recommended_action = scoring_results["recommended_action"]
        lead.ai_reasoning = scoring_results["reasoning"]
        
        db.commit()
        db.refresh(lead)
        
        return {
            "success": True,
            "lead_id": lead_id,
            "scoring_results": scoring_results
        }
        
    except Exception as e:
        logger.error(f"Error scoring lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AGENT ENDPOINTS ====================

@app.post("/api/leads/{lead_id}/process")
async def process_lead_with_agent(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """
    Process lead with autonomous agent.
    This runs the complete qualification pipeline.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    try:
        results = await ai_agent.process_lead(lead, db)
        db.refresh(lead)
        
        return {
            "success": True,
            "results": results,
            "lead": lead
        }
        
    except Exception as e:
        logger.error(f"Error processing lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads/{lead_id}/actions", response_model=List[AgentActionResponse])
async def get_lead_actions(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get all actions taken by the agent for a lead."""
    actions = db.query(AgentAction).filter(
        AgentAction.lead_id == lead_id
    ).order_by(desc(AgentAction.created_at)).all()
    
    return actions


# ==================== CONVERSATION ENDPOINTS ====================

@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation message."""
    conv = Conversation(
        lead_id=conversation.lead_id,
        sender=conversation.sender,
        message=conversation.message,
        channel=conversation.channel,
        metadata=conversation.metadata
    )
    
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    return conv


@app.get("/api/leads/{lead_id}/conversations", response_model=List[ConversationResponse])
async def get_lead_conversations(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get all conversations for a lead."""
    conversations = db.query(Conversation).filter(
        Conversation.lead_id == lead_id
    ).order_by(Conversation.created_at).all()
    
    return conversations


# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    total_leads = db.query(Lead).count()
    
    qualified_leads = db.query(Lead).filter(
        Lead.status == LeadStatus.QUALIFIED
    ).count()
    
    nurture_leads = db.query(Lead).filter(
        Lead.status == LeadStatus.NURTURE
    ).count()
    
    disqualified_leads = db.query(Lead).filter(
        Lead.status == LeadStatus.DISQUALIFIED
    ).count()
    
    # Average score
    avg_score_result = db.query(func.avg(Lead.lead_score)).scalar()
    average_score = float(avg_score_result) if avg_score_result else 0.0
    
    # Leads by status
    status_counts = db.query(
        Lead.status, func.count(Lead.id)
    ).group_by(Lead.status).all()
    
    leads_by_status = {
        status.value: count for status, count in status_counts
    }
    
    # Leads by source
    source_counts = db.query(
        Lead.source, func.count(Lead.id)
    ).group_by(Lead.source).all()
    
    leads_by_source = {
        source.value: count for source, count in source_counts
    }
    
    # Recent conversions (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_conversions = db.query(Lead).filter(
        Lead.status == LeadStatus.CONVERTED,
        Lead.updated_at >= thirty_days_ago
    ).count()
    
    return {
        "total_leads": total_leads,
        "qualified_leads": qualified_leads,
        "nurture_leads": nurture_leads,
        "disqualified_leads": disqualified_leads,
        "average_score": round(average_score, 2),
        "leads_by_status": leads_by_status,
        "leads_by_source": leads_by_source,
        "recent_conversions": recent_conversions
    }


# ==================== WEBHOOK ENDPOINTS ====================

@app.post("/api/webhooks/crm")
async def crm_webhook(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for CRM integrations (HubSpot, Salesforce, etc.)
    
    Automatically creates leads from CRM form submissions and contact updates.
    
    Setup Instructions:
    1. HubSpot: Go to Settings > Integrations > Webhooks
    2. Add this URL: https://your-domain.com/api/webhooks/crm
    3. Subscribe to: Contact creation, Form submissions
    4. Configure authentication if needed
    """
    try:
        logger.info(f"Received CRM webhook: {request}")
        
        # Extract lead data from webhook payload
        # Different CRMs send different formats, adapt as needed
        lead_data = {}
        
        # HubSpot format
        if 'properties' in request:
            props = request.get('properties', {})
            lead_data = {
                'email': props.get('email', {}).get('value'),
                'first_name': props.get('firstname', {}).get('value'),
                'last_name': props.get('lastname', {}).get('value'),
                'phone': props.get('phone', {}).get('value'),
                'company_name': props.get('company', {}).get('value'),
                'job_title': props.get('jobtitle', {}).get('value'),
            }
        # Generic format
        else:
            lead_data = {
                'email': request.get('email'),
                'first_name': request.get('first_name') or request.get('firstName'),
                'last_name': request.get('last_name') or request.get('lastName'),
                'phone': request.get('phone'),
                'company_name': request.get('company') or request.get('company_name'),
                'job_title': request.get('job_title') or request.get('jobTitle'),
            }
        
        # Validate email exists
        if not lead_data.get('email'):
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Check if lead already exists
        existing_lead = db.query(Lead).filter(Lead.email == lead_data['email']).first()
        if existing_lead:
            logger.info(f"Lead already exists: {lead_data['email']}")
            return {"status": "exists", "lead_id": existing_lead.id}
        
        # Create new lead
        lead = Lead(
            email=lead_data['email'],
            first_name=lead_data.get('first_name'),
            last_name=lead_data.get('last_name'),
            phone=lead_data.get('phone'),
            company_name=lead_data.get('company_name'),
            job_title=lead_data.get('job_title'),
            source=LeadSource.CRM_WEBHOOK,
            status=LeadStatus.NEW
        )
        
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Created lead from CRM webhook: {lead.id} - {lead.email}")
        
        # Trigger autonomous processing
        try:
            await ai_agent.process_lead(lead, db)
            db.refresh(lead)
        except Exception as e:
            logger.error(f"Error processing lead {lead.id}: {e}")
        
        return {
            "status": "success",
            "lead_id": lead.id,
            "message": "Lead created and processed automatically"
        }
        
    except Exception as e:
        logger.error(f"CRM webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/webhooks/email")
async def email_webhook(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for email integrations (SendGrid, Mailgun, etc.)
    
    Automatically creates leads from email inquiries.
    
    Setup Instructions:
    1. SendGrid: Go to Mail Settings > Inbound Parse
    2. Set destination URL: https://your-domain.com/api/webhooks/email
    3. Configure domain/subdomain (e.g., leads@yourdomain.com)
    """
    try:
        logger.info(f"Received email webhook: {request}")
        
        # Extract email data
        from_email = request.get('from') or request.get('sender')
        subject = request.get('subject', '')
        body = request.get('text') or request.get('html', '')
        
        if not from_email:
            raise HTTPException(status_code=400, detail="From email is required")
        
        # Parse email address
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_email)
        if not email_match:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        email = email_match.group(0)
        
        # Extract name from email sender
        name_match = re.match(r'^(.*?)\s*<', from_email)
        name_parts = name_match.group(1).split() if name_match else []
        first_name = name_parts[0] if len(name_parts) > 0 else None
        last_name = name_parts[-1] if len(name_parts) > 1 else None
        
        # Check if lead exists
        existing_lead = db.query(Lead).filter(Lead.email == email).first()
        if existing_lead:
            logger.info(f"Lead already exists: {email}")
            return {"status": "exists", "lead_id": existing_lead.id}
        
        # Create new lead
        lead = Lead(
            email=email,
            first_name=first_name,
            last_name=last_name,
            source=LeadSource.EMAIL,
            status=LeadStatus.NEW,
            notes=f"Email Subject: {subject}\n\nMessage: {body[:500]}"
        )
        
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Created lead from email: {lead.id} - {lead.email}")
        
        # Trigger autonomous processing
        try:
            await ai_agent.process_lead(lead, db)
            db.refresh(lead)
        except Exception as e:
            logger.error(f"Error processing lead {lead.id}: {e}")
        
        return {
            "status": "success",
            "lead_id": lead.id,
            "message": "Lead created from email and processed automatically"
        }
        
    except Exception as e:
        logger.error(f"Email webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/webhooks/form")
async def form_webhook(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for website form submissions.
    
    Add this to your website contact/demo form to automatically capture leads.
    
    Example JavaScript:
    ```javascript
    fetch('https://your-domain.com/api/webhooks/form', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            email: email,
            first_name: firstName,
            last_name: lastName,
            company_name: company,
            phone: phone,
            message: message
        })
    });
    ```
    """
    try:
        logger.info(f"Received form webhook: {request}")
        
        email = request.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Check if lead exists
        existing_lead = db.query(Lead).filter(Lead.email == email).first()
        if existing_lead:
            logger.info(f"Lead already exists: {email}")
            return {"status": "exists", "lead_id": existing_lead.id}
        
        # Create new lead
        lead = Lead(
            email=email,
            first_name=request.get('first_name') or request.get('firstName'),
            last_name=request.get('last_name') or request.get('lastName'),
            phone=request.get('phone'),
            company_name=request.get('company_name') or request.get('company'),
            job_title=request.get('job_title') or request.get('jobTitle'),
            source=LeadSource.WEBSITE_FORM,
            status=LeadStatus.NEW,
            notes=request.get('message') or request.get('comments')
        )
        
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Created lead from form: {lead.id} - {lead.email}")
        
        # Trigger autonomous processing
        try:
            await ai_agent.process_lead(lead, db)
            db.refresh(lead)
        except Exception as e:
            logger.error(f"Error processing lead {lead.id}: {e}")
        
        return {
            "status": "success",
            "lead_id": lead.id,
            "message": "Thank you! We'll be in touch soon.",
            "lead_score": lead.lead_score,
            "recommended_action": lead.recommended_action
        }
        
    except Exception as e:
        logger.error(f"Form webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GMAIL INTEGRATION ENDPOINTS ====================

@app.post("/api/gmail/sync")
async def sync_gmail_emails(
    max_emails: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Sync emails from Gmail and create leads from sales inquiries.
    
    This endpoint:
    1. Authenticates with Gmail API
    2. Fetches unread emails matching sales criteria
    3. Extracts lead information from emails
    4. Creates leads and triggers autonomous processing
    5. Marks processed emails as read
    """
    from services.gmail import gmail_service
    
    try:
        # Get unread sales emails
        emails = gmail_service.get_unread_emails(max_results=max_emails)
        
        if not emails:
            return {
                "status": "success",
                "message": "No new sales emails found",
                "emails_processed": 0,
                "leads_created": 0
            }
        
        leads_created = []
        errors = []
        
        for email_data in emails:
            try:
                # Extract lead information
                lead_info = gmail_service.extract_lead_info(email_data)
                
                # Check if lead already exists
                existing_lead = db.query(Lead).filter(
                    Lead.email == lead_info['email']
                ).first()
                
                if existing_lead:
                    logger.info(f"Lead already exists: {lead_info['email']}")
                    # Mark email as read anyway
                    gmail_service.mark_as_read(email_data['id'])
                    continue
                
                # Split full name into first and last name
                full_name = lead_info.get('full_name', '')
                name_parts = full_name.split(None, 1) if full_name else []
                first_name = name_parts[0] if len(name_parts) > 0 else None
                last_name = name_parts[1] if len(name_parts) > 1 else None
                
                # Create new lead
                lead = Lead(
                    email=lead_info['email'],
                    first_name=first_name,
                    last_name=last_name,
                    company_name=lead_info.get('company'),
                    phone=lead_info.get('phone'),
                    source=LeadSource.EMAIL,
                    status=LeadStatus.NEW,
                    notes=lead_info.get('notes'),
                    enrichment_data={
                        'gmail_thread_id': email_data.get('thread_id'),
                        'gmail_message_id': email_data.get('id'),
                        'original_subject': email_data.get('subject'),
                        'received_date': email_data.get('date')
                    }
                )
                
                db.add(lead)
                db.commit()
                db.refresh(lead)
                
                logger.info(f"Created lead from Gmail: {lead.id} - {lead.email}")
                
                # Trigger autonomous processing
                try:
                    await ai_agent.process_lead(lead, db)
                    db.refresh(lead)
                except Exception as e:
                    logger.error(f"Error processing lead {lead.id}: {e}")
                
                # Mark email as read
                gmail_service.mark_as_read(email_data['id'])
                
                # Build full name for display
                display_name = f"{lead.first_name or ''} {lead.last_name or ''}".strip() or lead.email
                
                leads_created.append({
                    'lead_id': lead.id,
                    'email': lead.email,
                    'name': display_name,
                    'score': lead.lead_score
                })
                
            except Exception as e:
                error_msg = f"Error processing email from {email_data.get('sender_email')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return {
            "status": "success",
            "message": f"Processed {len(emails)} emails",
            "emails_processed": len(emails),
            "leads_created": len(leads_created),
            "leads": leads_created,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"Gmail sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gmail/status")
async def gmail_status():
    """Check Gmail API authentication status."""
    from services.gmail import gmail_service
    
    try:
        is_authenticated = gmail_service.authenticate()
        
        return {
            "authenticated": is_authenticated,
            "credentials_file_exists": os.path.exists(settings.GMAIL_CREDENTIALS_FILE),
            "token_file_exists": os.path.exists(settings.GMAIL_TOKEN_FILE),
            "search_query": settings.GMAIL_SEARCH_QUERY
        }
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e)
        }


@app.get("/api/gmail/authorize")
async def gmail_authorize():
    """
    Initiate Gmail OAuth authorization flow.
    Returns authorization URL to redirect user to.
    """
    from services.gmail import gmail_service
    
    try:
        auth_url = gmail_service.get_authorization_url()
        
        if not auth_url:
            raise HTTPException(status_code=500, detail="Failed to generate authorization URL")
        
        return {
            "authorization_url": auth_url,
            "message": "Please visit the authorization URL to grant Gmail access"
        }
        
    except Exception as e:
        logger.error(f"Gmail authorization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gmail/oauth2callback")
async def gmail_oauth_callback(
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="State parameter"),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth2 callback from Google.
    This endpoint receives the authorization code and exchanges it for tokens.
    """
    from services.gmail import gmail_service
    
    try:
        success = gmail_service.handle_oauth_callback(code, state)
        
        if not success:
            raise HTTPException(status_code=400, detail="OAuth callback failed")
        
        # Return HTML page with success message
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gmail Authorization Successful</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }
                h1 { color: #28a745; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; }
                .button {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                .button:hover { background: #5568d3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✓ Authorization Successful!</h1>
                <p>Your Gmail account has been connected successfully.</p>
                <p>You can now sync sales emails and automatically create leads.</p>
                <a href="/" class="button">Go to Dashboard</a>
            </div>
            <script>
                // Auto-close after 3 seconds
                setTimeout(() => window.close(), 3000);
            </script>
        </body>
        </html>
        """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gmail Authorization Failed</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #f44336;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                }}
                h1 {{ color: #f44336; }}
                p {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✗ Authorization Failed</h1>
                <p>Error: {str(e)}</p>
                <p>Please try again.</p>
            </div>
        </body>
        </html>
        """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content, status_code=400)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
