import sys
from pathlib import Path
from types import SimpleNamespace, ModuleType
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.modules.setdefault('streamlit', ModuleType('streamlit'))

class Bag(dict):

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value
sys.modules['streamlit'].session_state = Bag()
from src.auth.auth0_auth import Auth0Auth
from src.auth.session import init_session, login_user, logout_user, require_auth

class DummySession:

    def __init__(self):
        self.fetched = None

    def create_authorization_url(self, endpoint):
        return (f'{endpoint}?x', 's1')

    def fetch_token(self, endpoint, code=None, grant_type=None):
        self.fetched = (endpoint, code, grant_type)

    def get(self, endpoint):
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {'email': 'e'})

def test_auth0_flow(monkeypatch):
    monkeypatch.setattr('src.auth.auth0_auth.OAuth2Session', lambda *a, **k: DummySession())
    auth = Auth0Auth({'domain': 'd', 'client_id': 'cid', 'client_secret': 'sec', 'redirect_uri': 'r'})
    url, state = auth.get_authorization_url()
    assert url == 'https://d/authorize?x'
    assert state == 's1'
    info = auth.get_user_info({'code': 'c'}, state)
    assert info['email'] == 'e'
    assert auth.session.fetched == (auth.token_endpoint, 'c', 'authorization_code')

def test_auth0_missing_code(monkeypatch):
    monkeypatch.setattr('src.auth.auth0_auth.OAuth2Session', lambda *a, **k: DummySession())
    auth = Auth0Auth({'domain': 'd', 'client_id': 'cid', 'client_secret': 'sec', 'redirect_uri': 'r'})
    try:
        auth.get_user_info({}, 's')
    except ValueError as e:
        assert 'authorization code' in str(e)

def test_session_login_flow(monkeypatch):
    st = sys.modules['streamlit']
    st.session_state = Bag()
    called = {}

    class Dummy:
        def login(self, email):
            called['email'] = email
            return {'userId': 'u', 'userEmail': email, 'userTZ': 'Z'}

    monkeypatch.setattr('src.auth.session.get_user_service', lambda: Dummy())
    init_session()
    assert require_auth() is False
    login_user({'email': 'e'})
    assert called['email'] == 'e'
    assert require_auth() is True
    logout_user()
    assert require_auth() is False
