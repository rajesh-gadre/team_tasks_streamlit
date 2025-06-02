"""
Session management module for the Task Management System.
Handles user session state and authentication status.
"""
import logging
from typing import Dict, Optional, Any

import streamlit as st

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
    Validate the current session.
    
    Returns:
        True if session is valid, False otherwise
    """
    # We now rely on the aiclub_auth_lib to handle token validation
    # Just check if user exists in session state
    user = get_current_user()
    if not user:
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
    
    # This function is kept for backward compatibility but is no longer used
    # in the main flow. Authentication is now handled directly in app.py
    # using the aiclub_auth_lib
    
    if not is_authenticated():
        return False
    
    if not validate_session():
        return False
    
    return True
