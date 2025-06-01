"""
Navigation module for the Task Management System.
Handles navigation components and state management.
"""
import streamlit as st
from enum import Enum

class Page(str, Enum):
    """Enum for application pages."""
    ACTIVE = "Active Tasks"
    COMPLETED = "Completed Tasks"
    DELETED = "Deleted Tasks"
    AI = "AI Assistant"
    LOGIN = "Login"

def init_navigation():
    """Initialize navigation state in session state."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = Page.ACTIVE

def set_page(page: Page):
    """
    Set the current page in session state.
    
    Args:
        page: Page to navigate to
    """
    st.session_state.current_page = page

def get_current_page() -> Page:
    """
    Get the current page from session state.
    
    Returns:
        Current page
    """
    return st.session_state.get('current_page', Page.ACTIVE)

def render_navigation():
    """Render navigation tabs."""
    # Create tabs for navigation
    tabs = st.tabs([
        Page.ACTIVE,
        Page.COMPLETED,
        Page.DELETED,
        Page.AI
    ])
    
    # Return tabs for use in main app
    return tabs

def render_sidebar():
    """Render sidebar with user info and logout button."""
    with st.sidebar:
        st.title("Task Management")
        
        # Show user info if authenticated
        if st.session_state.get('is_authenticated', False):
            user = st.session_state.get('user', {})
            
            # Display user info
            st.write(f"Logged in as: {user.get('name', user.get('email', 'User'))}")
            
            if user.get('picture'):
                st.image(user['picture'], width=100)
            
            # Logout button
            if st.button("Logout",key="logout_button"):
                from src.auth.session import logout_user
                logout_user()
                st.rerun()
        else:
            st.write("Please log in to access your tasks.")
            
            # Login button
            if st.button("Login with Google",key="login_button_with_google_navigation"):
                st.session_state.current_page = Page.LOGIN
                st.rerun()
