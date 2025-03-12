#!/usr/bin/env python3
"""
Email Handler Module

Handles email fetching and processing operations using Gmail API.
"""

import base64
import email
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Dict, Optional
from googleapiclient.discovery import Resource

class EmailHandler:
    """Manages email operations using Gmail API."""
    
    def __init__(self, service: Resource):
        self.service = service
    
    def fetch_recent_emails(self, max_results: int = 25) -> List[Dict]:
        """Fetch recent emails from Gmail."""
        try:
            # Get messages from Gmail API
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract email details
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
                recipient = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
                date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                
                # Parse email body
                body = self._extract_email_body(msg_data['payload'])
                
                # Create email object
                email_obj = {
                    'message_id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'recipient': recipient,
                    'received_date': self._parse_date(date_str),
                    'content': body,
                    'is_read': 'UNREAD' not in msg_data['labelIds'],
                    'labels': msg_data['labelIds']
                }
                
                emails.append(email_obj)
            
            return emails
        
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode()
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode()
        
        return ''
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime object."""
        try:
            # Try various date formats
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%d %b %Y %H:%M:%S %z']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Fallback to current datetime if parsing fails
            return datetime.now()
        except Exception:
            return datetime.now()
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read."""
        try:
            # Modify the message labels
            result = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            # Verify the operation by checking if UNREAD label is removed
            current_labels = result.get('labelIds', [])
            if 'UNREAD' not in current_labels:
                print(f"Successfully marked message {message_id} as read")
                return True
            else:
                print(f"Failed to mark message {message_id} as read - UNREAD label still present")
                return False
        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False
    
    def apply_label(self, message_id: str, label_name: str) -> bool:
        """Apply a label to an email."""
        try:
            # Get or create label
            label_id = self._get_or_create_label(label_name)
            if not label_id:
                return False
            
            # Apply label to message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return True
        except Exception as e:
            print(f"Error applying label: {e}")
            return False
    
    def _get_or_create_label(self, label_name: str) -> Optional[str]:
        """Get or create a Gmail label."""
        try:
            # List all labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Check if label exists
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
            
            # Create new label
            label = self.service.users().labels().create(
                userId='me',
                body={
                    'name': label_name,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
            ).execute()
            
            return label['id']
        except Exception as e:
            print(f"Error managing label: {e}")
            return None
    
    def move_to_folder(self, message_id: str, folder: str) -> bool:
        """Move an email to a specified folder."""
        try:
            # Map folder names to Gmail label IDs
            folder_mapping = {
                'inbox': 'INBOX',
                'spam': 'SPAM',
                'trash': 'TRASH',
                'archive': None  # Removing INBOX label effectively archives the message
            }
            
            if folder.lower() not in folder_mapping:
                return False
            
            # Remove current labels
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX', 'SPAM', 'TRASH']}
            ).execute()
            
            # Add new label if not archiving
            if folder_mapping[folder.lower()]:
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'addLabelIds': [folder_mapping[folder.lower()]]}
                ).execute()
            
            return True
        except Exception as e:
            print(f"Error moving message: {e}")
            return False