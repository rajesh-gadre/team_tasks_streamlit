import os
import logging
import streamlit as st
from dotenv import load_dotenv
from src.ui.navigation import render_main_page, render_sidebar
from src.auth.session import init_session, login_user, logout_user as session_logout_user

load_dotenv()
for key, value in st.secrets.items():
    os.environ[str(key)] = str(value)
logging_level = os.environ.get('LOG_LEVEL', 'INFO')
numeric_level = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
st.set_page_config(page_title='Task Management System', page_icon='✅', layout='wide', initial_sidebar_state='expanded')
init_session()


def main():
    if not st.user.is_logged_in:
        if st.button('Log in'):
            st.login()
        st.stop()
    if st.button('Logout'):
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