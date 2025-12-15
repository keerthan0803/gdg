"""
Autonomous AI Agent for lead qualification and action.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from config import settings
from models import Lead, AgentAction, Conversation, LeadStatus, AgentActionType
from services.enrichment import enrichment_service
from services.scoring import scoring_service
from services.communication import communication_service
from services.crm import crm_service
from services.calendar import calendar_service
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class AIAgent:
    """
    Autonomous AI Agent for lead qualification.
    
    This agent:
    - Analyzes leads
    - Makes decisions
    - Takes actions automatically
    - Asks clarifying questions when needed
    - Tracks all actions for auditability
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def process_lead(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """
        Process a lead through the complete qualification pipeline.
        
        Args:
            lead: Lead database object
            db: Database session
            
        Returns:
            Processing results dictionary
        """
        results = {
            "lead_id": lead.id,
            "actions_taken": [],
            "status": "processing"
        }
        
        try:
            # Step 1: Enrich lead data
            if not lead.enrichment_data or lead.status == LeadStatus.NEW:
                enrichment_result = await self._enrich_lead(lead, db)
                results["actions_taken"].append(enrichment_result)
            
            # Step 2: Score the lead
            if lead.lead_score == 0 or lead.status in [LeadStatus.NEW, LeadStatus.ENRICHING]:
                scoring_result = await self._score_lead(lead, db)
                results["actions_taken"].append(scoring_result)
            
            # Step 3: Make decision and take action
            decision_result = await self._make_decision(lead, db)
            results["actions_taken"].extend(decision_result["actions"])
            
            results["status"] = "completed"
            results["final_lead_score"] = lead.lead_score
            results["recommended_action"] = lead.recommended_action
            
        except Exception as e:
            logger.error(f"Error processing lead {lead.id}: {e}")
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def _enrich_lead(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Enrich lead with external data."""
        action = AgentAction(
            lead_id=lead.id,
            action_type=AgentActionType.ENRICH,
            action_description="Enriching lead with company data",
            status="processing"
        )
        db.add(action)
        db.commit()
        
        try:
            # Update lead status
            lead.status = LeadStatus.ENRICHING
            db.commit()
            
            # Extract domain and enrich
            domain = enrichment_service.extract_domain_from_email(lead.email)
            if domain:
                lead.company_domain = domain
            
            # Enrich company data
            enrichment_data = await enrichment_service.enrich_lead(
                lead.email,
                domain
            )
            
            # Update lead with enrichment data
            if enrichment_data:
                lead.enrichment_data = enrichment_data
                
                if enrichment_data.get("company_name"):
                    lead.company_name = enrichment_data["company_name"]
                if enrichment_data.get("company_size"):
                    lead.company_size = enrichment_data["company_size"]
                if enrichment_data.get("company_industry"):
                    lead.company_industry = enrichment_data["company_industry"]
                if enrichment_data.get("company_location"):
                    lead.company_location = enrichment_data["company_location"]
                if enrichment_data.get("technologies"):
                    lead.technographic_data = {"technologies": enrichment_data["technologies"]}
            
            # Mark action as completed
            action.status = "completed"
            action.action_output = enrichment_data
            action.completed_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "action": "enrich",
                "status": "success",
                "data": enrichment_data
            }
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            db.commit()
            raise
    
    async def _score_lead(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Score the lead using AI."""
        action = AgentAction(
            lead_id=lead.id,
            action_type=AgentActionType.SCORE,
            action_description="Scoring lead with AI",
            status="processing"
        )
        db.add(action)
        db.commit()
        
        try:
            # Update lead status
            lead.status = LeadStatus.SCORING
            db.commit()
            
            # Prepare lead data for scoring
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
                "notes": lead.notes,
                "enrichment_data": lead.enrichment_data
            }
            
            # Score the lead
            scoring_results = await scoring_service.score_lead(lead_data)
            
            # Update lead with scores
            lead.lead_score = scoring_results["lead_score"]
            lead.icp_fit_score = scoring_results["icp_fit_score"]
            lead.intent_score = scoring_results["intent_score"]
            lead.engagement_score = scoring_results["engagement_score"]
            lead.buying_intent = scoring_results["buying_intent"]
            lead.sales_stage = scoring_results["sales_stage"]
            lead.recommended_action = scoring_results["recommended_action"]
            lead.ai_reasoning = scoring_results["reasoning"]
            
            # Update status based on score
            if lead.lead_score >= settings.SCORE_THRESHOLD_HIGH:
                lead.status = LeadStatus.QUALIFIED
            elif lead.lead_score >= settings.SCORE_THRESHOLD_MEDIUM:
                lead.status = LeadStatus.NURTURE
            else:
                lead.status = LeadStatus.DISQUALIFIED
            
            # Mark action as completed
            action.status = "completed"
            action.action_output = scoring_results
            action.completed_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "action": "score",
                "status": "success",
                "score": scoring_results["lead_score"]
            }
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            db.commit()
            raise
    
    async def _make_decision(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """
        Make decision on what actions to take with the lead.
        """
        actions_taken = []
        
        try:
            # High-quality lead actions
            if lead.lead_score >= settings.SCORE_THRESHOLD_HIGH:
                # Sync to CRM
                crm_result = await self._sync_to_crm(lead, db)
                actions_taken.append(crm_result)
                
                # Schedule demo
                demo_result = await self._schedule_demo(lead, db)
                actions_taken.append(demo_result)
                
                # Notify sales team
                notify_result = await self._notify_sales(lead, db)
                actions_taken.append(notify_result)
                
                lead.status = LeadStatus.QUALIFIED
                
            # Medium-quality lead actions
            elif lead.lead_score >= settings.SCORE_THRESHOLD_MEDIUM:
                # Ask qualifying questions if needed
                if not lead.qualification_responses:
                    questions_result = await self._ask_qualifying_questions(lead, db)
                    actions_taken.append(questions_result)
                else:
                    # Sync to CRM for nurturing
                    crm_result = await self._sync_to_crm(lead, db)
                    actions_taken.append(crm_result)
                
                lead.status = LeadStatus.NURTURE
                
            # Low-quality lead actions
            else:
                # Add to nurture workflow
                nurture_result = await self._add_to_nurture(lead, db)
                actions_taken.append(nurture_result)
                
                lead.status = LeadStatus.DISQUALIFIED
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error making decision for lead {lead.id}: {e}")
        
        return {"actions": actions_taken}
    
    async def _sync_to_crm(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Sync lead to CRM."""
        action = AgentAction(
            lead_id=lead.id,
            action_type=AgentActionType.SYNC_CRM,
            action_description="Syncing lead to CRM",
            status="processing"
        )
        db.add(action)
        db.commit()
        
        try:
            lead_data = {
                "email": lead.email,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "phone": lead.phone,
                "job_title": lead.job_title,
                "company_name": lead.company_name,
                "status": lead.status.value if lead.status else None,
                "lead_score": lead.lead_score,
                "crm_id": lead.crm_id
            }
            
            result = await crm_service.sync_lead_to_crm(lead_data)
            
            if result["success"] and result.get("crm_id"):
                lead.crm_id = result["crm_id"]
                lead.crm_synced_at = datetime.utcnow()
            
            action.status = "completed"
            action.action_output = result
            action.completed_at = datetime.utcnow()
            db.commit()
            
            return {"action": "sync_crm", "status": "success"}
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            db.commit()
            return {"action": "sync_crm", "status": "failed", "error": str(e)}
    
    async def _schedule_demo(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Schedule a demo for the lead."""
        action = AgentAction(
            lead_id=lead.id,
            action_type=AgentActionType.SCHEDULE_DEMO,
            action_description="Scheduling demo",
            status="processing"
        )
        db.add(action)
        db.commit()
        
        try:
            lead_name = f"{lead.first_name or ''} {lead.last_name or ''}".strip() or "Prospect"
            
            result = await calendar_service.schedule_meeting(
                lead.email,
                lead_name
            )
            
            if result["success"]:
                # Send demo email with scheduling link
                await communication_service.send_email(
                    lead.email,
                    "Let's schedule your demo!",
                    f"Hi {lead.first_name or 'there'},\n\n"
                    f"Thank you for your interest! Based on your profile, "
                    f"I'd like to schedule a personalized demo.\n\n"
                    f"Please use this link to choose a time: {result['scheduling_link']}\n\n"
                    f"Looking forward to speaking with you!\n\n"
                    f"Best regards,\nSales Team"
                )
                
                lead.status = LeadStatus.SCHEDULED
            
            action.status = "completed"
            action.action_output = result
            action.completed_at = datetime.utcnow()
            db.commit()
            
            return {"action": "schedule_demo", "status": "success"}
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            db.commit()
            return {"action": "schedule_demo", "status": "failed", "error": str(e)}
    
    async def _notify_sales(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Notify sales team about qualified lead."""
        action = AgentAction(
            lead_id=lead.id,
            action_type=AgentActionType.NOTIFY_SALES,
            action_description="Notifying sales team",
            status="processing"
        )
        db.add(action)
        db.commit()
        
        try:
            lead_name = f"{lead.first_name or ''} {lead.last_name or ''}".strip() or lead.email
            
            await communication_service.notify_sales_team(
                lead.email,
                lead_name,
                lead.lead_score,
                lead.ai_reasoning or "High-quality lead"
            )
            
            action.status = "completed"
            action.completed_at = datetime.utcnow()
            db.commit()
            
            return {"action": "notify_sales", "status": "success"}
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            db.commit()
            return {"action": "notify_sales", "status": "failed", "error": str(e)}
    
    async def _ask_qualifying_questions(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Generate and send qualifying questions."""
        action = AgentAction(
            lead_id=lead.id,
            action_type=AgentActionType.ASK_QUESTION,
            action_description="Asking qualifying questions",
            status="processing"
        )
        db.add(action)
        db.commit()
        
        try:
            # Generate relevant questions based on lead data
            questions = await self._generate_questions(lead)
            
            # Store questions
            lead.qualification_questions = {"questions": questions}
            
            # Send questions via email
            await communication_service.send_qualification_email(
                lead.email,
                lead.first_name,
                questions
            )
            
            lead.status = LeadStatus.CONTACTED
            lead.last_contacted_at = datetime.utcnow()
            
            action.status = "completed"
            action.action_output = {"questions": questions}
            action.completed_at = datetime.utcnow()
            db.commit()
            
            return {"action": "ask_questions", "status": "success"}
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            db.commit()
            return {"action": "ask_questions", "status": "failed", "error": str(e)}
    
    async def _add_to_nurture(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Add lead to nurture workflow."""
        action = AgentAction(
            lead_id=lead.id,
            action_type=AgentActionType.ADD_TO_NURTURE,
            action_description="Adding to nurture workflow",
            status="processing"
        )
        db.add(action)
        db.commit()
        
        try:
            # In a production system, this would:
            # - Add to email drip campaign
            # - Tag in CRM for nurturing
            # - Set follow-up reminders
            
            lead.status = LeadStatus.NURTURE
            
            action.status = "completed"
            action.completed_at = datetime.utcnow()
            db.commit()
            
            return {"action": "add_to_nurture", "status": "success"}
            
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            db.commit()
            return {"action": "add_to_nurture", "status": "failed", "error": str(e)}
    
    async def _generate_questions(self, lead: Lead) -> List[str]:
        """Generate relevant qualifying questions for a lead."""
        try:
            context = f"""
Lead Information:
- Name: {lead.first_name} {lead.last_name}
- Company: {lead.company_name or 'Unknown'}
- Job Title: {lead.job_title or 'Unknown'}
- Industry: {lead.company_industry or 'Unknown'}
- Score: {lead.lead_score}/100
"""
            
            prompt = f"""
Based on this lead's profile, generate 3-4 relevant qualifying questions 
to better understand their needs and buying intent.

{context}

Questions should:
1. Be specific to their industry/role
2. Uncover budget and timeline
3. Identify decision-making authority
4. Understand their current challenges

Return only the questions as a JSON array.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sales qualification expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            questions = result.get("questions", [
                "What challenges are you currently facing?",
                "What's your timeline for implementing a solution?",
                "Who else is involved in the decision-making process?"
            ])
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return [
                "What specific challenges are you looking to solve?",
                "When do you need a solution in place?",
                "What's your budget range for this project?"
            ]


# Global agent instance
ai_agent = AIAgent()
