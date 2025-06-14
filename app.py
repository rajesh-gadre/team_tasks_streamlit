import os
import logging
import streamlit as st
from dotenv import load_dotenv
from src.ui.navigation import render_main_page, render_sidebar
from src.auth.session import init_session, login_user, logout_user as session_logout_user

load_dotenv()

AUTH_TYPE = os.environ.get('AUTH_TYPE', 'google').lower()
logging_level = os.environ.get('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from src.app_config import build_auth_config
st.set_page_config(page_title='Task Management System', page_icon='✅', layout='wide', initial_sidebar_state='expanded')

def create_auth(auth_type: str):
    if auth_type == 'auth0':
        from src.auth.auth0_auth import Auth0Auth
    else:
        from aiclub_auth_lib.oauth import AIClubGoogleAuth
    config = build_auth_config(auth_type)
    if auth_type == 'auth0':
        auth = Auth0Auth(config)

        def perform_logout():
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            logout_url = f"https://{config['domain']}/v2/logout?client_id={config['client_id']}&returnTo={config['redirect_uri']}"
            st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)
    else:
        auth = AIClubGoogleAuth(config)

        def perform_logout():
            session_logout_user()
    return auth, perform_logout

auth, perform_logout = create_auth(AUTH_TYPE)
init_session()

import langsmith
# NOTE: langsmith.init() does not exist in the current version of the langsmith package.
# Langsmith tracing is enabled via environment variables (LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT).
# No explicit initialization is required here.


def main():
    if not st.user.is_logged_in:
        if st.button('Log in'):
            st.login()
        st.stop()
    if st.sidebar.button('Logout'):
        st.logout()
        session_logout_user()
        st.stop()
    user_info = {'id': st.user.sub, 'email': st.user.email, 'name': st.user.name, 'picture': st.user.picture}
    if st.session_state.user != user_info:
        login_user(user_info)
    render_sidebar()
    render_main_page()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f'Application error: {str(e)}')
        st.error(f'An error occurred: {str(e)}')