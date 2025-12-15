"""
Communication service for sending emails, SMS, and WhatsApp messages.
"""
from typing import Optional, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# Twilio disabled - using SendGrid only
# from twilio.rest import Client
from config import settings
import logging

logger = logging.getLogger(__name__)


class CommunicationService:
    """Service for sending communications via email, SMS, and WhatsApp."""
    
    def __init__(self):
        # Initialize SendGrid
        if settings.SENDGRID_API_KEY:
            self.sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        else:
            self.sendgrid_client = None
            logger.warning("SendGrid API key not configured")
        
        # Twilio disabled - using SendGrid only for all communications
        self.twilio_client = None
        logger.info("Using SendGrid for all communications (Twilio disabled)")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email using SendGrid.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional)
            
        Returns:
            Result dictionary with status and message
        """
        if not self.sendgrid_client:
            logger.error("Cannot send email: SendGrid not configured")
            return {"success": False, "error": "SendGrid not configured"}
        
        try:
            message = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body,
                html_content=html_body or body
            )
            
            response = self.sendgrid_client.send(message)
            
            logger.info(f"Email sent to {to_email}: {response.status_code}")
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Send SMS using Twilio (DISABLED - using email only).
        
        Args:
            to_phone: Recipient phone number (E.164 format)
            message: SMS message content
            
        Returns:
            Result dictionary with status and message
        """
        logger.info(f"SMS sending disabled. Twilio not configured. Message for {to_phone}: {message}")
        return {"success": False, "error": "SMS disabled - using email only"}
        
        try:
            result = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_SMS_NUMBER,
                to=to_phone
            )
            
            logger.info(f"SMS sent to {to_phone}: {result.sid}")
            return {
                "success": True,
                "message_sid": result.sid,
                "message": "SMS sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS to {to_phone}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_whatsapp(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Send WhatsApp message using Twilio (DISABLED - using email only).
        
        Args:
            to_phone: Recipient phone number (E.164 format with whatsapp: prefix)
            message: WhatsApp message content
            
        Returns:
            Result dictionary with status and message
        """
        logger.info(f"WhatsApp sending disabled. Twilio not configured. Message for {to_phone}: {message}")
        return {"success": False, "error": "WhatsApp disabled - using email only"}
        
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            result = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=to_phone
            )
            
            logger.info(f"WhatsApp sent to {to_phone}: {result.sid}")
            return {
                "success": True,
                "message_sid": result.sid,
                "message": "WhatsApp message sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp to {to_phone}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_qualification_email(
        self,
        to_email: str,
        first_name: Optional[str],
        questions: list
    ) -> Dict[str, Any]:
        """
        Send qualification questions email to lead.
        
        Args:
            to_email: Lead email address
            first_name: Lead first name
            questions: List of qualification questions
            
        Returns:
            Result dictionary
        """
        greeting = f"Hi {first_name}," if first_name else "Hi there,"
        
        questions_html = "<ul>" + "".join(
            f"<li>{q}</li>" for q in questions
        ) + "</ul>"
        
        subject = "Quick questions about your needs"
        
        body = f"""
{greeting}

Thank you for your interest! To better understand how we can help you, 
could you please answer these quick questions?

{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

Simply reply to this email with your answers.

Best regards,
Sales Team
        """
        
        html_body = f"""
<html>
<body>
    <p>{greeting}</p>
    <p>Thank you for your interest! To better understand how we can help you, 
    could you please answer these quick questions?</p>
    {questions_html}
    <p>Simply reply to this email with your answers.</p>
    <p>Best regards,<br>Sales Team</p>
</body>
</html>
        """
        
        return await self.send_email(to_email, subject, body, html_body)
    
    async def send_demo_scheduled_email(
        self,
        to_email: str,
        first_name: Optional[str],
        meeting_link: str,
        meeting_time: str
    ) -> Dict[str, Any]:
        """
        Send demo scheduled confirmation email.
        
        Args:
            to_email: Lead email address
            first_name: Lead first name
            meeting_link: Calendly or meeting link
            meeting_time: Scheduled meeting time
            
        Returns:
            Result dictionary
        """
        greeting = f"Hi {first_name}," if first_name else "Hi there,"
        
        subject = "Your demo is scheduled!"
        
        body = f"""
{greeting}

Great news! Your demo has been scheduled for {meeting_time}.

Meeting Link: {meeting_link}

We look forward to showing you how our solution can help your business.

Best regards,
Sales Team
        """
        
        html_body = f"""
<html>
<body>
    <p>{greeting}</p>
    <p>Great news! Your demo has been scheduled for <strong>{meeting_time}</strong>.</p>
    <p><a href="{meeting_link}">Join Meeting</a></p>
    <p>We look forward to showing you how our solution can help your business.</p>
    <p>Best regards,<br>Sales Team</p>
</body>
</html>
        """
        
        return await self.send_email(to_email, subject, body, html_body)
    
    async def notify_sales_team(
        self,
        lead_email: str,
        lead_name: str,
        lead_score: float,
        reason: str
    ) -> Dict[str, Any]:
        """
        Notify sales team about a qualified lead.
        
        Args:
            lead_email: Lead email address
            lead_name: Lead name
            lead_score: Lead score
            reason: Qualification reason
            
        Returns:
            Result dictionary
        """
        subject = f"🎯 New Qualified Lead: {lead_name} (Score: {lead_score})"
        
        body = f"""
New qualified lead alert!

Lead: {lead_name}
Email: {lead_email}
Score: {lead_score}/100

Qualification Reason:
{reason}

Action Required: Review and contact this lead ASAP.
        """
        
        html_body = f"""
<html>
<body>
    <h2>🎯 New Qualified Lead Alert!</h2>
    <p><strong>Lead:</strong> {lead_name}<br>
    <strong>Email:</strong> {lead_email}<br>
    <strong>Score:</strong> {lead_score}/100</p>
    <p><strong>Qualification Reason:</strong><br>{reason}</p>
    <p><strong>Action Required:</strong> Review and contact this lead ASAP.</p>
</body>
</html>
        """
        
        # Send to sales team email (configured in settings)
        sales_email = settings.SENDGRID_FROM_EMAIL  # Replace with actual sales team email
        return await self.send_email(sales_email, subject, body, html_body)


# Global communication service instance
communication_service = CommunicationService()
