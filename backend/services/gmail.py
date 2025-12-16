"""
Gmail service for reading and processing sales lead emails.
"""
import os
import base64
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from email.mime.text import MIMEText
import pickle
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import settings
import logging

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailService:
    """Service for reading emails from Gmail."""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.flow = None
        
    def get_authorization_url(self) -> Optional[str]:
        """
        Get the OAuth authorization URL for web application flow.
        
        Returns:
            Authorization URL string or None if error
        """
        try:
            if not os.path.exists(settings.GMAIL_CREDENTIALS_FILE):
                logger.error(f"Gmail credentials file not found: {settings.GMAIL_CREDENTIALS_FILE}")
                return None
            
            self.flow = Flow.from_client_secrets_file(
                settings.GMAIL_CREDENTIALS_FILE,
                scopes=SCOPES,
                redirect_uri=settings.GMAIL_REDIRECT_URI
            )
            
            authorization_url, state = self.flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Save state for verification
            with open('gmail_oauth_state.json', 'w') as f:
                json.dump({'state': state}, f)
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {str(e)}")
            return None
    
    def handle_oauth_callback(self, code: str, state: str) -> bool:
        """
        Handle OAuth callback and exchange code for tokens.
        
        Args:
            code: Authorization code from callback
            state: State parameter for verification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify state
            if os.path.exists('gmail_oauth_state.json'):
                with open('gmail_oauth_state.json', 'r') as f:
                    saved_state = json.load(f).get('state')
                    if saved_state != state:
                        logger.error("State mismatch in OAuth callback")
                        return False
            
            # Exchange code for credentials
            self.flow = Flow.from_client_secrets_file(
                settings.GMAIL_CREDENTIALS_FILE,
                scopes=SCOPES,
                redirect_uri=settings.GMAIL_REDIRECT_URI
            )
            self.flow.fetch_token(code=code)
            self.credentials = self.flow.credentials
            
            # Save credentials
            with open(settings.GMAIL_TOKEN_FILE, 'wb') as token:
                pickle.dump(self.credentials, token)
            
            # Build service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Gmail OAuth callback handled successfully")
            
            # Cleanup state file
            if os.path.exists('gmail_oauth_state.json'):
                os.remove('gmail_oauth_state.json')
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {str(e)}")
            return False
        
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using saved token.
        
        Returns:
            True if authentication successful, False if needs authorization
        """
        try:
            # Check if token file exists
            if os.path.exists(settings.GMAIL_TOKEN_FILE):
                with open(settings.GMAIL_TOKEN_FILE, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If credentials don't exist, need authorization
            if not self.credentials:
                logger.info("No credentials found - authorization required")
                return False
            
            # If credentials are expired, refresh them
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                # Save refreshed credentials
                with open(settings.GMAIL_TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Gmail authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {str(e)}")
            return False
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch unread emails matching the search criteria.
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries with parsed content
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Search for emails matching criteria
            results = self.service.users().messages().list(
                userId='me',
                q=settings.GMAIL_SEARCH_QUERY,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No unread sales emails found")
                return []
            
            logger.info(f"Found {len(messages)} unread sales emails")
            
            # Fetch full details for each message
            emails = []
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            logger.error(f"Error fetching emails: {error}")
            return []
    
    def _get_email_details(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific email.
        
        Args:
            msg_id: Gmail message ID
            
        Returns:
            Dictionary with email details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            # Extract key information from headers
            subject = self._get_header(headers, 'Subject')
            sender = self._get_header(headers, 'From')
            date = self._get_header(headers, 'Date')
            to = self._get_header(headers, 'To')
            
            # Parse email body
            body = self._get_email_body(message['payload'])
            
            # Parse sender information
            sender_email, sender_name = self._parse_sender(sender)
            
            return {
                'id': msg_id,
                'subject': subject,
                'from': sender,
                'sender_email': sender_email,
                'sender_name': sender_name,
                'to': to,
                'date': date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'thread_id': message.get('threadId')
            }
            
        except HttpError as error:
            logger.error(f"Error fetching email details for {msg_id}: {error}")
            return None
    
    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract header value by name."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _get_email_body(self, payload: Dict) -> str:
        """
        Extract email body from message payload.
        
        Args:
            payload: Email payload from Gmail API
            
        Returns:
            Decoded email body text
        """
        body = ''
        
        if 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        
        return body
    
    def _parse_sender(self, sender: str) -> tuple[str, str]:
        """
        Parse sender string to extract email and name.
        
        Args:
            sender: Full sender string (e.g., "John Doe <john@example.com>")
            
        Returns:
            Tuple of (email, name)
        """
        email_match = re.search(r'<(.+?)>', sender)
        if email_match:
            email = email_match.group(1)
            name = sender.split('<')[0].strip().strip('"')
        else:
            email = sender
            name = sender.split('@')[0]
        
        return email, name
    
    def mark_as_read(self, msg_id: str) -> bool:
        """
        Mark an email as read.
        
        Args:
            msg_id: Gmail message ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Marked email {msg_id} as read")
            return True
        except HttpError as error:
            logger.error(f"Error marking email as read: {error}")
            return False
    
    def extract_lead_info(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract lead information from email content using pattern matching and AI.
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            Dictionary with extracted lead information
        """
        body = email_data.get('body', '')
        subject = email_data.get('subject', '')
        
        # Basic extraction
        lead_info = {
            'email': email_data.get('sender_email'),
            'full_name': email_data.get('sender_name'),
            'source': 'Gmail',
            'notes': f"Email Subject: {subject}\n\n{body[:500]}",  # First 500 chars
        }
        
        # Extract company from email domain (basic)
        email = email_data.get('sender_email', '')
        if email and '@' in email:
            domain = email.split('@')[1]
            if domain not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                lead_info['company'] = domain.split('.')[0].title()
        
        # Extract phone number if present
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b'
        phone_match = re.search(phone_pattern, body)
        if phone_match:
            lead_info['phone'] = phone_match.group(0)
        
        # Extract company name from signature or body
        company_patterns = [
            r'(?:from|at|with)\s+([A-Z][A-Za-z\s&]+(?:Inc|LLC|Ltd|Corp|Corporation))',
            r'([A-Z][A-Za-z\s&]+(?:Inc|LLC|Ltd|Corp|Corporation))',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, body)
            if match and 'company' not in lead_info:
                lead_info['company'] = match.group(1).strip()
                break
        
        return lead_info


# Global instance
gmail_service = GmailService()
