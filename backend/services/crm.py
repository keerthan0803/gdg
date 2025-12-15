"""
CRM integration service for syncing with HubSpot.
"""
from typing import Optional, Dict, Any
import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)


class CRMService:
    """Service for integrating with HubSpot CRM."""
    
    def __init__(self):
        self.base_url = "https://api.hubapi.com"
        self.timeout = 10.0
        
    async def create_contact(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a contact in HubSpot CRM.
        
        Args:
            lead_data: Lead information dictionary
            
        Returns:
            HubSpot contact ID or None
        """
        if not settings.HUBSPOT_API_KEY:
            logger.warning("HubSpot API key not configured")
            return None
        
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts"
            
            headers = {
                "Authorization": f"Bearer {settings.HUBSPOT_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Map lead data to HubSpot properties
            properties = {
                "email": lead_data.get("email"),
                "firstname": lead_data.get("first_name"),
                "lastname": lead_data.get("last_name"),
                "phone": lead_data.get("phone"),
                "jobtitle": lead_data.get("job_title"),
                "company": lead_data.get("company_name"),
                "hs_lead_status": self._map_status_to_hubspot(lead_data.get("status")),
            }
            
            # Add custom properties for scoring
            if lead_data.get("lead_score"):
                properties["lead_score"] = lead_data["lead_score"]
            
            payload = {"properties": properties}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    contact_id = data.get("id")
                    logger.info(f"Created HubSpot contact: {contact_id}")
                    return contact_id
                else:
                    logger.error(f"HubSpot API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error creating HubSpot contact: {e}")
        
        return None
    
    async def update_contact(self, contact_id: str, lead_data: Dict[str, Any]) -> bool:
        """
        Update a contact in HubSpot CRM.
        
        Args:
            contact_id: HubSpot contact ID
            lead_data: Updated lead information
            
        Returns:
            True if successful, False otherwise
        """
        if not settings.HUBSPOT_API_KEY:
            logger.warning("HubSpot API key not configured")
            return False
        
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
            
            headers = {
                "Authorization": f"Bearer {settings.HUBSPOT_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Map lead data to HubSpot properties
            properties = {}
            
            if lead_data.get("first_name"):
                properties["firstname"] = lead_data["first_name"]
            if lead_data.get("last_name"):
                properties["lastname"] = lead_data["last_name"]
            if lead_data.get("phone"):
                properties["phone"] = lead_data["phone"]
            if lead_data.get("job_title"):
                properties["jobtitle"] = lead_data["job_title"]
            if lead_data.get("company_name"):
                properties["company"] = lead_data["company_name"]
            if lead_data.get("status"):
                properties["hs_lead_status"] = self._map_status_to_hubspot(lead_data["status"])
            if lead_data.get("lead_score"):
                properties["lead_score"] = lead_data["lead_score"]
            
            payload = {"properties": properties}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"Updated HubSpot contact: {contact_id}")
                    return True
                else:
                    logger.error(f"HubSpot API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error updating HubSpot contact: {e}")
        
        return False
    
    async def create_deal(
        self,
        contact_id: str,
        deal_name: str,
        amount: Optional[float] = None
    ) -> Optional[str]:
        """
        Create a deal in HubSpot CRM.
        
        Args:
            contact_id: HubSpot contact ID
            deal_name: Deal name
            amount: Deal amount (optional)
            
        Returns:
            HubSpot deal ID or None
        """
        if not settings.HUBSPOT_API_KEY:
            logger.warning("HubSpot API key not configured")
            return None
        
        try:
            url = f"{self.base_url}/crm/v3/objects/deals"
            
            headers = {
                "Authorization": f"Bearer {settings.HUBSPOT_API_KEY}",
                "Content-Type": "application/json"
            }
            
            properties = {
                "dealname": deal_name,
                "dealstage": "appointmentscheduled",
                "pipeline": "default"
            }
            
            if amount:
                properties["amount"] = amount
            
            payload = {
                "properties": properties,
                "associations": [
                    {
                        "to": {"id": contact_id},
                        "types": [
                            {
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 3  # Deal to Contact
                            }
                        ]
                    }
                ]
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    deal_id = data.get("id")
                    logger.info(f"Created HubSpot deal: {deal_id}")
                    return deal_id
                else:
                    logger.error(f"HubSpot API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error creating HubSpot deal: {e}")
        
        return None
    
    def _map_status_to_hubspot(self, status: Optional[str]) -> str:
        """
        Map internal lead status to HubSpot lead status.
        
        Args:
            status: Internal lead status
            
        Returns:
            HubSpot lead status
        """
        status_mapping = {
            "new": "NEW",
            "qualified": "OPEN",
            "nurture": "IN_PROGRESS",
            "contacted": "OPEN",
            "scheduled": "APPOINTMENT_SCHEDULED",
            "converted": "CONNECTED",
            "disqualified": "UNQUALIFIED"
        }
        
        return status_mapping.get(status, "NEW")
    
    async def sync_lead_to_crm(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync lead to CRM (create or update).
        
        Args:
            lead_data: Complete lead information
            
        Returns:
            Result dictionary with CRM ID and status
        """
        crm_id = lead_data.get("crm_id")
        
        if crm_id:
            # Update existing contact
            success = await self.update_contact(crm_id, lead_data)
            return {
                "success": success,
                "crm_id": crm_id,
                "action": "update"
            }
        else:
            # Create new contact
            crm_id = await self.create_contact(lead_data)
            return {
                "success": crm_id is not None,
                "crm_id": crm_id,
                "action": "create"
            }


# Global CRM service instance
crm_service = CRMService()
