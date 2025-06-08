import logging
from typing import Dict, Optional, Any
import streamlit as st
from src.users.user_service import get_user_service
logger = logging.getLogger(__name__)

def init_session():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'auth_message' not in st.session_state:
        st.session_state.auth_message = ''

def login_user(user_info: Dict[str, Any]):
    record = get_user_service().login(user_info.get('email'))
    user_info.update(record)
    st.session_state.user = user_info
    st.session_state.userId = record['userId']
    st.session_state.userEmail = record['userEmail']
    st.session_state.userTZ = record['userTZ']
    st.session_state.is_authenticated = True
    st.session_state.auth_message = f"Logged in as {user_info.get('name', user_info.get('email', 'User'))}"
    logger.info(f"User logged in: {user_info.get('email')}")

def logout_user():
    if st.session_state.user:
        logger.info(f"User logged out: {st.session_state.user.get('email')}")
    st.session_state.user = None
    st.session_state.is_authenticated = False
    st.session_state.auth_message = 'Logged out'

def get_current_user() -> Optional[Dict[str, Any]]:
    return st.session_state.get('user')

def is_authenticated() -> bool:
    return st.session_state.get('is_authenticated', False)

def validate_session():
    user = get_current_user()
    if not user:
        return False
    return True

def require_auth():
    init_session()
    if not is_authenticated():
        return False
    if not validate_session():
        return False
    return True
