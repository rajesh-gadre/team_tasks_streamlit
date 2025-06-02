"""
Main application module for the User Task Management System.
Integrates all components and handles the application flow.
"""
import os
import logging
import streamlit as st
import uuid
from dotenv import load_dotenv
from aiclub_auth_lib.oauth import AIClubGoogleAuth

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
from src.auth.session import init_session, login_user, logout_user
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

# Set up the auth config
auth_config = {
    "client_id": st.secrets["GOOGLE_CLIENT_ID"],
    "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
    "redirect_uri": st.secrets["GOOGLE_REDIRECT_URI"],
    "allow_insecure_http": True  # for localhost
}

# Initialize the library
auth = AIClubGoogleAuth(auth_config)

# Initialize session state
init_session()
init_navigation()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

query_params = st.query_params

# Main application function
def main():
    """Main application entry point."""
    # Get query parameters
    query_params = st.query_params.to_dict()
    
    # Check authentication status
    if "user_info" in st.session_state and st.session_state.user_info:
        # User is authenticated
        # Store user info in session state for compatibility with existing code
        if st.session_state.user != st.session_state.user_info:
            login_user(st.session_state.user_info)
        
        # Render sidebar
        render_sidebar()
        
        # Create a simple tab-based navigation
        tab1, tab2, tab3, tab4 = st.tabs(["Active Tasks", "Completed Tasks", "Deleted Tasks", "AI Assistant"])
        
        with tab1:
            # Check if adding or editing a task
            if st.session_state.get('adding_task'):
                render_task_form()
            elif st.session_state.get('editing_task'):
                render_task_form(st.session_state.editing_task)
            else:
                render_active_tasks()
        
        with tab2:
            render_completed_tasks()
        
        with tab3:
            render_deleted_tasks()
        
        with tab4:
            render_ai_chat()
                
        # Add logout button to sidebar
        with st.sidebar:
            if st.button("🚪 **Logout**", help="Sign out of your account"):
                st.session_state.user_info = None
                logout_user()
                st.rerun()
    
    elif "code" in query_params and "user_info" not in st.session_state:
        # Process OAuth callback
        user_info = auth.get_user_info(query_params, st.session_state.get("state"))
        st.session_state.user_info = user_info
        st.query_params.clear()
        st.rerun()
    else:
        # User is not authenticated, show login page
        render_login_page()

@st.dialog("Please log in with your Google account")
def render_login_page():
    st.title("Welcome to Task Management System")
    st.write("Please log in to access your tasks.")
    auth_url, state = auth.get_authorization_url()
    st.session_state.state = state
    st.markdown(
        f'''
        <a href="{auth_url}" target="_self">
            <button style="
                background-color: #34a853;
                color: white;
                padding: 0.5em 1em;
                font-size: 1.1em;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <img src="https://developers.google.com/identity/images/g-logo.png" style="height:20px;" />
                Login with Google
            </button>
        </a>
        ''',
        unsafe_allow_html=True
    )

# Run the application
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
