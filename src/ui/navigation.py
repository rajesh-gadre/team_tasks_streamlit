"""
Navigation module for the Task Management System.
Handles navigation components and state management.
"""
import streamlit as st
from enum import Enum
import logging
import pandas as pd

from src.ui.task_list import (
    render_active_tasks,
    render_completed_tasks,
    render_deleted_tasks,
)

from src.ui.task_form import render_task_form
from src.ui.ai_chat import render_ai_chat
from src.ui.prompt_management import render_prompt_management
from src.ui.summary import render_summary
from src.ui.changelog import render_changelog

from src.ai.chat_service import delete_all_chats_one_by_one, get_all_chats
from src.tasks.task_service import get_task_service
from src.ai.prompt_repository import get_prompt_repository
from src.eval.debug_data import get_eval_inputs, get_eval_results

logger = logging.getLogger(__name__)

class Page(str, Enum):
    """Enum for application pages."""
    ACTIVE = "Active Tasks"
    COMPLETED = "Completed Tasks"
    DELETED = "Deleted Tasks"
    AI = "AI Assistant"
    LOGIN = "Login"


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


# WAS @st.dialog("Please log in with your Google account")
def render_login_page(auth, AUTH_TYPE):
    st.title("Welcome to TASK MANAGEMENT SYSTEM")
    st.write("Please log in to access your tasks.")
    logger.debug("Login page accessed")
    auth_url, state = auth.get_authorization_url()
    st.session_state.state = state
    if AUTH_TYPE == "auth0":
        st.markdown(
            f"""
            <a href="{auth_url}" target="_blank" rel="noopener noreferrer">
                <button style="
                    background-color: #eb5424;
                    color: white;
                    padding: 0.5em 1em;
                    font-size: 1.1em;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                ">
                    Login with Auth0
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <a href="{auth_url}" target="_blank" rel="noopener noreferrer">
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
            """,
            unsafe_allow_html=True,
        )


def render_sidebar():
    """Render sidebar with user info and logout button."""
    with st.sidebar:
        st.title("TASK MANAGEMENT")
        
        # Show user info if authenticated
        if st.session_state.get('is_authenticated', False):
            user = st.session_state.get('user', {})
            
            # Display user info
            st.write(f"Logged in as: {user.get('name', user.get('email', 'User'))}")
            
            if user.get('picture'):
                st.image(user['picture'], width=100)
            
            # Refresh button
            if st.button("🔄 Refresh Page", key="refresh_page_button"):
                st.rerun()
            
        else:
            st.write("Please log in to access your tasks.")
            
            # Login button
            if st.button("Login with Google", key="login_button_with_google_navigation"):
                st.session_state.current_page = Page.LOGIN
                st.rerun()

# Define page functions for navigation
def active_tasks_page():
    if st.session_state.get("adding_task"):
        render_task_form()
    elif st.session_state.get("editing_task"):
        render_task_form(st.session_state.editing_task)
    else:
        render_active_tasks()

def completed_tasks_page():
    render_completed_tasks()

def deleted_tasks_page():
    render_deleted_tasks()

def ai_assistant_page():
    render_ai_chat()

def prompt_management_page():
    render_prompt_management()

def summary_page():
    render_summary()

def changelog_page():
    render_changelog()

def eval_candidates_page():
    from src.ui.eval_candidates import render_eval_candidates
    render_eval_candidates()

def run_evals_page():
    from src.ui.run_evals import render_run_evals
    render_run_evals()

def debug_session_state():
    session_items = {}
    for key, value in st.session_state.items():
        # Handle complex objects
        if hasattr(value, "__dict__"):
            session_items[key] = str(value)
        else:
            session_items[key] = value

    # Display session state as JSON
    st.json(session_items)

def debug_eval_inputs():
    df = pd.DataFrame(get_eval_inputs())
    st.dataframe(df)

def debug_eval_results():
    df = pd.DataFrame(get_eval_results())
    st.dataframe(df)

def debug_page():
    st.header("Debug Information")
    with st.expander("Session State"):
        debug_session_state()
    with st.expander("AI Chats"):
        df = pd.DataFrame(get_all_chats())
        st.dataframe(df)
    with st.expander("Tasks"):
        task_service = get_task_service()
        tasks = task_service.get_all_tasks()
        # Convert tasks to a simplified dict format that can be displayed in a dataframe
        task_list = [
            {
                "id": task.id,
                "userId": task.user_id,
                "title": task.title,
                "status": task.status,
                "description": task.description,
                "dueDate": (
                    task.due_date.isoformat()
                    if hasattr(task.due_date, "isoformat")
                    else task.due_date
                ),
                "createdAt": (
                    task.created_at.isoformat()
                    if hasattr(task.created_at, "isoformat")
                    else task.created_at
                ),
                "updatedAt": (
                    task.updated_at.isoformat()
                    if hasattr(task.updated_at, "isoformat")
                    else task.updated_at
                ),
                "notes": task.notes,
                "updates_count": len(task.updates) if task.updates else 0,
            }
            for task in tasks
        ]
        df = pd.DataFrame(task_list)
        st.dataframe(df)
    with st.expander("Prompts"):
        prompt_repository = get_prompt_repository()
        # Display all prompts rather than just the latest versions
        prompts = prompt_repository.get_all_prompts()
        prompt_list = [prompt.to_dict() for prompt in prompts]
        df = pd.DataFrame(prompt_list)
        st.dataframe(df)
    with st.expander("AI Eval Inputs"):
        debug_eval_inputs()
    with st.expander("AI Eval Results"):
        debug_eval_results()
    with st.expander("Delete AI Chats"):
        delete_count = st.number_input(
            "Delete count", min_value=1, max_value=100, value=1
        )
        if st.button("Delete AI Chats one-by-one"):
            delete_all_chats_one_by_one(delete_count)

def render_main_page():
    # Define pages for navigation
    active_page = st.Page(
        active_tasks_page, title="Active Tasks", icon="✅", default=True
    )
    completed_page = st.Page(
        completed_tasks_page, title="Completed Tasks", icon="✨"
    )
    deleted_page = st.Page(deleted_tasks_page, title="Deleted Tasks", icon="🗑️")
    ai_page = st.Page(ai_assistant_page, title="AI Assistant", icon="🤖")
    prompt_page = st.Page(
        prompt_management_page, title="Prompt Management", icon="📝"
    )
    summary_nav = st.Page(summary_page, title="Summary", icon="📋")
    changelog_nav = st.Page(changelog_page, title="ChangeLog", icon="📜")
    eval_candidates_nav = st.Page(
        eval_candidates_page, title="Eval Candidates", icon="🧪"
    )
    run_evals_nav = st.Page(
        run_evals_page, title="Run Evals", icon="⚙️"
    )
    debug_page_nav = st.Page(debug_page, title="Debug", icon="🐞")

    user_pages = [ai_page, active_page, completed_page, deleted_page]

    navigation_pages = [summary_nav, changelog_nav]
    admin_pages = [prompt_page, eval_candidates_nav, run_evals_nav, debug_page_nav]

    page = st.navigation({
        "============= 🧑‍💼 User": user_pages, 
        "============= 🧭 Nav" : navigation_pages,
        "============= 🛠️ Admin": admin_pages,
        })

    # Run the selected page
    page.run()
