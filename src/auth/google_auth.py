"""
Google OAuth authentication module for the Task Management System.
Handles user authentication and JWT token management.
"""
import os
import json
import logging
import time
from typing import Dict, Optional, Any, Tuple

import jwt
import streamlit as st
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests

# Configure logging
logger = logging.getLogger(__name__)

class GoogleAuth:
    """Google OAuth authentication handler."""
    
    def __init__(self):
        """Initialize Google OAuth configuration."""
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            logger.error("Google OAuth credentials not found in environment variables")
            raise ValueError("Missing Google OAuth credentials")
        
        # Define OAuth scopes
        self.scopes = [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]
    
    def create_auth_url(self) -> str:
        """
        Create Google OAuth authorization URL.
        
        Returns:
            Authorization URL for Google OAuth
        """
        try:
            # Create OAuth flow
            logger.debug("Creating OAuth flow")
            redirect_uri = self._get_redirect_uri()
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uri": redirect_uri
                    }
                },
                scopes=self.scopes
            )
            logger.debug("OAuth flow created")
            
            # Generate authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            logger.debug("Authorization URL generated")
            
            # Store flow in session state for later use
            st.session_state['oauth_flow'] = flow
            
            return auth_url
        except Exception as e:
            logger.error(f"Error creating auth URL: {str(e)}")
            raise
    
    def exchange_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens.
        
        Args:
            code: Authorization code from Google OAuth
            
        Returns:
            User information dictionary
        """
        try:
            # Get flow from session state
            flow = st.session_state.get('oauth_flow')
            if not flow:
                raise ValueError("OAuth flow not found in session state")
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            
            # Get credentials and ID token
            credentials = flow.credentials
            id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                requests.Request(),
                self.client_id
            )
            
            # Create user info dictionary
            user_info = {
                'id': id_info['sub'],
                'email': id_info['email'],
                'name': id_info.get('name', ''),
                'picture': id_info.get('picture', '')
            }
            
            # Generate JWT token
            token = self.generate_token(user_info)
            user_info['token'] = token
            
            return user_info
        except Exception as e:
            logger.error(f"Error exchanging code: {str(e)}")
            raise
    
    def generate_token(self, user_info: Dict[str, Any]) -> str:
        """
        Generate JWT token for authenticated user.
        
        Args:
            user_info: User information dictionary
            
        Returns:
            JWT token
        """
        try:
            # Create payload with user info and expiration
            payload = {
                'sub': user_info['id'],
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600 * 24  # 24 hours
            }
            
            # Sign token with a secret key
            # In production, use a proper secret key management system
            secret_key = os.environ.get('JWT_SECRET_KEY', 'default-secret-key')
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            
            return token
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate JWT token and extract user information.
        
        Args:
            token: JWT token
            
        Returns:
            Tuple of (is_valid, user_info)
        """
        try:
            # Decode and verify token
            secret_key = os.environ.get('JWT_SECRET_KEY', 'default-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Extract user info from payload
            user_info = {
                'id': payload['sub'],
                'email': payload['email'],
                'name': payload.get('name', '')
            }
            
            return True, user_info
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return False, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return False, None
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False, None
    
    def _get_redirect_uri(self) -> str:
        """
        Get the redirect URI for OAuth flow.
        
        Returns:
            Redirect URI
        """
        # Get redirect URI from environment variable - this MUST match exactly what's in Google OAuth console
        redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
        
        if not redirect_uri:
            # Default to Streamlit's default port if not specified
            port = os.environ.get('PORT', '8501')
            redirect_uri = f'http://localhost:{port}/'
            logger.warning(f"GOOGLE_REDIRECT_URI not set in environment, using default: {redirect_uri}")
        
        logger.info(f"Using redirect URI: {redirect_uri}")
        return redirect_uri

# Create an instance for use in the application
#google_auth = GoogleAuth()
google_auth = None

def get_google_auth():
    global google_auth
    if google_auth is None:
        google_auth = GoogleAuth()
    return google_auth
