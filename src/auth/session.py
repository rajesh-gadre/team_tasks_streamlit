"""
Session management module for the Task Management System.
Handles user session state and authentication status.
"""
import logging
from typing import Dict, Optional, Any

import streamlit as st
from .google_auth import google_auth

# Configure logging
logger = logging.getLogger(__name__)

def init_session():
    """Initialize session state variables if they don't exist."""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'auth_message' not in st.session_state:
        st.session_state.auth_message = ""

def login_user(user_info: Dict[str, Any]):
    """
    Log in a user by storing their information in session state.
    
    Args:
        user_info: User information dictionary
    """
    st.session_state.user = user_info
    st.session_state.is_authenticated = True
    st.session_state.auth_message = f"Logged in as {user_info.get('name', user_info.get('email', 'User'))}"
    logger.info(f"User logged in: {user_info.get('email')}")

def logout_user():
    """Log out the current user by clearing session state."""
    if st.session_state.user:
        logger.info(f"User logged out: {st.session_state.user.get('email')}")
    st.session_state.user = None
    st.session_state.is_authenticated = False
    st.session_state.auth_message = "Logged out"

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user.
    
    Returns:
        User information dictionary or None if not authenticated
    """
    return st.session_state.get('user')

def is_authenticated() -> bool:
    """
    Check if a user is currently authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    return st.session_state.get('is_authenticated', False)

def validate_session():
    """
    Validate the current session by checking the JWT token.
    
    Returns:
        True if session is valid, False otherwise
    """
    user = get_current_user()
    if not user or 'token' not in user:
        return False
    
    # Validate token
    is_valid, user_info = google_auth.validate_token(user['token'])
    if not is_valid:
        logout_user()
        return False
    
    return True

def require_auth():
    """
    Decorator-like function to require authentication for a page.
    Should be called at the beginning of each protected page.
    
    Returns:
        True if authenticated, False otherwise
    """
    init_session()
    
    if not is_authenticated():
        st.warning("Please log in to access this page")
        return False
    
    if not validate_session():
        st.warning("Your session has expired. Please log in again")
        return False
    
    return True
