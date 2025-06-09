import streamlit as st
from enum import Enum
import logging
import pandas as pd
from src.ui.tasks_page import render_tasks_page
from src.ui.ai_chat import render_ai_chat
from src.ui.prompt_management import render_prompt_management
from src.ui.group_management import render_group_management
from src.ui.settings import render_settings
from src.ui.summary import render_summary
from src.ui.changelog import render_changelog
from src.ai.chat_service import delete_all_chats_one_by_one, get_all_chats
from src.tasks.task_service import get_task_service
from src.ai.prompt_repository import get_prompt_repository
from src.eval.debug_data import get_eval_inputs, get_eval_results
from src.ui.run_tests import render_run_tests
from src.database.firestore import get_client
logger = logging.getLogger(__name__)

class Page(str, Enum):
    TASKS = 'Tasks'
    AI = 'AI Assistant'
    LOGIN = 'Login'

def set_page(page: Page):
    st.session_state.current_page = page

def get_current_page() -> Page:
    return st.session_state.get('current_page', Page.TASKS)

def render_login_page(auth, AUTH_TYPE):
    st.title('Welcome to TASK MANAGEMENT SYSTEM')
    st.write('Please log in to access your tasks.')
    logger.debug('Login page accessed')
    auth_url, state = auth.get_authorization_url()
    st.session_state.state = state
    if AUTH_TYPE == 'auth0':
        st.markdown(f'\n            <a href="{auth_url}" target="_blank" rel="noopener noreferrer">\n                <button style="\n                    background-color: #eb5424;\n                    color: white;\n                    padding: 0.5em 1em;\n                    font-size: 1.1em;\n                    border: none;\n                    border-radius: 5px;\n                    cursor: pointer;\n                ">\n                    Login with Auth0\n                </button>\n            </a>\n            ', unsafe_allow_html=True)
    else:
        st.markdown(f'\n            <a href="{auth_url}" target="_blank" rel="noopener noreferrer">\n                <button style="\n                    background-color: #34a853;\n                    color: white;\n                    padding: 0.5em 1em;\n                    font-size: 1.1em;\n                    border: none;\n                    border-radius: 5px;\n                    cursor: pointer;\n                    display: flex;\n                    align-items: center;\n                    gap: 10px;\n                ">\n                    <img src="https://developers.google.com/identity/images/g-logo.png" style="height:20px;" />\n                    Login with Google\n                </button>\n            </a>\n            ', unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.title('TASK MANAGEMENT')
        if st.session_state.get('is_authenticated', False):
            user = st.session_state.get('user', {})
            st.write(f"Logged in as: {user.get('name', user.get('email', 'User'))}")
            if user.get('picture'):
                st.image(user['picture'], width=100)
            if st.button('🔄 Refresh Page', key='refresh_page_button'):
                st.rerun()
        else:
            st.write('Please log in to access your tasks.')
            if st.button('Login with Google', key='login_button_with_google_navigation'):
                st.session_state.current_page = Page.LOGIN
                st.rerun()



def ai_assistant_page():
    render_ai_chat()

def prompt_management_page():
    render_prompt_management()

def group_management_page():
    render_group_management()

def settings_page():
    render_settings()

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

def run_tests_page():
    render_run_tests()

def tasks_page():
    render_tasks_page()

def debug_session_state():
    session_items = {}
    for key, value in st.session_state.items():
        if hasattr(value, '__dict__'):
            session_items[key] = str(value)
        else:
            session_items[key] = value
    st.json(session_items)

def debug_eval_inputs():
    df = pd.DataFrame(get_eval_inputs())
    st.dataframe(df)

def debug_eval_results():
    df = pd.DataFrame(get_eval_results())
    st.dataframe(df)

def _debug_session_state_tab():
    debug_session_state()

def _debug_ai_chats_tab():
    df = pd.DataFrame(get_all_chats())
    st.dataframe(df)

def _debug_tasks_tab():
    task_service = get_task_service()
    tasks = task_service.get_all_tasks()
    task_list = [{'id': task.id, 'userId': task.user_id, 'title': task.title, 'status': task.status, 'description': task.description, 'dueDate': task.due_date.isoformat() if hasattr(task.due_date, 'isoformat') else task.due_date, 'createdAt': task.created_at.isoformat() if hasattr(task.created_at, 'isoformat') else task.created_at, 'updatedAt': task.updated_at.isoformat() if hasattr(task.updated_at, 'isoformat') else task.updated_at, 'notes': task.notes, 'updates_count': len(task.updates) if task.updates else 0} for task in tasks]
    df = pd.DataFrame(task_list)
    st.dataframe(df)

def _debug_prompts_tab():
    prompt_repository = get_prompt_repository()
    prompts = prompt_repository.get_all_prompts()
    prompt_list = [prompt.to_dict() for prompt in prompts]
    df = pd.DataFrame(prompt_list)
    st.dataframe(df)

def _debug_eval_inputs_tab():
    debug_eval_inputs()

def _debug_eval_results_tab():
    debug_eval_results()

def _delete_ai_chats_tab():
    delete_count = st.number_input('Delete count', min_value=1, max_value=100, value=1)
    confirm = st.checkbox('Confirm deletion')
    if st.button('Delete AI Chats one-by-one') and confirm:
        delete_all_chats_one_by_one(delete_count)

def _debug_user_tables_tab():
    client = get_client()
    users_df = pd.DataFrame(client.get_all('users'))
    st.dataframe(users_df)
    roles_df = pd.DataFrame(client.get_all('user_roles'))
    st.dataframe(roles_df)

def debug_page():
    st.header('Debug Information')
    tabs = st.tabs(['Session State', 'AI Chats', 'Tasks', 'Prompts', 'AI Eval Inputs', 'AI Eval Results', 'Users and Roles', 'Delete AI Chats'])
    with tabs[0]:
        _debug_session_state_tab()
    with tabs[1]:
        _debug_ai_chats_tab()
    with tabs[2]:
        _debug_tasks_tab()
    with tabs[3]:
        _debug_prompts_tab()
    with tabs[4]:
        _debug_eval_inputs_tab()
    with tabs[5]:
        _debug_eval_results_tab()
    with tabs[6]:
        _debug_user_tables_tab()
    with tabs[7]:
        _delete_ai_chats_tab()

def render_main_page():
    tasks_nav = st.Page(tasks_page, title='Tasks', icon='✅', default=True)
    ai_page = st.Page(ai_assistant_page, title='AI Assistant', icon='🤖')
    prompt_page = st.Page(prompt_management_page, title='Prompt Management', icon='📝')
    group_page = st.Page(group_management_page, title='Group Management', icon='👥')
    settings_nav = st.Page(settings_page, title='Settings', icon='⚙️')
    summary_nav = st.Page(summary_page, title='Summary', icon='📋')
    changelog_nav = st.Page(changelog_page, title='ChangeLog', icon='📜')
    run_tests_nav = st.Page(run_tests_page, title='Run Tests', icon='🧪')
    eval_candidates_nav = st.Page(eval_candidates_page, title='Eval Candidates', icon='🧪')
    run_evals_nav = st.Page(run_evals_page, title='Run Evals', icon='⚙️')
    debug_page_nav = st.Page(debug_page, title='Debug', icon='🐞')

    ai_pages = [ai_page]
    user_pages = [tasks_nav]
    navigation_pages = [settings_nav, summary_nav, changelog_nav, run_tests_nav]
    admin_pages = [prompt_page, group_page, eval_candidates_nav, run_evals_nav, debug_page_nav]
    page = st.navigation({'============= 🧑\u200d💼 AI': ai_pages,'============= 🧑\u200d💼 User': user_pages, '============= 🧭 Nav': navigation_pages, '============= 🛠️ Admin': admin_pages})
    page.run()
