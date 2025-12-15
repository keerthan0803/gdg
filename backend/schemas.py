"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# Enums
class LeadStatusEnum(str, Enum):
    NEW = "new"
    ENRICHING = "enriching"
    SCORING = "scoring"
    QUALIFIED = "qualified"
    NURTURE = "nurture"
    DISQUALIFIED = "disqualified"
    CONTACTED = "contacted"
    SCHEDULED = "scheduled"
    CONVERTED = "converted"


class LeadSourceEnum(str, Enum):
    WEBSITE_FORM = "website_form"
    CRM_WEBHOOK = "crm_webhook"
    EMAIL = "email"
    CHAT = "chat"
    API = "api"
    MANUAL = "manual"


# Lead Schemas
class LeadCreate(BaseModel):
    """Schema for creating a new lead."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    source: LeadSourceEnum = LeadSourceEnum.API
    notes: Optional[str] = None
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower()


class LeadUpdate(BaseModel):
    """Schema for updating an existing lead."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    status: Optional[LeadStatusEnum] = None
    notes: Optional[str] = None


class LeadEnrichmentData(BaseModel):
    """Schema for enrichment data."""
    company_size: Optional[int] = None
    company_industry: Optional[str] = None
    company_location: Optional[str] = None
    company_revenue: Optional[str] = None
    company_description: Optional[str] = None
    company_founded: Optional[int] = None
    company_linkedin: Optional[str] = None
    company_twitter: Optional[str] = None
    technologies: Optional[List[str]] = None


class LeadScore(BaseModel):
    """Schema for lead scoring results."""
    lead_score: float = Field(..., ge=0, le=100)
    icp_fit_score: float = Field(..., ge=0, le=100)
    intent_score: float = Field(..., ge=0, le=100)
    engagement_score: float = Field(..., ge=0, le=100)
    buying_intent: str
    sales_stage: str
    recommended_action: str
    reasoning: str


class LeadResponse(BaseModel):
    """Schema for lead response."""
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    job_title: Optional[str]
    company_name: Optional[str]
    company_domain: Optional[str]
    company_size: Optional[int]
    company_industry: Optional[str]
    company_location: Optional[str]
    source: str
    status: str
    lead_score: float
    icp_fit_score: float
    intent_score: float
    engagement_score: float
    buying_intent: Optional[str]
    sales_stage: Optional[str]
    recommended_action: Optional[str]
    ai_reasoning: Optional[str]
    enrichment_data: Optional[Dict[str, Any]]
    technographic_data: Optional[Dict[str, Any]]
    crm_id: Optional[str]
    crm_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    last_contacted_at: Optional[datetime]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Schema for paginated lead list response."""
    total: int
    page: int
    page_size: int
    leads: List[LeadResponse]


# Agent Action Schemas
class AgentActionCreate(BaseModel):
    """Schema for creating an agent action."""
    lead_id: int
    action_type: str
    action_description: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None


class AgentActionResponse(BaseModel):
    """Schema for agent action response."""
    id: int
    lead_id: int
    action_type: str
    action_description: Optional[str]
    action_input: Optional[Dict[str, Any]]
    action_output: Optional[Dict[str, Any]]
    reasoning: Optional[str]
    confidence: Optional[float]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationCreate(BaseModel):
    """Schema for creating a conversation message."""
    lead_id: int
    sender: str  # "agent" or "lead"
    message: str
    channel: Optional[str] = "email"
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: int
    lead_id: int
    sender: str
    message: str
    channel: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Agent Decision Schemas
class AgentDecisionRequest(BaseModel):
    """Schema for agent decision request."""
    lead_id: int
    context: Optional[Dict[str, Any]] = None


class AgentDecisionResponse(BaseModel):
    """Schema for agent decision response."""
    lead_id: int
    decision: str
    actions: List[str]
    reasoning: str
    confidence: float
    next_steps: List[str]


# Dashboard Stats
class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    total_leads: int
    qualified_leads: int
    nurture_leads: int
    disqualified_leads: int
    average_score: float
    leads_by_status: Dict[str, int]
    leads_by_source: Dict[str, int]
    recent_conversions: int
