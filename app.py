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

load_dotenv()
for key, value in st.secrets.items():
    os.environ[str(key)] = str(value)

logging_level = os.environ.get('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.auth.session import init_session, login_user, logout_user
from src.ui.navigation import render_sidebar
from src.ui.task_list import render_active_tasks, render_completed_tasks, render_deleted_tasks
from src.ui.task_form import render_task_form
from src.ui.ai_chat import render_ai_chat

st.set_page_config(
    page_title="Task Management System",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

auth_config = {
    "client_id": st.secrets["GOOGLE_CLIENT_ID"],
    "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
    "redirect_uri": st.secrets["GOOGLE_REDIRECT_URI"],
    "allow_insecure_http": True  # for localhost
}

auth = AIClubGoogleAuth(auth_config)

init_session()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

query_params = st.query_params
def main():
    """Main application entry point."""
    query_params = st.query_params.to_dict()
    
    if "user_info" in st.session_state and st.session_state.user_info:
        if st.session_state.user != st.session_state.user_info:
            login_user(st.session_state.user_info)
        
        render_sidebar()
        
        # Define page functions for navigation
        def active_tasks_page():
            if st.session_state.get('adding_task'):
                render_task_form()
            elif st.session_state.get('editing_task'):
                render_task_form(st.session_state.editing_task)
            else:
                render_active_tasks()
                
        def completed_tasks_page():
            render_completed_tasks()
            
        def deleted_tasks_page():
            render_deleted_tasks()
            
        def ai_assistant_page():
            render_ai_chat()

        def debug_page():
            st.header("Debug Information: Session State")
            # Convert session state to a readable format
            session_items = {}
            for key, value in st.session_state.items():
                # Handle complex objects
                if hasattr(value, '__dict__'):
                    session_items[key] = str(value)
                else:
                    session_items[key] = value
            
            # Display session state as JSON
            st.json(session_items)
        
        # Define pages for navigation
        active_page = st.Page(active_tasks_page, title="Active Tasks", icon="✅", default=True)
        completed_page = st.Page(completed_tasks_page, title="Completed Tasks", icon="✨")
        deleted_page = st.Page(deleted_tasks_page, title="Deleted Tasks", icon="🗑️")
        ai_page = st.Page(ai_assistant_page, title="AI Assistant", icon="🤖")
        debug_page_nav = st.Page(debug_page, title="Debug", icon="🐞")
        
        # Create navigation
        page = st.navigation([active_page, completed_page, deleted_page, ai_page, debug_page_nav])
        
        # Run the selected page
        page.run()
                
        with st.sidebar:
            if st.button("🚪 **Logout**", help="Sign out of your account"):
                st.session_state.user_info = None
                logout_user()
                st.rerun()
    
    elif "code" in query_params and "user_info" not in st.session_state:
        user_info = auth.get_user_info(query_params, st.session_state.get("state"))
        st.session_state.user_info = user_info
        st.query_params.clear()
        st.rerun()
    else:
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

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
