import os
import logging
import streamlit as st
import uuid
from dotenv import load_dotenv
from src.auth.auth0_auth import Auth0Auth
from src.ai.chat_service import delete_all_chats_one_by_one, get_all_chats
from src.tasks.task_service import get_task_service
from src.ai.prompt_repository import get_prompt_repository
from src.eval.debug_data import get_eval_inputs, get_eval_results
import pandas as pd
load_dotenv()
for key, value in st.secrets.items():
    os.environ[str(key)] = str(value)
logging_level = os.environ.get('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from src.auth.session import init_session, login_user, logout_user
from src.ui.navigation import render_sidebar
from src.ui.task_list import render_active_tasks, render_completed_tasks, render_deleted_tasks
from src.ui.task_form import render_task_form
from src.ui.ai_chat import render_ai_chat
from src.ui.prompt_management import render_prompt_management
from src.ui.summary import render_summary

def logout_user():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    auth0_domain = st.secrets['AUTH0_DOMAIN']
    client_id = st.secrets['AUTH0_CLIENT_ID']
    return_to = st.secrets['AUTH0_CALLBACK_URL']
    logout_url = f'https://{auth0_domain}/v2/logout?client_id={client_id}&returnTo={return_to}'
    st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)
st.set_page_config(page_title='Task Management System', page_icon='✅', layout='wide', initial_sidebar_state='expanded')
auth_config = {'domain': st.secrets['AUTH0_DOMAIN'], 'client_id': st.secrets['AUTH0_CLIENT_ID'], 'client_secret': st.secrets['AUTH0_CLIENT_SECRET'], 'redirect_uri': st.secrets['AUTH0_CALLBACK_URL']}
auth = Auth0Auth(auth_config)
init_session()
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
query_params = st.query_params

def main():
    query_params = st.query_params.to_dict()
    if 'user_info' in st.session_state and st.session_state.user_info:
        if st.session_state.user != st.session_state.user_info:
            login_user(st.session_state.user_info)
        render_sidebar()

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

        def prompt_management_page():
            render_prompt_management()

        def summary_page():
            render_summary()

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

        def debug_page():
            st.header('Debug Information')
            with st.expander('Session State'):
                debug_session_state()
            with st.expander('Session secrets'):
                st.json(st.secrets)
            with st.expander('Environment secrets'):
                env_dict = {k: v for k, v in os.environ.items() if isinstance(v, str)}
                st.json(env_dict)
            with st.expander('AI Chats'):
                df = pd.DataFrame(get_all_chats())
                st.dataframe(df)
            with st.expander('Tasks'):
                task_service = get_task_service()
                tasks = task_service.get_all_tasks()
                task_list = [{'id': task.id, 'userId': task.user_id, 'title': task.title, 'status': task.status, 'description': task.description, 'dueDate': task.due_date.isoformat() if hasattr(task.due_date, 'isoformat') else task.due_date, 'createdAt': task.created_at.isoformat() if hasattr(task.created_at, 'isoformat') else task.created_at, 'updatedAt': task.updated_at.isoformat() if hasattr(task.updated_at, 'isoformat') else task.updated_at, 'notes': task.notes, 'updates_count': len(task.updates) if task.updates else 0} for task in tasks]
                df = pd.DataFrame(task_list)
                st.dataframe(df)
            with st.expander('Prompts'):
                prompt_repository = get_prompt_repository()
                prompts = prompt_repository.get_all_prompts()
                prompt_list = [prompt.to_dict() for prompt in prompts]
                df = pd.DataFrame(prompt_list)
                st.dataframe(df)
            with st.expander('AI Eval Inputs'):
                debug_eval_inputs()
            with st.expander('AI Eval Results'):
                debug_eval_results()
            with st.expander('Delete AI Chats'):
                if st.button('Delete AI Chats'):
                    delete_all_chats()
        active_page = st.Page(active_tasks_page, title='Active Tasks', icon='✅', default=True)
        completed_page = st.Page(completed_tasks_page, title='Completed Tasks', icon='✨')
        deleted_page = st.Page(deleted_tasks_page, title='Deleted Tasks', icon='🗑️')
        ai_page = st.Page(ai_assistant_page, title='AI Assistant', icon='🤖')
        prompt_page = st.Page(prompt_management_page, title='Prompt Management', icon='📝')
        summary_nav = st.Page(summary_page, title='Summary', icon='📋')
        debug_page_nav = st.Page(debug_page, title='Debug', icon='🐞')
        user_pages = [active_page, completed_page, deleted_page, ai_page]
        admin_pages = [prompt_page, summary_nav, debug_page_nav]
        page = st.navigation({'User': user_pages, 'Admin': admin_pages})
        page.run()
        with st.sidebar:
            if st.button('🚪 **Logout**', help='Sign out of your account'):
                logout_user()
                st.stop()
    elif 'code' in query_params and 'user_info' not in st.session_state:
        user_info = auth.get_user_info(query_params, st.session_state.get('state'))
        st.session_state.user_info = user_info
        st.query_params.clear()
        st.rerun()
    else:
        render_login_page()

def render_login_page():
    st.title('Welcome to TASK MANAGEMENT SYSTEM')
    st.write('Please log in to access your tasks.')
    logger.debug('Login page accessed')
    auth_url, state = auth.get_authorization_url()
    st.session_state.state = state
    st.markdown(f'\n        <a href="{auth_url}" target="_blank" rel="noopener noreferrer">\n            <button style="\n                background-color: #eb5424;\n                color: white;\n                padding: 0.5em 1em;\n                font-size: 1.1em;\n                border: none;\n                border-radius: 5px;\n                cursor: pointer;\n            ">\n                Login with Auth0\n            </button>\n        </a>\n        ', unsafe_allow_html=True)
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f'Application error: {str(e)}')
        st.error(f'An error occurred: {str(e)}')
