"""
Lead enrichment service.
Enriches lead data using external APIs and public data sources.
"""
import re
import httpx
from typing import Optional, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class EnrichmentService:
    """Service for enriching lead data with company information."""
    
    def __init__(self):
        self.timeout = 10.0
        
    def extract_domain_from_email(self, email: str) -> Optional[str]:
        """
        Extract company domain from email address.
        
        Args:
            email: Email address
            
        Returns:
            Company domain or None
        """
        try:
            # Extract domain from email
            domain = email.split('@')[1].lower()
            
            # Filter out common free email providers
            free_providers = [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'
            ]
            
            if domain in free_providers:
                logger.info(f"Email {email} is from free provider: {domain}")
                return None
                
            return domain
        except Exception as e:
            logger.error(f"Error extracting domain from email {email}: {e}")
            return None
    
    async def enrich_company_data(self, domain: str) -> Dict[str, Any]:
        """
        Enrich company data using domain.
        Uses multiple data sources to gather company information.
        
        Args:
            domain: Company domain
            
        Returns:
            Enrichment data dictionary
        """
        enrichment_data = {
            'domain': domain,
            'company_name': None,
            'company_size': None,
            'company_industry': None,
            'company_location': None,
            'company_description': None,
            'company_founded': None,
            'company_revenue': None,
            'company_linkedin': None,
            'company_twitter': None,
            'technologies': []
        }
        
        try:
            # Try Clearbit if API key is available
            if settings.CLEARBIT_API_KEY:
                clearbit_data = await self._enrich_with_clearbit(domain)
                if clearbit_data:
                    enrichment_data.update(clearbit_data)
                    return enrichment_data
            
            # Fallback to free data sources
            free_data = await self._enrich_with_free_sources(domain)
            if free_data:
                enrichment_data.update(free_data)
                
        except Exception as e:
            logger.error(f"Error enriching company data for {domain}: {e}")
        
        return enrichment_data
    
    async def _enrich_with_clearbit(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Enrich using Clearbit API.
        
        Args:
            domain: Company domain
            
        Returns:
            Enrichment data or None
        """
        try:
            url = f"https://company.clearbit.com/v2/companies/find?domain={domain}"
            headers = {
                "Authorization": f"Bearer {settings.CLEARBIT_API_KEY}"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'company_name': data.get('name'),
                        'company_size': data.get('metrics', {}).get('employees'),
                        'company_industry': data.get('category', {}).get('industry'),
                        'company_location': data.get('location'),
                        'company_description': data.get('description'),
                        'company_founded': data.get('foundedYear'),
                        'company_linkedin': data.get('linkedin', {}).get('handle'),
                        'company_twitter': data.get('twitter', {}).get('handle'),
                        'technologies': data.get('tech', [])
                    }
        except Exception as e:
            logger.error(f"Clearbit enrichment error for {domain}: {e}")
        
        return None
    
    async def _enrich_with_free_sources(self, domain: str) -> Dict[str, Any]:
        """
        Enrich using free data sources and web scraping.
        
        Args:
            domain: Company domain
            
        Returns:
            Enrichment data
        """
        data = {}
        
        try:
            # Try to get basic company info from website
            website_data = await self._scrape_website_metadata(domain)
            if website_data:
                data.update(website_data)
            
            # Estimate company size based on domain patterns
            estimated_size = self._estimate_company_size(domain)
            if estimated_size:
                data['company_size'] = estimated_size
                
        except Exception as e:
            logger.error(f"Free source enrichment error for {domain}: {e}")
        
        return data
    
    async def _scrape_website_metadata(self, domain: str) -> Dict[str, Any]:
        """
        Scrape basic metadata from company website.
        
        Args:
            domain: Company domain
            
        Returns:
            Website metadata
        """
        try:
            url = f"https://{domain}"
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    html = response.text
                    
                    # Extract company name from title tag
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
                    company_name = title_match.group(1) if title_match else None
                    
                    # Extract description from meta tag
                    desc_match = re.search(
                        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
                        html,
                        re.IGNORECASE
                    )
                    description = desc_match.group(1) if desc_match else None
                    
                    return {
                        'company_name': company_name,
                        'company_description': description
                    }
        except Exception as e:
            logger.debug(f"Website scraping error for {domain}: {e}")
        
        return {}
    
    def _estimate_company_size(self, domain: str) -> Optional[int]:
        """
        Estimate company size based on domain patterns.
        This is a basic heuristic - in production, use proper data sources.
        
        Args:
            domain: Company domain
            
        Returns:
            Estimated company size
        """
        # Common patterns for enterprise companies
        enterprise_indicators = ['.com', '.io', '.co']
        
        # This is a simplified estimation - enhance with real data
        if any(domain.endswith(indicator) for indicator in enterprise_indicators):
            # Return a reasonable mid-range estimate
            return 100
        
        return 50
    
    async def detect_technologies(self, domain: str) -> list:
        """
        Detect technologies used by company.
        
        Args:
            domain: Company domain
            
        Returns:
            List of detected technologies
        """
        technologies = []
        
        try:
            # In a production system, you would use services like:
            # - BuiltWith API
            # - Wappalyzer
            # - Datanyze
            
            # For this MVP, we'll do basic detection
            url = f"https://{domain}"
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    html = response.text.lower()
                    
                    # Detect common technologies
                    tech_patterns = {
                        'React': ['react', 'react-dom'],
                        'Vue.js': ['vue.js', 'vuejs'],
                        'Angular': ['angular', 'ng-'],
                        'WordPress': ['wp-content', 'wordpress'],
                        'Shopify': ['shopify', 'cdn.shopify'],
                        'Google Analytics': ['google-analytics', 'gtag'],
                        'HubSpot': ['hubspot', 'hs-analytics'],
                        'Salesforce': ['salesforce', 'force.com']
                    }
                    
                    for tech, patterns in tech_patterns.items():
                        if any(pattern in html for pattern in patterns):
                            technologies.append(tech)
                            
        except Exception as e:
            logger.debug(f"Technology detection error for {domain}: {e}")
        
        return technologies
    
    async def enrich_lead(self, email: str, company_domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete lead enrichment process.
        
        Args:
            email: Lead email address
            company_domain: Optional company domain (will be extracted if not provided)
            
        Returns:
            Complete enrichment data
        """
        # Extract domain if not provided
        if not company_domain:
            company_domain = self.extract_domain_from_email(email)
        
        if not company_domain:
            logger.warning(f"Could not extract domain from email: {email}")
            return {}
        
        # Enrich company data
        enrichment_data = await self.enrich_company_data(company_domain)
        
        # Detect technologies
        technologies = await self.detect_technologies(company_domain)
        if technologies:
            enrichment_data['technologies'] = technologies
        
        logger.info(f"Successfully enriched lead: {email}")
        return enrichment_data


# Global enrichment service instance
enrichment_service = EnrichmentService()
