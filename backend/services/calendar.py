"""
Calendar integration service for scheduling demos via Calendly.
"""
from typing import Optional, Dict, Any
import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)


class CalendarService:
    """Service for scheduling meetings via Calendly."""
    
    def __init__(self):
        self.base_url = "https://api.calendly.com"
        self.timeout = 10.0
    
    async def create_scheduling_link(
        self,
        lead_email: str,
        lead_name: str
    ) -> Optional[str]:
        """
        Create a personalized Cal.com scheduling link for a lead.
        
        Args:
            lead_email: Lead email address
            lead_name: Lead name
            
        Returns:
            Cal.com scheduling link or None
        """
        if not settings.CAL_COM_API_KEY or not settings.CAL_COM_USERNAME:
            logger.warning("Cal.com not configured")
            # Return a generic link if API is not configured
            username = settings.CAL_COM_USERNAME or "your-username"
            event_type = settings.CAL_COM_EVENT_TYPE_ID or "demo"
            return f"https://cal.com/{username}/{event_type}"
        
        try:
            # Build Cal.com booking link with pre-filled parameters
            username = settings.CAL_COM_USERNAME
            event_type = settings.CAL_COM_EVENT_TYPE_ID or "demo"
            
            # Cal.com supports query parameters for pre-filling
            # Format: https://cal.com/username/event?name=Name&email=email@example.com
            base_link = f"https://cal.com/{username}/{event_type}"
            prefill_params = f"?name={lead_name}&email={lead_email}"
            
            scheduling_link = base_link + prefill_params
            
            logger.info(f"Generated Cal.com scheduling link for {lead_email}")
            return scheduling_link
            
        except Exception as e:
            logger.error(f"Error creating scheduling link: {e}")
        
        return None
    
    async def schedule_meeting(
        self,
        lead_email: str,
        lead_name: str,
        preferred_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a meeting for a lead.
        
        Args:
            lead_email: Lead email address
            lead_name: Lead name
            preferred_time: Preferred meeting time (optional)
            
        Returns:
            Result dictionary with meeting details
        """
        scheduling_link = await self.create_scheduling_link(lead_email, lead_name)
        
        if scheduling_link:
            return {
                "success": True,
                "scheduling_link": scheduling_link,
                "message": "Scheduling link created successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to create scheduling link"
            }
    
    async def get_scheduled_events(self, lead_email: str) -> list:
        """
        Get scheduled events for a lead.
        
        Args:
            lead_email: Lead email address
            
        Returns:
            List of scheduled events
        """
        if not settings.CAL_COM_API_KEY:
            logger.warning("Cal.com API key not configured")
            return []
        
        try:
            url = f"{self.base_url}/bookings"
            
            headers = {
                "Authorization": f"Bearer {settings.CAL_COM_API_KEY}",
                "Content-Type": "application/json"
            }
            
            params = {
                "attendeeEmail": lead_email
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("bookings", [])
                else:
                    logger.error(f"Cal.com API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error fetching scheduled events: {e}")
        
        return []


# Global calendar service instance
calendar_service = CalendarService()
