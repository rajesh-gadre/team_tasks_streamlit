"""
Main application module for the User Task Management System.
Integrates all components and handles the application flow.
"""
import os
import logging
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging_level = os.environ.get('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import application modules
from src.auth.session import init_session, require_auth, login_user, logout_user
from src.auth.google_auth import google_auth
from src.ui.navigation import init_navigation, render_navigation, render_sidebar, Page, get_current_page, set_page
from src.ui.task_list import render_active_tasks, render_completed_tasks, render_deleted_tasks
from src.ui.task_form import render_task_form
from src.ui.ai_chat import render_ai_chat

# Set page configuration
st.set_page_config(
    page_title="Task Management System",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session()
init_navigation()

# Main application function
def main():
    """Main application entry point."""
    # Render sidebar
    render_sidebar()
    
    # Handle authentication
    if not require_auth():
        render_login_page()
        return
    
    # Get current page
    current_page = get_current_page()
    
    # Render navigation tabs
    tabs = render_navigation()
    
    # Handle tab selection
    if tabs[0].selectbox("", [""], key="active_tab"):
        set_page(Page.ACTIVE)
        st.rerun()
    elif tabs[1].selectbox("", [""], key="completed_tab"):
        set_page(Page.COMPLETED)
        st.rerun()
    elif tabs[2].selectbox("", [""], key="deleted_tab"):
        set_page(Page.DELETED)
        st.rerun()
    elif tabs[3].selectbox("", [""], key="ai_tab"):
        set_page(Page.AI)
        st.rerun()
    
    # Render content based on current page
    if current_page == Page.ACTIVE:
        with tabs[0]:
            # Check if adding or editing a task
            if st.session_state.get('adding_task'):
                render_task_form()
            elif st.session_state.get('editing_task'):
                render_task_form(st.session_state.editing_task)
            else:
                render_active_tasks()
    
    elif current_page == Page.COMPLETED:
        with tabs[1]:
            render_completed_tasks()
    
    elif current_page == Page.DELETED:
        with tabs[2]:
            render_deleted_tasks()
    
    elif current_page == Page.AI:
        with tabs[3]:
            render_ai_chat()

def render_login_page():
    """Render the login page."""
    st.title("Welcome to Task Management System")
    st.write("Please log in to access your tasks.")
    
    # Google OAuth login
    if st.button("Login with Google",key="login_button_with_google"):
        try:
            # Create authorization URL
            auth_url = google_auth.create_auth_url()
            
            # Redirect to Google OAuth
            st.markdown(f'<a href="{auth_url}" target="_self">Click here to login with Google</a>', unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Error creating auth URL: {str(e)}")
            st.error(f"Error setting up authentication: {str(e)}")
    
    # Handle OAuth callback
    if 'code' in st.query_params:
        try:
            # Exchange code for tokens
            code = st.query_params['code']
            logger.info(f"Received OAuth code, attempting to exchange for tokens")
            user_info = google_auth.exchange_code(code)
            
            # Log in user
            login_user(user_info)
            
            # Clear query parameters
            st.query_params.clear()
            
            # Rerun to update UI
            st.rerun()
        except Exception as e:
            logger.error(f"Error processing OAuth callback: {str(e)}")
            st.error(f"Error logging in: {str(e)}")

# Run the application
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
