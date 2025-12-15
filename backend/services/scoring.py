"""
AI-powered lead scoring service using OpenAI GPT models.
"""
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from config import settings
import json
import logging

logger = logging.getLogger(__name__)


class ScoringService:
    """Service for AI-powered lead scoring and classification."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def calculate_icp_fit_score(self, lead_data: Dict[str, Any]) -> float:
        """
        Calculate Ideal Customer Profile (ICP) fit score.
        
        Args:
            lead_data: Lead information including company data
            
        Returns:
            ICP fit score (0-100)
        """
        score = 0.0
        max_score = 100.0
        
        # Company size scoring (30 points)
        company_size = lead_data.get("company_size", 0)
        if settings.ICP_MIN_COMPANY_SIZE <= company_size <= settings.ICP_MAX_COMPANY_SIZE:
            score += 30
        elif company_size > 0:
            # Partial credit for companies outside ideal range
            score += 15
        
        # Industry scoring (30 points)
        company_industry = lead_data.get("company_industry", "")
        if any(target.lower() in company_industry.lower() 
               for target in settings.ICP_TARGET_INDUSTRIES):
            score += 30
        
        # Job title/role scoring (25 points)
        job_title = lead_data.get("job_title", "")
        if any(role.lower() in job_title.lower() 
               for role in settings.ICP_TARGET_ROLES):
            score += 25
        
        # Company domain scoring (15 points) - having a business email
        if lead_data.get("company_domain"):
            score += 15
        
        return min(score, max_score)
    
    def calculate_engagement_score(self, lead_data: Dict[str, Any]) -> float:
        """
        Calculate engagement score based on lead interactions.
        
        Args:
            lead_data: Lead information including interaction history
            
        Returns:
            Engagement score (0-100)
        """
        score = 0.0
        
        # Has provided complete information (40 points)
        required_fields = ["first_name", "last_name", "company_name", "job_title"]
        filled_fields = sum(1 for field in required_fields if lead_data.get(field))
        score += (filled_fields / len(required_fields)) * 40
        
        # Has phone number (20 points)
        if lead_data.get("phone"):
            score += 20
        
        # Source quality (20 points)
        source = lead_data.get("source", "")
        source_scores = {
            "website_form": 20,
            "crm_webhook": 15,
            "email": 10,
            "chat": 15,
            "api": 10,
            "manual": 5
        }
        score += source_scores.get(source, 0)
        
        # Provided additional notes/context (20 points)
        if lead_data.get("notes") and len(lead_data.get("notes", "")) > 20:
            score += 20
        
        return min(score, 100.0)
    
    async def calculate_intent_score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate buying intent score using AI analysis.
        
        Args:
            lead_data: Complete lead information
            
        Returns:
            Dictionary with intent score and analysis
        """
        try:
            # Prepare context for AI
            context = self._prepare_lead_context(lead_data)
            
            prompt = f"""
Analyze this lead's buying intent based on the following information:

{context}

Evaluate the lead's buying intent on a scale of 0-100, where:
- 0-30: Low intent (just browsing, no clear need)
- 31-60: Medium intent (exploring options, has a need)
- 61-100: High intent (actively looking to buy, urgent need)

Provide your analysis in the following JSON format:
{{
    "intent_score": <score 0-100>,
    "intent_level": "<low|medium|high>",
    "buying_signals": ["signal1", "signal2", ...],
    "concerns": ["concern1", "concern2", ...],
    "reasoning": "<detailed explanation>"
}}
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert sales analyst specializing in lead qualification."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error calculating intent score: {e}")
            return {
                "intent_score": 50,
                "intent_level": "medium",
                "buying_signals": [],
                "concerns": [],
                "reasoning": "Unable to analyze intent due to error"
            }
    
    async def classify_sales_stage(self, lead_data: Dict[str, Any]) -> str:
        """
        Classify the lead's sales stage using AI.
        
        Args:
            lead_data: Complete lead information
            
        Returns:
            Sales stage classification
        """
        try:
            context = self._prepare_lead_context(lead_data)
            
            prompt = f"""
Based on this lead information, classify them into one of these sales stages:

{context}

Sales stages:
1. Awareness - Just learning about solutions
2. Consideration - Actively evaluating options
3. Decision - Ready to make a purchase decision
4. Nurture - Not ready yet, needs more time

Return only the stage name.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sales stage classifier."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=50
            )
            
            stage = response.choices[0].message.content.strip()
            return stage
            
        except Exception as e:
            logger.error(f"Error classifying sales stage: {e}")
            return "Consideration"
    
    async def score_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive lead scoring using multiple factors.
        
        Args:
            lead_data: Complete lead information
            
        Returns:
            Complete scoring results
        """
        # Calculate component scores
        icp_fit_score = self.calculate_icp_fit_score(lead_data)
        engagement_score = self.calculate_engagement_score(lead_data)
        
        # Calculate AI-powered intent score
        intent_analysis = await self.calculate_intent_score(lead_data)
        intent_score = intent_analysis.get("intent_score", 50)
        
        # Classify sales stage
        sales_stage = await self.classify_sales_stage(lead_data)
        
        # Calculate overall lead score (weighted average)
        lead_score = (
            icp_fit_score * 0.35 +       # 35% weight on ICP fit
            intent_score * 0.40 +         # 40% weight on intent
            engagement_score * 0.25       # 25% weight on engagement
        )
        
        # Determine recommended action
        recommended_action = self._determine_action(
            lead_score,
            icp_fit_score,
            intent_score,
            engagement_score
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            lead_score,
            icp_fit_score,
            intent_score,
            engagement_score,
            intent_analysis,
            sales_stage
        )
        
        return {
            "lead_score": round(lead_score, 2),
            "icp_fit_score": round(icp_fit_score, 2),
            "intent_score": round(intent_score, 2),
            "engagement_score": round(engagement_score, 2),
            "buying_intent": intent_analysis.get("intent_level", "medium"),
            "sales_stage": sales_stage,
            "recommended_action": recommended_action,
            "reasoning": reasoning,
            "buying_signals": intent_analysis.get("buying_signals", []),
            "concerns": intent_analysis.get("concerns", [])
        }
    
    def _prepare_lead_context(self, lead_data: Dict[str, Any]) -> str:
        """Prepare lead context for AI analysis."""
        context_parts = []
        
        if lead_data.get("first_name") and lead_data.get("last_name"):
            context_parts.append(f"Name: {lead_data['first_name']} {lead_data['last_name']}")
        
        if lead_data.get("job_title"):
            context_parts.append(f"Job Title: {lead_data['job_title']}")
        
        if lead_data.get("company_name"):
            context_parts.append(f"Company: {lead_data['company_name']}")
        
        if lead_data.get("company_size"):
            context_parts.append(f"Company Size: {lead_data['company_size']} employees")
        
        if lead_data.get("company_industry"):
            context_parts.append(f"Industry: {lead_data['company_industry']}")
        
        if lead_data.get("notes"):
            context_parts.append(f"Notes: {lead_data['notes']}")
        
        if lead_data.get("source"):
            context_parts.append(f"Source: {lead_data['source']}")
        
        return "\n".join(context_parts) if context_parts else "Limited information available"
    
    def _determine_action(
        self,
        lead_score: float,
        icp_fit: float,
        intent: float,
        engagement: float
    ) -> str:
        """Determine recommended action based on scores."""
        if lead_score >= settings.SCORE_THRESHOLD_HIGH:
            if intent >= 70:
                return "schedule_demo"
            else:
                return "contact_sales"
        elif lead_score >= settings.SCORE_THRESHOLD_MEDIUM:
            if icp_fit >= 60:
                return "qualify_further"
            else:
                return "nurture"
        else:
            return "add_to_nurture"
    
    def _generate_reasoning(
        self,
        lead_score: float,
        icp_fit: float,
        intent: float,
        engagement: float,
        intent_analysis: Dict[str, Any],
        sales_stage: str
    ) -> str:
        """Generate human-readable reasoning for the score."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Overall Lead Score: {lead_score:.1f}/100")
        reasoning_parts.append(f"- ICP Fit: {icp_fit:.1f}/100")
        reasoning_parts.append(f"- Intent: {intent:.1f}/100")
        reasoning_parts.append(f"- Engagement: {engagement:.1f}/100")
        reasoning_parts.append(f"\nSales Stage: {sales_stage}")
        
        if intent_analysis.get("buying_signals"):
            signals = ", ".join(intent_analysis["buying_signals"])
            reasoning_parts.append(f"\nBuying Signals: {signals}")
        
        if intent_analysis.get("concerns"):
            concerns = ", ".join(intent_analysis["concerns"])
            reasoning_parts.append(f"\nConcerns: {concerns}")
        
        if intent_analysis.get("reasoning"):
            reasoning_parts.append(f"\n{intent_analysis['reasoning']}")
        
        return "\n".join(reasoning_parts)


# Global scoring service instance
scoring_service = ScoringService()
