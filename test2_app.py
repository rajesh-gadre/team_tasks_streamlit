# app.py
import streamlit as st
from dotenv import load_dotenv
import os
import uuid
from aiclub_auth_lib.oauth import AIClubGoogleAuth
from urllib.parse import urlencode

load_dotenv()

# Set up the auth config
auth_config = {
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
    "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
    "allow_insecure_http": True  # for localhost
}

# Initialize the library
auth = AIClubGoogleAuth(auth_config)


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

query_params = st.query_params

@st.dialog("Please log in with your Google account")
def login_dialog():
    #st.write("Please log in to continue.")
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

if "user_info" in st.session_state and st.session_state.user_info:
    st.title("My Reusable Google OAuth App")
    st.success(f"Logged in as {st.session_state.user_info['email']}")
    st.json(st.session_state.user_info)
    if st.button("🚪 **Logout**", help="Sign out of your account"):
        st.session_state.user_info = None
        st.rerun()

elif "code" in query_params and "user_info" not in st.session_state:
    user_info = auth.get_user_info(query_params, st.session_state.get("state"))
    st.session_state.user_info = user_info
    st.query_params.clear()
    st.rerun()

else:
    login_dialog()