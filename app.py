"""
Main application module for the User Task Management System.
Integrates all components and handles the application flow.
"""

import os
import logging
import streamlit as st
import uuid
from dotenv import load_dotenv
from src.ui.navigation import render_login_page, render_main_page, render_sidebar

load_dotenv()
for key, value in st.secrets.items():
    os.environ[str(key)] = str(value)

AUTH_TYPE = os.environ.get("AUTH_TYPE", "google").lower()
if AUTH_TYPE == "auth0":
    from src.auth.auth0_auth import Auth0Auth
else:
    from aiclub_auth_lib.oauth import AIClubGoogleAuth



logging_level = os.environ.get("LOG_LEVEL", "INFO")
numeric_level = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(
    level=numeric_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from src.auth.session import (
    init_session,
    login_user,
    logout_user as session_logout_user,
)


st.set_page_config(
    page_title="Task Management System",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

if AUTH_TYPE == "auth0":
    auth_config = {
        "domain": st.secrets["AUTH0_DOMAIN"],
        "client_id": st.secrets["AUTH0_CLIENT_ID"],
        "client_secret": st.secrets["AUTH0_CLIENT_SECRET"],
        "redirect_uri": st.secrets["AUTH0_CALLBACK_URL"],
    }
    auth = Auth0Auth(auth_config)

    def perform_logout():
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        logout_url = (
            f"https://{st.secrets['AUTH0_DOMAIN']}/v2/logout"
            f"?client_id={st.secrets['AUTH0_CLIENT_ID']}"
            f"&returnTo={st.secrets['AUTH0_CALLBACK_URL']}"
        )
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={logout_url}">',
            unsafe_allow_html=True,
        )

else:
    auth_config = {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": st.secrets["GOOGLE_REDIRECT_URI"],
        "allow_insecure_http": True,  # for localhost
    }
    auth = AIClubGoogleAuth(auth_config)

    def perform_logout():
        session_logout_user()


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

        render_main_page()

        with st.sidebar:
            if st.button("🚪 **Logout**", help="Sign out of your account"):
                st.session_state.user_info = None
                perform_logout()
                st.rerun()

    elif "code" in query_params and "user_info" not in st.session_state:
        user_info = auth.get_user_info(query_params, st.session_state.get("state"))
        st.session_state.user_info = user_info
        st.query_params.clear()
        st.rerun()
    else:
        render_login_page(auth, AUTH_TYPE)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
