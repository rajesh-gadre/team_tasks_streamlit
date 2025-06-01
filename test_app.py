import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from dotenv import load_dotenv
import uuid
from urllib.parse import urlencode

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
print(f"GOOGLE_REDIRECT_URI: {GOOGLE_REDIRECT_URI}")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [GOOGLE_REDIRECT_URI],
    }
}

# Generate a session ID to persist state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("Task Management System")

query_params = st.query_params
if "code" not in query_params:
    st.write("Please log in to access your tasks.")
    flow = Flow.from_client_config(
        CLIENT_CONFIG, scopes=SCOPES, redirect_uri=GOOGLE_REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(prompt="consent")
    st.session_state.state = state

    st.markdown(
        f"[Login with Google]({auth_url})"
    )

else:
    # Callback: user returned with `code` in query params
    state = st.session_state.get("state")
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        state=state,
        redirect_uri=GOOGLE_REDIRECT_URI
    )

    authorization_response = f"{GOOGLE_REDIRECT_URI}?{urlencode(st.query_params)}"
    flow.fetch_token(authorization_response=authorization_response)
    # flow.fetch_token(authorization_response=st.query_params['code'])

    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )

    st.success(f"Logged in as {id_info['email']}")
    st.write("You can now view your tasks here.")