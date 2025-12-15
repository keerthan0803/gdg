"""
Database models for the AI Lead Qualification Agent.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Enum
)
from sqlalchemy.sql import func
from datetime import datetime
from database import Base
import enum


class LeadStatus(str, enum.Enum):
    """Lead status enumeration."""
    NEW = "new"
    ENRICHING = "enriching"
    SCORING = "scoring"
    QUALIFIED = "qualified"
    NURTURE = "nurture"
    DISQUALIFIED = "disqualified"
    CONTACTED = "contacted"
    SCHEDULED = "scheduled"
    CONVERTED = "converted"


class LeadSource(str, enum.Enum):
    """Lead source enumeration."""
    WEBSITE_FORM = "website_form"
    CRM_WEBHOOK = "crm_webhook"
    EMAIL = "email"
    CHAT = "chat"
    API = "api"
    MANUAL = "manual"


class AgentActionType(str, enum.Enum):
    """Agent action type enumeration."""
    ENRICH = "enrich"
    SCORE = "score"
    ASK_QUESTION = "ask_question"
    SEND_EMAIL = "send_email"
    SEND_MESSAGE = "send_message"
    SCHEDULE_DEMO = "schedule_demo"
    SYNC_CRM = "sync_crm"
    NOTIFY_SALES = "notify_sales"
    ADD_TO_NURTURE = "add_to_nurture"
    DISQUALIFY = "disqualify"


class Lead(Base):
    """Lead model - stores all lead information."""
    __tablename__ = "leads"
    
    # Primary identifiers
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Contact information
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    job_title = Column(String)
    
    # Company information
    company_name = Column(String)
    company_domain = Column(String, index=True)
    company_size = Column(Integer)
    company_industry = Column(String)
    company_location = Column(String)
    company_revenue = Column(String)
    
    # Lead metadata
    source = Column(Enum(LeadSource), default=LeadSource.API)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    
    # Enrichment data (stored as JSON)
    enrichment_data = Column(JSON)
    technographic_data = Column(JSON)
    
    # AI scoring and classification
    lead_score = Column(Float, default=0.0, index=True)
    icp_fit_score = Column(Float, default=0.0)
    intent_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    
    # AI-generated insights
    buying_intent = Column(String)
    sales_stage = Column(String)
    recommended_action = Column(String)
    ai_reasoning = Column(Text)
    
    # Qualification questions and responses
    qualification_questions = Column(JSON)
    qualification_responses = Column(JSON)
    
    # CRM sync
    crm_id = Column(String, index=True)
    crm_synced_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted_at = Column(DateTime)
    
    # Additional notes
    notes = Column(Text)


class AgentAction(Base):
    """Agent action log - tracks all autonomous agent actions."""
    __tablename__ = "agent_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True, nullable=False)
    
    # Action details
    action_type = Column(Enum(AgentActionType), nullable=False)
    action_description = Column(Text)
    
    # Action input and output
    action_input = Column(JSON)
    action_output = Column(JSON)
    
    # AI decision reasoning
    reasoning = Column(Text)
    confidence = Column(Float)
    
    # Status
    status = Column(String, default="pending")  # pending, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)


class Conversation(Base):
    """Conversation log - stores agent-lead interactions."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True, nullable=False)
    
    # Message details
    sender = Column(String, nullable=False)  # "agent" or "lead"
    message = Column(Text, nullable=False)
    channel = Column(String)  # email, whatsapp, sms, chat
    
    # Message metadata
    message_metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SystemLog(Base):
    """System log - tracks system events and errors."""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Log details
    level = Column(String, index=True)  # INFO, WARNING, ERROR, CRITICAL
    component = Column(String, index=True)
    message = Column(Text)
    
    # Additional context
    context = Column(JSON)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
