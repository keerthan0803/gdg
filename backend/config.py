"""
Configuration management for the AI Lead Qualification Agent.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "AI Lead Qualification Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/lead_qualification"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Email Service (SendGrid)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@yourdomain.com"
    
    # Messaging Services (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    TWILIO_SMS_NUMBER: str = ""
    
    # Calendar Integration (Cal.com)
    CAL_COM_API_KEY: str = ""
    CAL_COM_EVENT_TYPE_ID: str = ""
    CAL_COM_USERNAME: str = ""
    
    # CRM Integration (HubSpot)
    HUBSPOT_API_KEY: str = ""
    HUBSPOT_ACCESS_TOKEN: str = ""
    HUBSPOT_CLIENT_SECRET: str = ""
    HUBSPOT_PORTAL_ID: str = ""
    
    # External Data Enrichment (Optional)
    CLEARBIT_API_KEY: str = ""
    HUNTER_API_KEY: str = ""
    
    # Gmail API Integration
    GMAIL_CREDENTIALS_FILE: str = "credentials.json"  # OAuth2 credentials from Google Cloud Console
    GMAIL_TOKEN_FILE: str = "token.json"  # Generated after first authentication
    GMAIL_LABEL_FILTER: str = "INBOX"  # Which label/folder to check
    GMAIL_SEARCH_QUERY: str = "is:unread subject:(inquiry OR quote OR sales OR demo OR contact)"  # Filter emails
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/api/gmail/oauth2callback"  # OAuth callback for web apps
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Lead Scoring Thresholds
    SCORE_THRESHOLD_HIGH: int = 75  # Sales-ready leads
    SCORE_THRESHOLD_MEDIUM: int = 50  # Nurture/qualify leads
    SCORE_THRESHOLD_LOW: int = 50  # Disqualified leads
    
    # ICP (Ideal Customer Profile) Criteria
    ICP_MIN_COMPANY_SIZE: int = 10
    ICP_MAX_COMPANY_SIZE: int = 5000
    ICP_TARGET_INDUSTRIES: List[str] = [
        "Technology",
        "SaaS",
        "Software",
        "IT Services",
        "Financial Services",
        "Healthcare",
        "E-commerce"
    ]
    ICP_TARGET_ROLES: List[str] = [
        "CEO",
        "CTO",
        "VP",
        "Director",
        "Head of",
        "Manager"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
