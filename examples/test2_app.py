import streamlit as st
from dotenv import load_dotenv
import os
import uuid
from aiclub_auth_lib.oauth import AIClubGoogleAuth
from urllib.parse import urlencode
load_dotenv()
auth_config = {'client_id': os.getenv('GOOGLE_CLIENT_ID'), 'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'), 'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'), 'allow_insecure_http': True}
auth = AIClubGoogleAuth(auth_config)
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
query_params = st.query_params

@st.dialog('Please log in with your Google account')
def login_dialog():
    auth_url, state = auth.get_authorization_url()
    st.session_state.state = state
    st.markdown(f'\n        <a href="{auth_url}" target="_self">\n            <button style="\n                background-color: #34a853;\n                color: white;\n                padding: 0.5em 1em;\n                font-size: 1.1em;\n                border: none;\n                border-radius: 5px;\n                cursor: pointer;\n                display: flex;\n                align-items: center;\n                gap: 10px;\n            ">\n                <img src="https://developers.google.com/identity/images/g-logo.png" style="height:20px;" />\n                Login with Google\n            </button>\n        </a>\n        ', unsafe_allow_html=True)
if 'user_info' in st.session_state and st.session_state.user_info:
    st.title('My Reusable Google OAuth App')
    st.success(f"Logged in as {st.session_state.user_info['email']}")
    st.json(st.session_state.user_info)
    if st.button('🚪 **Logout**', help='Sign out of your account'):
        st.session_state.user_info = None
        st.rerun()
elif 'code' in query_params and 'user_info' not in st.session_state:
    user_info = auth.get_user_info(query_params, st.session_state.get('state'))
    st.session_state.user_info = user_info
    st.query_params.clear()
    st.rerun()
else:
    login_dialog()