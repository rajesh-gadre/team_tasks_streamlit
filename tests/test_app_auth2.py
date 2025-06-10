import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

st = ModuleType('streamlit')
nav = ModuleType('src.ui.navigation')
nav.render_main_page = lambda: None
nav.render_sidebar = lambda: None
sys.modules['src.ui.navigation'] = nav
db = ModuleType('src.database.firestore')
db.get_client = lambda: None
sys.modules['src.database.firestore'] = db

class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)
    def __setattr__(self, name, value):
        self[name] = value

st.session_state = SessionState({'user': None})
st.secrets = {}
st.set_page_config = lambda *a, **k: None
calls = {}

class Stop(Exception):
    pass
st.button = lambda label, on_click=None: calls.setdefault(label, False)
st.login = lambda *a, **k: calls.setdefault('login', True)
st.logout = lambda *a, **k: calls.setdefault('logout', True)
def _stop():
    calls.setdefault('stop', True)
    raise Stop()
st.stop = _stop
st.user = SimpleNamespace(is_logged_in=False, id=None, email=None, name=None, sub=None, picture=None)

sys.modules['streamlit'] = st

import app_auth2


def test_not_logged_in(monkeypatch):
    calls.clear()
    try:
        app_auth2.main()
    except Stop:
        pass
    assert 'stop' in calls


def test_logged_in(monkeypatch):
    st.user.is_logged_in = True
    st.user.id = '1'
    st.user.sub = '1'
    st.user.email = 'e'
    st.user.name = 'n'
    calls.clear()
    recorded = {}
    monkeypatch.setattr(app_auth2, 'render_sidebar', lambda: recorded.setdefault('sidebar', True))
    monkeypatch.setattr(app_auth2, 'render_main_page', lambda: recorded.setdefault('main', True))
    monkeypatch.setattr(app_auth2, 'login_user', lambda info: recorded.setdefault('user', info))
    app_auth2.main()
    assert recorded['user']['email'] == 'e'
    assert recorded.get('sidebar') and recorded.get('main')
