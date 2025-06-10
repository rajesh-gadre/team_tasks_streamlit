import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'src'))

st = ModuleType('streamlit')

class Tab:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

tabs_called = []

def tabs(names):
    tabs_called.append(names)
    return [Tab() for _ in names]

class Spinner:
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc, tb):
        pass

class SessionState(dict):
    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self[name] = value

st.session_state = SessionState({'userId': 'u1', 'user': {'name': 'N', 'email': 'E'}, 'userTZ': 'America/Los_Angeles'})
st.title = lambda *a, **k: None
st.header = lambda *a, **k: None
st.write = lambda *a, **k: None
st.markdown = lambda *a, **k: None
st.selectbox = lambda *a, **k: 'UTC'
st.button = lambda *a, **k: True
st.success = lambda *a, **k: None
st.tabs = tabs
st.spinner = lambda *a, **k: Spinner()
st.rerun = lambda: None
st.code = lambda *a, **k: None
st.error = lambda *a, **k: None
sys.modules['streamlit'] = st

import importlib
import src.ui.settings as settings
importlib.reload(settings)


def test_render_settings(monkeypatch):
    calls = {}
    monkeypatch.setattr(settings, 'get_user_group_service', lambda: SimpleNamespace(get_groups_for_user=lambda uid: [{'groupName': 'G'}]))
    monkeypatch.setattr(settings, 'get_user_service', lambda: SimpleNamespace(update_timezone=lambda uid, tz: calls.setdefault('update', (uid, tz)) or True))
    monkeypatch.setattr(settings, 'render_changelog', lambda: None)
    monkeypatch.setattr(settings, 'render_run_tests', lambda: None)
    tabs_called.clear()
    settings.render_settings()
    assert tabs_called and tabs_called[0] == ['Settings', 'ChangeLog', 'Run Tests']
    assert calls['update'][1] == 'UTC'

