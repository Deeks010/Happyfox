#!/usr/bin/env python3
"""
Gmail Authentication Manager

This module handles OAuth2 authentication with Gmail API using custom token management.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import imaplib

class GmailAuthManager:
    """Manages Gmail API authentication and service creation."""
    
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.labels'
        ]
        self.credentials_path = 'credentials.json'
        self.token_path = 'token.pickle'
    
    def _load_saved_credentials(self):
        """Load previously saved credentials if they exist."""
        if not os.path.exists(self.token_path):
            return None
            
        with open(self.token_path, 'rb') as token:
            try:
                return pickle.load(token)
            except Exception:
                return None
    
    def _save_credentials(self, credentials):
        """Save credentials for future use."""
        with open(self.token_path, 'wb') as token:
            pickle.dump(credentials, token)
    
    def initialize_gmail_service(self):
        """Initialize and return an authorized Gmail API service instance."""
        credentials = self._load_saved_credentials()
        
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                credentials = flow.run_local_server(port=0)
                
            self._save_credentials(credentials)
        
        return build('gmail', 'v1', credentials=credentials)
    
    def setup_imap_connection(self):
        """Create and return an authenticated IMAP connection."""
        credentials = self._load_saved_credentials()
        if not credentials:
            raise ValueError("No valid credentials found. Please authenticate first.")
        
        # Connect to Gmail's IMAP server
        imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
        
        # Use the OAuth2 token for authentication
        auth_string = f'user={credentials.client_id}\1auth=Bearer {credentials.token}\1\1'
        imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
        
        return imap_conn